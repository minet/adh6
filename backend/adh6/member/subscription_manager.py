import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from adh6 import mail
from adh6.config.configuration import settings
from adh6.constants import (
    DURATION_STRING,
    PRICES,
    MembershipStatus,
)
from adh6.context import get_api_key_id, get_user
from adh6.decorator import log_call
from adh6.entity import (
    AbstractMembership,
    AbstractTransaction,
    Member,
    Membership,
    SubscriptionBody,
)
from adh6.exceptions import (
    CharterNotSigned,
    MemberNotFoundError,
    MembershipAlreadyExist,
    MembershipNotFoundError,
    MembershipStatusNotAllowed,
    NoPriceAssignedToThatDuration,
    PaymentMethodNotFoundError,
    UnknownPaymentMethod,
    WifiOnlyRestrictionError,
)
from adh6.treasury.interfaces import PaymentMethodRepository
from adh6.treasury.transaction_manager import TransactionManager

from .interfaces import CharterRepository, MemberRepository, MembershipRepository

logger = logging.getLogger(__name__)

# The container clock is UTC. A receipt read by a human in Évry must not be dated the day before.
PARIS = ZoneInfo("Europe/Paris")


class SubscriptionManager:
    def __init__(
        self,
        member_repository: MemberRepository,
        membership_repository: MembershipRepository,
        charter_repository: CharterRepository,
        transaction_manager: TransactionManager,
        payment_method_repository: PaymentMethodRepository,
    ):
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.charter_repository = charter_repository
        self.payment_method_repository = payment_method_repository
        self.transaction_manager = transaction_manager

    @property
    def duration_price(self) -> dict[int, int]:
        return PRICES

    @property
    def duration_string(self) -> dict[int, str]:
        return DURATION_STRING

    def is_finished(self, status: MembershipStatus) -> bool:
        return status in [
            MembershipStatus.CANCELLED,
            MembershipStatus.ABORTED,
            MembershipStatus.COMPLETE,
        ]

    @log_call
    async def latest(self, member_id: int) -> Membership | None:
        """Get the latest subscription of a member, if it exists."""
        subscriptions, _ = await self.membership_repository.search(filter_=AbstractMembership(member=member_id))
        if not subscriptions:
            return None

        if n := next(
            filter(
                lambda x: not self.is_finished(MembershipStatus(x.status)),
                subscriptions,
            ),
            None,
        ):
            return n
        subscriptions.sort(key=lambda r: r.created_at or datetime.min, reverse=True)
        return subscriptions[0]

    @log_call
    async def create(self, member_id: int, body: SubscriptionBody) -> Membership:
        """
        Core use case of ADH. Registers a Subscription.

        User story: As an admin, I can create a new membership record, so that a member can have internet access.

        Args:
            ctx (_type_): _description_
            member_id (int): _description_
            body (SubscriptionBody): _description_

        Raises:
            MemberNotFoundError: _description_
            MembershipAlreadyExist: _description_
            NoPriceAssignedToThatDuration: _description_
            AccountNotFoundError: _description_
            PaymentMethodNotFoundError: _description_

        Returns:
            Membership: the subscription created
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        latest_subscription = await self.latest(member_id=member_id)

        if latest_subscription and latest_subscription.status not in [
            MembershipStatus.COMPLETE.value,
            MembershipStatus.CANCELLED.value,
            MembershipStatus.ABORTED.value,
        ]:
            raise MembershipAlreadyExist(latest_subscription.status)

        state = MembershipStatus.PENDING_RULES

        if state == MembershipStatus.PENDING_RULES:
            date_signed_minet = await self.charter_repository.get(member_id=member_id, charter_id=1)
            if date_signed_minet is not None and date_signed_minet != "":
                logging.getLogger(__name__).debug("create_membership_record_switch_status_to_pending_payment_initial")
                state = MembershipStatus.PENDING_PAYMENT_INITIAL

        if state == MembershipStatus.PENDING_PAYMENT_INITIAL and body.duration is not None and body.duration != 0:
            if body.duration not in self.duration_price:
                logging.getLogger(__name__).warning(
                    "create_membership_record_no_price_defined - duration: %s",
                    body.duration,
                )
                raise NoPriceAssignedToThatDuration(body.duration)
            logging.getLogger(__name__).debug(
                "create_membership_record_switch_status_to_pending_payment"
            )  # TODO: use a proper logger
            state = MembershipStatus.PENDING_PAYMENT

        if state == MembershipStatus.PENDING_PAYMENT and body.payment_method is not None:
            payment_method = await self.payment_method_repository.get_by_id(body.payment_method)
            if not payment_method:
                raise PaymentMethodNotFoundError(body.payment_method)
            logging.getLogger(__name__).debug("create_membership_record_switch_status_to_pending_payment_validation")
            state = MembershipStatus.PENDING_PAYMENT_VALIDATION

        try:
            membership_created = await self.membership_repository.create(body, state)
        except UnknownPaymentMethod:
            logging.getLogger(__name__).warning(
                "create_membership_record_unknown_payment_method"
            )  # TODO: use a proper logger
            raise

        return membership_created

    @log_call
    async def update(self, member_id: int, body: SubscriptionBody) -> None:
        """Update a subscription if not completed

        Args:
            ctx (_type_): _description_
            member_id (int): _description_
            body (SubscriptionBody): _description_

        Raises:
            MemberNotFoundError: _description_
            MembershipNotFoundError: _description_
            MembershipStatusNotAllowed: _description_
            CharterNotSigned: _description_
            NoPriceAssignedToThatDuration: _description_
            AccountNotFoundError: _description_
            PaymentMethodNotFoundError: _description_
        """
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        if member.wifi_only:
            raise WifiOnlyRestrictionError("wifi-only accounts cannot update their subscription")

        subscription = await self.latest(member_id=member_id)
        if not subscription:
            raise MembershipNotFoundError

        if subscription.status in [
            MembershipStatus.COMPLETE,
            MembershipStatus.CANCELLED,
            MembershipStatus.ABORTED,
        ]:
            raise MembershipStatusNotAllowed(
                subscription.status,
                "membership already completed, cancelled or aborted",
            )

        state = MembershipStatus(subscription.status)

        if state == MembershipStatus.PENDING_RULES:
            date_signed_minet = await self.charter_repository.get(member_id=member_id, charter_id=1)
            if date_signed_minet is not None and date_signed_minet != "":
                logging.debug("create_membership_record_switch_status_to_pending_payment_initial")  # noqa: LOG015  # TODO: use a proper logger
                state = MembershipStatus.PENDING_PAYMENT_INITIAL
            else:
                raise CharterNotSigned(str(member_id))

        if body.duration is not None and body.duration != 0 and body.duration not in self.duration_price:
            logging.getLogger(__name__).warning(
                "create_membership_record_no_price_defined - duration: %s",
                body.duration,
            )  # TODO: use a proper logger
            raise NoPriceAssignedToThatDuration(body.duration)

        if state == MembershipStatus.PENDING_PAYMENT_INITIAL and body.duration is not None:
            logging.debug("create_membership_record_switch_status_to_pending_payment")  # noqa: LOG015  # TODO: use a proper logger
            state = MembershipStatus.PENDING_PAYMENT

        if body.payment_method is not None:
            payment_method = await self.payment_method_repository.get_by_id(body.payment_method)
            if not payment_method:
                raise PaymentMethodNotFoundError(body.payment_method)

        if state == MembershipStatus.PENDING_PAYMENT and body.payment_method is not None:
            logging.debug("create_membership_record_switch_status_to_pending_payment_validation")  # noqa: LOG015
            state = MembershipStatus.PENDING_PAYMENT_VALIDATION

        await self.membership_repository.update(subscription.uuid, body, state)

    @log_call
    async def validate(self, member_id: int, free: bool) -> None:
        member = await self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        subscription = await self.latest(member_id=member_id)
        if not subscription:
            raise MembershipNotFoundError(None)
        if subscription.status == MembershipStatus.PENDING_RULES.value:
            # Read the signature instead of inferring it from the status. Keycloak's charter
            # Required Action writes `adherents.datesignedminet` with a direct UPDATE, without
            # going through charter_manager.sign, so it never advances a waiting membership. A
            # member can therefore be signed AND still sit in PENDING_RULES -- announcing "charter
            # not signed" to them would send the reader looking in the wrong place, which is the
            # very problem this branch exists to fix.
            signed_at = await self.charter_repository.get(member_id=member_id, charter_id=1)
            if signed_at:
                raise MembershipStatusNotAllowed(
                    subscription.status,
                    "the charter is signed but this membership was never advanced past PENDING_RULES",
                )
            raise CharterNotSigned(str(member_id))

        if subscription.status != MembershipStatus.PENDING_PAYMENT_VALIDATION.value:
            raise MembershipStatusNotAllowed(subscription.status, "status cannot be used to validate a membership")

        await self.membership_repository.validate(subscription.uuid)
        await self.add_payment_record(subscription, free)
        if subscription.duration is None:
            raise MembershipNotFoundError(None)
        await self.member_repository.add_duration(subscription.member, subscription.duration)

        await self._send_receipt(member, subscription, free)

    async def _author_label(self) -> str:
        """Who took the money.

        Worth a query: for cash handled at the desk, a name is the only accountability trail there
        is. Never fails -- falls back to the raw id, then to a generic label.
        """
        author_id = get_user()
        if author_id is None:
            return "clé d'API"
        try:
            author = await self.member_repository.get_by_id(author_id)
        except Exception:
            return str(author_id)
        return author.username if author else str(author_id)

    async def _send_receipt(self, member: Member, subscription: Membership, free: bool) -> None:
        """Receipt for a subscription recorded at the desk.

        Members paying online already get one from payment; those paying cash at the desk got
        nothing -- yet cash is precisely the case where they hold no other proof of payment.

        Never raises: a delivery failure must not undo a subscription that is already committed.
        Called after add_duration so the departure date read here is the new one.
        """
        if not member.email:
            logger.warning("Member %s has no email address, not sending the receipt", member.id)
            return
        # Both are Optional on the generated entity, and a receipt without them would be
        # meaningless anyway: no amount, no payment method.
        duration = subscription.duration
        payment_method_id = subscription.payment_method
        if duration is None or payment_method_id is None:
            logger.warning(
                "Membership of member %s has no duration or no payment method, not sending the receipt",
                member.id,
            )
            return

        try:
            price = "0.00" if free else f"{self.duration_price[duration]:.2f}"
            method = await self.payment_method_repository.get_by_id(payment_method_id)
            # Re-read: add_duration has just moved the departure date, the member we hold is stale.
            fresh = await self.member_repository.get_by_id(member.id)
            end_date = fresh.departure_date if fresh else None
            method_name = method.name if method else "-"
            end_day = end_date.date() if isinstance(end_date, datetime) else end_date
            now = datetime.now(PARIS)

            await mail.send_subscription_receipt_async(
                to=member.email,
                first_name=member.first_name or member.username,
                username=member.username,
                price=price,
                months=duration,
                end_date=end_day,
                payment_method=method_name,
                paid_at=now.date(),
                language=fresh.preferred_language if fresh else None,
            )

            # The treasury list saw every online payment through payment, but nothing for desk
            # payments -- the ones involving cash in a box.
            if settings.treasury_recipients:
                await mail.send_subscription_admin_async(
                    to=settings.treasury_recipients,
                    username=member.username,
                    adh6_url=f"https://{settings.adh6_url}/fr/member/view/{member.id}/payment",
                    price=price,
                    months=duration,
                    end_date=end_day,
                    payment_method=method_name,
                    author=await self._author_label(),
                    paid_at=now,
                )
        except Exception:
            logger.warning("Cannot send the subscription receipt to member %s", member.id, exc_info=True)

    @log_call
    async def add_payment_record(self, membership: Membership, free: bool) -> None:
        if membership.payment_method is None:
            raise MembershipNotFoundError(None)
        payment_method = await self.payment_method_repository.get_by_id(membership.payment_method)
        if membership.duration is None:
            raise MembershipNotFoundError(None)
        price = self.duration_price[membership.duration]
        title = f"Internet - {self.duration_string.get(membership.duration)}"
        if price == 50 and not membership.has_room:
            price = 9
            title = title + " (sans chambre)"

        await self.transaction_manager.update_or_create(
            AbstractTransaction(
                value=price if not free else 0,
                name=title + " (gratuit)" if free else title,
                paymentMethod=payment_method.id,  # type: ignore
                author=get_user(),
                apiKeyId=get_api_key_id(),
                productType="cotisation",
                membershipUuid=membership.uuid,
            )
        )
