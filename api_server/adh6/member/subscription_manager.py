import typing as t
import logging

from adh6.constants import KnownAccountExpense
from adh6.entity import (
    Membership,
    AbstractAccount, 
    AbstractTransaction,
    SubscriptionBody
)
from adh6.exceptions import (
    AccountNotFoundError,
    MembershipNotFoundError,
    MemberNotFoundError,
    MembershipAlreadyExist,
    UnknownPaymentMethod,
    NoPriceAssignedToThatDuration,
    MembershipStatusNotAllowed,
    CharterNotSigned
)
from adh6.decorator import log_call
from adh6.treasury import TransactionManager, PaymentMethodManager, AccountManager

from .enums import MembershipStatus
from .notification_manager import NotificationManager
from .charter_manager import CharterManager
from .interfaces import MemberRepository, MembershipRepository


DURATION_STRING = {
    1: '1 mois',
    2: '2 mois',
    3: '3 mois',
    4: '4 mois',
    5: '5 mois',
    6: '6 mois',
    12: '1 an',
}


PRICES = {
    1: 9,
    2: 18,
    3: 27,
    4: 36,
    5: 45,
    12: 50,
}


class SubscriptionManager:
    def __init__(self, 
                member_repository: MemberRepository, 
                membership_repository: MembershipRepository, 
                charter_manager: CharterManager, 
                notification_manager: NotificationManager,
                transaction_manager: TransactionManager, 
                payment_method_manager: PaymentMethodManager, 
                account_manager: AccountManager):
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.charter_manager = charter_manager
        self.notification_manager = notification_manager
        self.account_manager = account_manager
        self.payment_method_manager = payment_method_manager
        self.transaction_manager = transaction_manager

    @property
    def duration_price(self) -> t.Dict[int, int]:
        return PRICES

    @property
    def duration_string(self) -> t.Dict[int, str]:
        return DURATION_STRING

    def is_finished(self, status: MembershipStatus) -> bool:
        return status in [
            MembershipStatus.CANCELLED,
            MembershipStatus.ABORTED,
            MembershipStatus.COMPLETE
        ]

    @log_call
    def latest(self, member_id: int) -> t.Union[Membership, None]:
        m = self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        subscriptions = self.membership_repository.from_member(m)
        if not subscriptions:
            return None
        if n := next(filter(lambda x: not self.is_finished(MembershipStatus(x.status)), subscriptions), None):
            return n
        subscriptions.sort(key=lambda r: r.created_at, reverse=True)
        return subscriptions[0]


    @log_call
    def create(self, member_id: int, body: SubscriptionBody) -> Membership:
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
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        latest_subscription = self.latest(member_id=member_id)
        
        if latest_subscription and latest_subscription.status not in[
            MembershipStatus.COMPLETE.value,
            MembershipStatus.CANCELLED.value,
            MembershipStatus.ABORTED.value
        ]:
            raise MembershipAlreadyExist(latest_subscription.status)

        state = MembershipStatus.PENDING_RULES

        if state == MembershipStatus.PENDING_RULES:
            date_signed_minet = self.charter_manager.get(member_id=member_id, charter_id=1)
            if date_signed_minet is not None and date_signed_minet != "":
                logging.debug("create_membership_record_switch_status_to_pending_payment_initial")
                state = MembershipStatus.PENDING_PAYMENT_INITIAL

        if state == MembershipStatus.PENDING_PAYMENT_INITIAL:
            if body.duration is not None and body.duration != 0:
                if body.duration not in self.duration_price:
                    logging.warning(f"create_membership_record_no_price_defined - duration: {body.duration}")
                    raise NoPriceAssignedToThatDuration(body.duration)
                logging.debug("create_membership_record_switch_status_to_pending_payment")
                state = MembershipStatus.PENDING_PAYMENT

        if state == MembershipStatus.PENDING_PAYMENT:
            if body.account is not None and body.payment_method is not None:
                _ = self.account_manager.get_by_id(body.account)
                _ = self.payment_method_manager.get_by_id(body.payment_method)
                logging.debug("create_membership_record_switch_status_to_pending_payment_validation")
                state = MembershipStatus.PENDING_PAYMENT_VALIDATION

        try:
            membership_created = self.membership_repository.create(body, state)
        except UnknownPaymentMethod:
            logging.warning("create_membership_record_unknown_payment_method")
            raise

        return membership_created


    @log_call
    def update(self, member_id: int, body: SubscriptionBody) -> None:
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
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        
        subscription = self.latest(member_id=member_id)    
        if not subscription:
            raise MembershipNotFoundError()

        if subscription.status in [MembershipStatus.COMPLETE, MembershipStatus.CANCELLED, MembershipStatus.ABORTED]:
            raise MembershipStatusNotAllowed(subscription.status, "membership already completed, cancelled or aborted")

        state = MembershipStatus(subscription.status)

        if state == MembershipStatus.PENDING_RULES:
            date_signed_minet = self.charter_manager.get(member_id=member_id, charter_id=1)
            if date_signed_minet is not None and date_signed_minet != "":
                logging.debug("create_membership_record_switch_status_to_pending_payment_initial")
                state = MembershipStatus.PENDING_PAYMENT_INITIAL
            else:
                raise CharterNotSigned(str(member_id))


        if body.duration is not None and body.duration != 0:
            if body.duration not in self.duration_price:
                logging.warning(f"create_membership_record_no_price_defined - duration: {body.duration}")
                raise NoPriceAssignedToThatDuration(body.duration)

        if state == MembershipStatus.PENDING_PAYMENT_INITIAL:
            if body.duration is not None:
                logging.debug("create_membership_record_switch_status_to_pending_payment")
                state = MembershipStatus.PENDING_PAYMENT

        if body.account is not None:
            _ = self.account_manager.get_by_id(body.account)
        if body.payment_method is not None:
            _ = self.payment_method_manager.get_by_id(body.payment_method)

        if state == MembershipStatus.PENDING_PAYMENT:
            if body.account is not None and body.payment_method is not None:
                logging.debug("create_membership_record_switch_status_to_pending_payment_validation")
                state = MembershipStatus.PENDING_PAYMENT_VALIDATION

        try:
            self.membership_repository.update(subscription.uuid, body, state)
        except Exception:
            raise


    @log_call
    def validate(self, member_id: int, free: bool) -> None:
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        subscription = self.latest(member_id=member_id)    
        if not subscription:
            raise MembershipNotFoundError(None)
        if subscription.status != MembershipStatus.PENDING_PAYMENT_VALIDATION.value:
            raise MembershipStatusNotAllowed(subscription.status, "status cannot be used to validate a membership")

        self.membership_repository.validate(subscription.uuid)
        self.add_payment_record(subscription, free)
        self.member_repository.add_duration(subscription.member, subscription.duration)
        self.notification_manager.send(template_title="Nouvelle cotisation / New subscription", member_email=member.email, subscription_duration=subscription.duration.value, subscription_end=member.departure_date)

    @log_call
    def add_payment_record(self, membership: Membership, free: bool) -> None:
        payment_method = self.payment_method_manager.get_by_id(membership.payment_method)
        asso_account, _ = self.account_manager.search(limit=1, filter_=AbstractAccount(name=KnownAccountExpense.ASSOCIATION_EXPENCE.value))
        if len(asso_account) != 1:
            raise AccountNotFoundError(KnownAccountExpense.ASSOCIATION_EXPENCE.value)
        tech_account, _ = self.account_manager.search(limit=1, filter_=AbstractAccount(name=KnownAccountExpense.TECHNICAL_EXPENSE.value))
        if len(tech_account) != 1:
            raise AccountNotFoundError(KnownAccountExpense.TECHNICAL_EXPENSE.value)
        src_account = self.account_manager.get_by_id(membership.account)
        price = self.duration_price[membership.duration]  # Expressed in EUR.
        title = f'Internet - {self.duration_string.get(membership.duration)}'
        if price == 50 and not membership.has_room:
            price = 9
            title = title + " (sans chambre)"

        self.transaction_manager.update_or_create(
            AbstractTransaction(
                value=9 if not free else 0,
                src=src_account.id,
                dst=asso_account[0].id,
                name=title + " (gratuit)" if free else title,
                payment_method=payment_method.id
            )
        )
        if price > 9 and not free:
            self.transaction_manager.update_or_create(
                AbstractTransaction(
                    value=price-9,
                    src=src_account.id,
                    dst=tech_account[0].id,
                    name=title,
                    payment_method=payment_method.id
                )
            )