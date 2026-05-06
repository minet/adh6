import logging
from datetime import datetime

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
from .notification_manager import NotificationManager


class SubscriptionManager:
    def __init__(
        self,
        member_repository: MemberRepository,
        membership_repository: MembershipRepository,
        charter_repository: CharterRepository,
        notification_manager: NotificationManager,
        transaction_manager: TransactionManager,
        payment_method_repository: PaymentMethodRepository,
    ):
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.charter_repository = charter_repository
        self.notification_manager = notification_manager
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
        if subscription.status != MembershipStatus.PENDING_PAYMENT_VALIDATION.value:
            raise MembershipStatusNotAllowed(subscription.status, "status cannot be used to validate a membership")

        await self.membership_repository.validate(subscription.uuid)
        await self.add_payment_record(subscription, free)
        if subscription.duration is None:
            raise MembershipNotFoundError(None)
        await self.member_repository.add_duration(subscription.member, subscription.duration)
        # self.notification_manager.send(template_title="Nouvelle cotisation / New subscription", member_email=member.email, subscription_duration=subscription.duration.value, subscription_end=member.departure_date)

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
