# coding=utf-8
""" Use cases (business rule layer) of everything related to members. """
from ipaddress import IPv4Address, IPv4Network
from typing import Dict, List, Optional, Tuple, Union

from adh6.constants import CTX_ADMIN, CTX_ROLES, KnownAccountExpense, MembershipStatus, SUBNET_PUBLIC_ADDRESSES_WIRELESS, PRICES, DURATION_STRING
from adh6.entity import (
    AbstractMember, Member,
    AbstractMembership, Membership,
    AbstractDevice, MemberStatus,
    AbstractAccount,
)
from adh6.entity.abstract_transaction import AbstractTransaction
from adh6.entity.payment_method import PaymentMethod
from adh6.entity.subscription_body import SubscriptionBody
from adh6.entity.validators.member_validators import is_member_active
from adh6.exceptions import (
    AccountNotFoundError,
    AccountTypeNotFoundError,
    MembershipNotFoundError,
    NoSubnetAvailable,
    MemberNotFoundError,
    MemberAlreadyExist,
    MembershipAlreadyExist,
    UnauthorizedError,
    UnknownPaymentMethod,
    LogFetchError,
    NoPriceAssignedToThatDuration,
    IntMustBePositive,
    MembershipStatusNotAllowed,
    CharterNotSigned,
    UpdateImpossible,
    ValidationError
)
from adh6.device.storage.device_repository import DeviceType
from adh6.device.interfaces.device_repository import DeviceRepository
from adh6.device.device_manager import DeviceManager
from adh6.default.crud_manager import CRUDManager
from adh6.default.decorator.auto_raise import auto_raise
from adh6.authentication.security import Roles
from adh6.treasury.interfaces.account_repository import AccountRepository
from adh6.treasury.interfaces.account_type_repository import AccountTypeRepository
from adh6.treasury.interfaces.transaction_repository import TransactionRepository
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.member.interfaces.logs_repository import LogsRepository
from adh6.member.interfaces.member_repository import MemberRepository
from adh6.member.interfaces.membership_repository import MembershipRepository
from adh6.util.context import log_extra
from adh6.util.log import LOG
from adh6.default.decorator.log_call import log_call
import re


class MemberManager(CRUDManager):
    """
    Implements all the use cases related to member management.
    """

    def __init__(self, member_repository: MemberRepository, membership_repository: MembershipRepository,
                 logs_repository: LogsRepository, payment_method_repository: PaymentMethodRepository,
                 device_repository: DeviceRepository, account_repository: AccountRepository,
                 transaction_repository: TransactionRepository,  account_type_repository: AccountTypeRepository,
                 device_manager: DeviceManager):
        super().__init__(member_repository, AbstractMember, MemberNotFoundError)
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.logs_repository = logs_repository
        self.device_repository = device_repository
        self.payment_method_repository = payment_method_repository
        self.account_repository = account_repository
        self.account_type_repository = account_type_repository
        self.transaction_repository = transaction_repository
        self.device_manager = device_manager

    @property
    def duration_price(self) -> Dict[int, int]:
        return PRICES

    @property
    def duration_string(self) -> Dict[int, str]:
        return DURATION_STRING

    @log_call
    @auto_raise
    def get_by_id(self, ctx, id: int):
        latest_sub = self.latest_subscription(ctx, id)
        member = super().get_by_id(ctx, id)
        member.membership = latest_sub.status if latest_sub else None
        return member

    @log_call
    @auto_raise
    def get_profile(self, ctx) -> Tuple[AbstractMember, List[str]]:
        user = ctx.get(CTX_ADMIN)
        m = self.member_repository.get_by_id(ctx, user)
        return m, ctx.get(CTX_ROLES)

    @log_call
    @auto_raise
    def new_member(self, ctx, member: AbstractMember) -> Member:
        LOG.debug("create_member_records", extra=log_extra(ctx, username=member.username))
        # Check that the user exists in the system.
        fetched_member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(username=member.username))
        if fetched_member:
            raise MemberAlreadyExist(fetched_member[0].username)

        fetched_account_type, _ = self.account_type_repository.search_by(ctx, terms="Adhérent")
        if not fetched_account_type:
            raise AccountTypeNotFoundError("Adhérent") 
 
        created_member = self.member_repository.create(ctx, member)
        _ = self.account_repository.create(ctx, AbstractAccount(
            id=0,
            actif=True,
            account_type=fetched_account_type[0].id,
            member=created_member.id,
            name=f'{created_member.first_name} {created_member.last_name} ({created_member.username})',
            pinned=False,
            compte_courant=False,
            balance=0,
            pending_balance=0
        ))

        _ = self.create_subscription(
            ctx=ctx, 
            member_id=created_member.id, 
            body=SubscriptionBody(
                member=created_member.id
            ),
        )
        return created_member

    @log_call
    @auto_raise
    def update_member(self, ctx, id: int, abstract_member: AbstractMember, override: bool) -> None:
        member = self.__member_not_found(ctx, id)
        latest_sub = self.latest_subscription(ctx, id)
        if not latest_sub or latest_sub.status not in [
            MembershipStatus.CANCELLED.value,
            MembershipStatus.ABORTED.value,
            MembershipStatus.COMPLETE.value
        ]:
            raise UpdateImpossible(f'member {member.username}', 'membership not validated')

        if abstract_member.mailinglist:
            if abstract_member.mailinglist < 0:
                raise IntMustBePositive(abstract_member.mailinglist)
            if abstract_member.mailinglist > 255: # Allow subscription to 4 or less mailinglists
                raise ValidationError("Number to high")

        is_room_changed = abstract_member.room_number is not None and (member.room_number is None or (member.room_number is not None and abstract_member.room_number != member.room_number))
        member = self.member_repository.update(ctx, abstract_member, override)

        if not is_member_active(member):
            self.reset_member(ctx, id)
        else:
            if member.ip is None or member.subnet is None:
                self.update_subnet(ctx, id)
            if is_room_changed:
                devices_to_refresh, _ = self.device_repository.search_by(ctx, filter_=AbstractDevice(
                    member=member.id,
                    connection_type=DeviceType.wired.name
                ))
                for d in devices_to_refresh:
                    self.device_manager.allocate_ip_addresses(ctx, d, True)

    def is_subscription_finished(self, status: MembershipStatus) -> bool:
        return status in [
            MembershipStatus.CANCELLED,
            MembershipStatus.ABORTED,
            MembershipStatus.COMPLETE
        ]

    @log_call
    @auto_raise
    def latest_subscription(self, ctx, member_id: int) -> Union[Membership, None]:
        LOG.debug("get_latest_membership_records", extra=log_extra(ctx, id=member_id))
        subscriptions, _ = self.membership_repository.search(
            ctx=ctx,
            filter_=AbstractMembership(member=member_id)
        )
        if not subscriptions:
            return None
        if n := next(filter(lambda x: not self.is_subscription_finished(MembershipStatus(x.status)), subscriptions), None):
            return n
        subscriptions.sort(key=lambda r: r.created_at, reverse=True)
        return subscriptions[0]


    @log_call
    @auto_raise
    def create_subscription(self, ctx, member_id: int, body: SubscriptionBody) -> Membership:
        """
        Core use case of ADH. Registers a membership.

        User story: As an admin, I can create a new membership record, so that a member can have internet access.
        :param ctx: context
        :param member_id: member_id
        :param membership: entity AbstractMembership

        :raise IntMustBePositiveException
        :raise NoPriceAssignedToThatDurationException
        :raise MemberNotFound
        :raise UnknownPaymentMethod
        """

        self.__member_not_found(ctx, member_id)

        latest_subscription = self.latest_subscription(ctx=ctx, member_id=member_id)
        
        if latest_subscription and latest_subscription.status not in[
            MembershipStatus.COMPLETE.value,
            MembershipStatus.CANCELLED.value,
            MembershipStatus.ABORTED.value
        ]:
            raise MembershipAlreadyExist(latest_subscription.status)

        state = MembershipStatus.PENDING_RULES

        if state == MembershipStatus.PENDING_RULES:
            date_signed_minet = self.member_repository.get_charter(ctx, member_id, 1)
            if date_signed_minet is not None and date_signed_minet != "":
                LOG.debug("create_membership_record_switch_status_to_pending_payment_initial")
                state = MembershipStatus.PENDING_PAYMENT_INITIAL

        if state == MembershipStatus.PENDING_PAYMENT_INITIAL:
            if body.duration is not None and body.duration != 0:
                if body.duration < 0:
                    raise IntMustBePositive('duration')
                if body.duration not in self.duration_price:
                    LOG.warning("create_membership_record_no_price_defined", extra=log_extra(ctx, duration=body.duration))
                    raise NoPriceAssignedToThatDuration(body.duration)
                LOG.debug("create_membership_record_switch_status_to_pending_payment")
                state = MembershipStatus.PENDING_PAYMENT

        if state == MembershipStatus.PENDING_PAYMENT:
            if body.account is not None and body.payment_method is not None:
                self.__account_not_found(ctx, body.account)
                self.__payment_method_not_found(ctx, body.payment_method)
                LOG.debug("create_membership_record_switch_status_to_pending_payment_validation")
                state = MembershipStatus.PENDING_PAYMENT_VALIDATION

        try:
            membership_created = self.membership_repository.create(ctx, body, state)
        except UnknownPaymentMethod:
            LOG.warning("create_membership_record_unknown_payment_method", extra=log_extra(ctx, payment_method=body.payment_method))
            raise

        LOG.info("create_membership_record", extra=log_extra(
            ctx,
            membership_uuis=membership_created.uuid,
            membership_status=membership_created.status
        ))

        return membership_created


    @log_call
    @auto_raise
    def update_subscription(self, ctx, member_id: int, body: SubscriptionBody) -> None:
        self.__member_not_found(ctx, member_id)
        
        subscription = self.latest_subscription(ctx=ctx, member_id=member_id)    
        if not subscription:
            raise MembershipNotFoundError()

        if subscription.status in [MembershipStatus.COMPLETE, MembershipStatus.CANCELLED, MembershipStatus.ABORTED]:
            raise MembershipStatusNotAllowed(subscription.status, "membership already completed, cancelled or aborted")

        state = MembershipStatus(subscription.status)

        if state == MembershipStatus.PENDING_RULES:
            date_signed_minet = self.member_repository.get_charter(ctx, member_id, 1)
            if date_signed_minet is not None and date_signed_minet != "":
                LOG.debug("create_membership_record_switch_status_to_pending_payment_initial")
                state = MembershipStatus.PENDING_PAYMENT_INITIAL
            else:
                raise CharterNotSigned(str(member_id))


        if body.duration is not None and body.duration != 0:
            if body.duration < 0:
                raise IntMustBePositive('duration')
            if body.duration not in self.duration_price:
                LOG.warning("create_membership_record_no_price_defined", extra=log_extra(ctx, duration=body.duration))
                raise NoPriceAssignedToThatDuration(body.duration)

        if state == MembershipStatus.PENDING_PAYMENT_INITIAL:
            if body.duration is not None:
                LOG.debug("create_membership_record_switch_status_to_pending_payment")
                state = MembershipStatus.PENDING_PAYMENT

        if body.account is not None:
            self.__account_not_found(ctx, body.account)
        if body.payment_method is not None:
            self.__payment_method_not_found(ctx, body.payment_method)

        if state == MembershipStatus.PENDING_PAYMENT:
            if body.account is not None and body.payment_method is not None:
                LOG.debug("create_membership_record_switch_status_to_pending_payment_validation")
                state = MembershipStatus.PENDING_PAYMENT_VALIDATION

        try:
            self.membership_repository.update(ctx, subscription.uuid, body, state)
        except Exception:
            raise


    @log_call
    @auto_raise
    def validate_subscription(self, ctx, member_id: int, free: bool):
        self.__member_not_found(ctx, member_id)
        subscription = self.latest_subscription(ctx=ctx, member_id=member_id)    
        if not subscription:
            raise MembershipNotFoundError(None)
        print(subscription)
        if subscription.status != MembershipStatus.PENDING_PAYMENT_VALIDATION.value:
            raise MembershipStatusNotAllowed(subscription.status, "status cannot be used to validate a membership")

        self.membership_repository.validate(ctx, subscription.uuid)
        self.add_membership_payment_record(ctx, subscription, free)
        self.member_repository.add_duration(ctx, subscription.member, subscription.duration)
        self.update_subnet(ctx, member_id) 


    @log_call
    @auto_raise
    def add_membership_payment_record(self, ctx, membership: Membership, free: bool):
        LOG.debug("membership_add_membership_payment_record", extra=log_extra(ctx, duration=membership.duration, membership_accoun=membership.account))

        if free and not Roles.TRESO_WRITE.value in ctx.get(CTX_ROLES):
            raise UnauthorizedError("Impossibilité de faire une cotisation gratuite")

        payment_method = self.payment_method_repository.get_by_id(ctx, membership.payment_method)
        asso_account, _ = self.account_repository.search_by(ctx, limit=1, filter_=AbstractAccount(name=KnownAccountExpense.ASSOCIATION_EXPENCE.value))
        if len(asso_account) != 1:
            raise AccountNotFoundError(KnownAccountExpense.ASSOCIATION_EXPENCE.value)
        tech_account, _ = self.account_repository.search_by(ctx, limit=1, filter_=AbstractAccount(name=KnownAccountExpense.TECHNICAL_EXPENSE.value))
        if len(tech_account) != 1:
            raise AccountNotFoundError(KnownAccountExpense.TECHNICAL_EXPENSE.value)
        src_account = self.account_repository.get_by_id(ctx, membership.account)
        price = self.duration_price[membership.duration]  # Expressed in EUR.
        if price == 50 and not membership.has_room:
            price = 9
        duration_str = self.duration_string.get(membership.duration)
        title = f'Internet - {duration_str}'

        self.transaction_repository.create(
            ctx, 
            AbstractTransaction(
                value=9 if not free else 0,
                src=src_account.id,
                dst=asso_account[0].id,
                name=title + " (gratuit)" if free else title,
                payment_method=payment_method.id
            )
        )
        if price > 9 and not free:
            self.transaction_repository.create(
                ctx, 
                AbstractTransaction(
                    value=price-9,
                    src=src_account.id,
                    dst=tech_account[0].id,
                    name=title,
                    payment_method=payment_method.id
                )
            )


    def __account_not_found(self, ctx, account: int) -> None:
        _ = self.account_repository.get_by_id(ctx, account)

    def __payment_method_not_found(self, ctx, payment_method: int) -> PaymentMethod:
        return self.payment_method_repository.get_by_id(ctx, payment_method)
    
    def __member_not_found(self, ctx, member: int) -> AbstractMember:
        return self.member_repository.get_by_id(ctx, member)


    @log_call
    @auto_raise
    def get_logs(self, ctx, member_id, dhcp=False) -> List[str]:
        """
        User story: As an admin, I can retrieve the logs of a member, so I can help him troubleshoot their connection
        issues.

        :raise MemberNotFound
        """
        # Fetch all the devices of the member to put them in the request
        # all_devices = get_all_devices(s)
        # query = session.query(all_devices, Adherent.login.label("login"))
        # query = query.join(Adherent, Adherent.id == all_devices.columns.adherent_id)
        # query = query.filter(Adherent.login == username)
        # mac_tbl = list(map(lambda x: x.mac, query.all()))

        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)

        # Do the actual log fetching.
        try:
            devices = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=member[0].id))[0]
            logs = self.logs_repository.get_logs(ctx, username=member[0].username, devices=devices, dhcp=dhcp)

            return list(map(
                lambda x: "{} {}".format(x[0], x[1]),
                logs
            ))

        except LogFetchError:
            LOG.warning("log_fetch_failed", extra=log_extra(ctx, username=member[0].username))
            return []  # We fail open here.


    @log_call
    @auto_raise
    def get_statuses(self, ctx, member_id) -> List[MemberStatus]:
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)

        member = member[0]

        # Do the actual log fetching.
        try:
            devices = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=member.id))[0]
            logs = self.logs_repository.get_logs(ctx, username=member.username, devices=devices, dhcp=False)
            device_to_statuses = {}
            last_ok_login_mac = {}

            def add_to_statuses(status, timestamp, mac):
                if mac not in device_to_statuses:
                    device_to_statuses[mac] = {}
                if status not in device_to_statuses[mac] or device_to_statuses[mac][
                    status].last_timestamp < timestamp:
                    device_to_statuses[mac][status] = MemberStatus(status=status, last_timestamp=timestamp,
                                                                   comment=mac)

            prev_log = ["", ""]
            for log in logs:
                if "Login OK" in log[1]:
                    match = re.search(r'.*?Login OK:\s*\[(.*?)\].*?cli ([a-f0-9|-]+)\).*', log[1])
                    if match is not None:
                        login, mac = match.group(1), match.group(2).upper()
                        if mac not in last_ok_login_mac or last_ok_login_mac[mac] < log[0]:
                            last_ok_login_mac[mac] = log[0]
                if "EAP sub-module failed" in prev_log[1] \
                        and "mschap: MS-CHAP2-Response is incorrect" in log[1] \
                        and (prev_log[0] - log[0]).total_seconds() < 1:
                    match = re.search(r'.*?EAP sub-module failed\):\s*\[(.*?)\].*?cli ([a-f0-9\-]+)\).*',
                                      prev_log[1])
                    if match:
                        login, mac = match.group(1), match.group(2).upper()
                        if login != member.username:
                            add_to_statuses("LOGIN_INCORRECT_WRONG_USER", log[0], mac)
                        else:
                            add_to_statuses("LOGIN_INCORRECT_WRONG_PASSWORD", log[0], mac)
                if 'rlm_python' in log[1]:
                    match = re.search(r'.*?rlm_python: Fail (.*?) ([a-f0-9A-F\-]+) with (.+)', log[1])
                    if match is not None:
                        login, mac, reason = match.group(1), match.group(2).upper(), match.group(3)
                        if 'MAC not found and not association period' in reason:
                            add_to_statuses("LOGIN_INCORRECT_WRONG_MAC", log[0], mac)
                        if 'Adherent not found' in reason:
                            add_to_statuses("LOGIN_INCORRECT_WRONG_USER", log[0], mac)
                if "TLS Alert" in log[1]:  # @TODO Difference between TLS Alert read and TLS Alert write ??
                    # @TODO a read access denied means the user is validating the certificate
                    # @TODO a read/write protocol version is ???
                    # @TODO a write unknown CA means the user is validating the certificate
                    # @TODO a write decryption failed is ???
                    # @TODO a read internal error is most likely not user-related
                    # @TODO a write unexpected_message is ???
                    match = re.search(
                        r'.*?TLS Alert .*?\):\s*\[(.*?)\].*?cli ([a-f0-9\-]+)\).*',
                        log[1])
                    if match is not None:
                        login, mac = match.group(1), match.group(2).upper()
                        add_to_statuses("LOGIN_INCORRECT_SSL_ERROR", log[0], mac)
                prev_log = log

            all_statuses = []
            for mac, statuses in device_to_statuses.items():
                for _, object in statuses.items():
                    if mac in last_ok_login_mac and object.last_timestamp < last_ok_login_mac[mac]:
                        continue
                    all_statuses.append(object)
            return all_statuses

        except LogFetchError:
            LOG.warning("log_fetch_failed", extra=log_extra(ctx, username=member.username))
            return []  # We fail open here.


    @log_call
    def change_password(self, ctx, member_id, password: str, hashed_password):
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)

        from binascii import hexlify
        import hashlib

        pw = hashed_password or hexlify(hashlib.new('md4', password.encode('utf-16le')).digest())

        self.member_repository.update_password(ctx, member_id, pw)

        return True

    @log_call
    @auto_raise
    def update_charter(self, ctx, member_id, charter_id: int) -> None:
        self.member_repository.update_charter(ctx, member_id, charter_id)

    @log_call
    @auto_raise
    def get_charter(self, ctx, member_id, charter_id: int) -> str:
        return self.member_repository.get_charter(ctx, member_id, charter_id)

    @log_call
    @auto_raise
    def update_subnet(self, ctx, member_id) -> Optional[Tuple[IPv4Network, IPv4Address]]:
        member = self.__member_not_found(ctx, member_id)
        if not is_member_active(member):
            return None

        used_wireles_public_ips = self.member_repository.used_wireless_public_ips(ctx)

        subnet = None
        ip = None
        if len(used_wireles_public_ips) < len(SUBNET_PUBLIC_ADDRESSES_WIRELESS):
            for i, s in SUBNET_PUBLIC_ADDRESSES_WIRELESS.items():
                if i not in used_wireles_public_ips:
                    subnet = s
                    ip = i
        
        if subnet is None:
            raise NoSubnetAvailable("wireless")

        self.member_repository.update(ctx, AbstractMember(id=member_id, subnet=str(subnet), ip=str(ip)))
        member = self.__member_not_found(ctx, member_id)

        # Update wireless devices
        devices_to_reset, _ = self.device_repository.search_by(ctx, filter_=AbstractDevice(
            member=member.id,
            connection_type=DeviceType.wireless.name
        ))
        for d in devices_to_reset:
            self.device_manager.allocate_ip_addresses(ctx, d, True)

        return subnet, ip

    @log_call
    @auto_raise
    def reset_member(self, ctx, member_id) -> None:
        member = self.__member_not_found(ctx, member_id)
        self.member_repository.update(ctx, AbstractMember(
            id=member_id,
            room_number=-1, 
            ip="", 
            subnet=""
        ))
        devices_to_reset, _ = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=member.id))
        for d in devices_to_reset:
            self.device_manager.unallocate_ip_addresses(ctx, d)
