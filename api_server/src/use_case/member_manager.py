# coding=utf-8
""" Use cases (business rule layer) of everything related to members. """
from ipaddress import IPv4Address, IPv4Network
from typing import Dict, List, Optional, Tuple, Union

from src.constants import CTX_ADMIN, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus, SUBNET_PUBLIC_ADDRESSES_WIRELESS, PRICES, DURATION_STRING
from src.entity import (
    AbstractMember, Member,
    AbstractMembership, Membership,
    AbstractDevice, MemberStatus,
    AbstractAccount, Account,
    AbstractPaymentMethod,
    AccountType
)
from src.entity.payment_method import PaymentMethod
from src.entity.validators.member_validators import is_member_active
from src.exceptions import (
    AccountTypeNotFoundError,
    MembershipNotFoundError,
    NoSubnetAvailable,
    PaymentMethodNotFoundError,
    AccountNotFoundError,
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
    UpdateImpossible
)
from src.interface_adapter.sql.device_repository import DeviceType
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, Roles, defines_security, has_any_role, is_admin, owns, uses_security, User
from src.use_case.device_manager import DeviceManager
from src.use_case.interface.account_repository import AccountRepository
from src.use_case.interface.account_type_repository import AccountTypeRepository
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.logs_repository import LogsRepository
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.util.context import log_extra
from src.util.log import LOG
from src.interface_adapter.http_api.decorator.log_call import log_call
import re


@defines_security(SecurityDefinition(
    item={
        "read": owns(Member.id) | owns(AbstractMember.id) | is_admin(),
        "admin": is_admin(),
        "profile": has_any_role([Roles.USER]),
        "password": owns(Member.id) | is_admin(),
        "membership": owns(Member.id) | is_admin(),
        "create": owns(Member.id) | is_admin(),
        "update": owns(Member.id) | is_admin(),
        "delete": is_admin()
    },
    collection={
        "read": owns(Member.id) | is_admin(),
        "create": owns(Member.id) | is_admin(),
        "membership": owns(Member.id) | is_admin()
    }
))
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
    @uses_security("profile", is_collection=False)
    def get_profile(self, ctx) -> Tuple[AbstractMember, List[str]]:
        user: User = ctx.get(CTX_ADMIN)
        m = self.member_repository.get_by_id(ctx,user.id)
        if not m:
            raise UnauthorizedError("Not authorize to access this profile")
        return m, [r.removeprefix("adh6_") for r in user.roles if (r in Roles._value2member_map_ and r != Roles.USER.value)]

    @log_call
    @auto_raise
    @uses_security("create", is_collection=True)
    def new_member(self, ctx, member: AbstractMember) -> Member:
        LOG.debug("create_member_records", extra=log_extra(ctx, username=member.username))
        # Check that the user exists in the system.
        fetched_member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(username=member.username))
        if fetched_member:
            raise MemberAlreadyExist(fetched_member[0].username)

        fetched_account_type, _ = self.account_type_repository.search_by(ctx, filter_=AccountType(name="Adhérent"))
        if not fetched_account_type:
            raise AccountTypeNotFoundError("Adhérent") 
 
        created_member: Member = self.member_repository.create(ctx, member)
        _: Account = self.account_repository.create(ctx, AbstractAccount(
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

        _ = self.new_membership(ctx, created_member.id, Membership(
            uuid="123e4567-e89b-12d3-a456-426614174000",
            status='INITIAL',
            member=created_member.id,
        ))

        return created_member

    def __is_membership_finished(self, membership: Membership) -> bool:
        return membership is not None and (
            membership.status == MembershipStatus.CANCELLED.value or
            membership.status == MembershipStatus.ABORTED.value or
            membership.status == MembershipStatus.COMPLETE.value
        )

    @log_call
    @auto_raise
    @uses_security("update")
    def update_member(self, ctx, id: int, abstract_member: Union[AbstractMember, Member], override: bool) -> None:
        member = self.__member_not_found(ctx, id)
        if not self.__is_membership_finished(self.get_latest_membership(ctx, id)):
            raise UpdateImpossible(f'member {member.username}', 'membership not validated')

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

    
    @log_call
    @auto_raise
    @uses_security("read", is_collection=True)
    def membership_search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                          filter_: AbstractMembership = None) -> Tuple[List[Membership], int]:
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        return self._membership_search(ctx, limit=limit,
                                       offset=offset,
                                       terms=terms,
                                       filter_=filter_)

    def _membership_search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None) -> Tuple[List[Membership], int]:
        return self.membership_repository.membership_search_by(ctx, limit=limit,
                                                               offset=offset,
                                                               terms=terms,
                                                               filter_=filter_)

    @log_call
    @auto_raise
    @uses_security("read", is_collection=True)
    def get_latest_membership(self, ctx, id: int) -> Membership:
        LOG.debug("get_latest_membership_records", extra=log_extra(ctx, id=id))
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(ctx, id)
        if not member:
            raise MemberNotFoundError(id)
        
        membership = self.membership_repository.get_latest_membership(ctx, id)
        
        # All members shuld have a least 1 membership
        if membership is None:
            raise MembershipNotFoundError(id)
        LOG.debug("latest_membership_records", extra=log_extra(ctx,membership_uuid=membership.uuid))

        return membership


    @log_call
    @auto_raise
    @uses_security("create", is_collection=True)
    def new_membership(self, ctx, member_id: int, membership: Membership) -> Membership:
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

        if membership.status != MembershipStatus.INITIAL.value:
            raise MembershipStatusNotAllowed(membership.status, "status cannot be used to create a membership")

        searched_membership, _ = self.membership_repository.membership_search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractMembership(uuid=membership.uuid)
        )
        if searched_membership:
            raise MembershipAlreadyExist(membership.uuid)

        LOG.debug("create_membership_records", extra=log_extra(ctx,membership_status=membership.status))
        if membership.status == MembershipStatus.INITIAL.value:
            LOG.debug("create_membership_record_switch_status_to_pending_rules")
            membership.status = MembershipStatus.PENDING_RULES.value

        if membership.status == MembershipStatus.PENDING_RULES.value:
            date_signed_minet = self.member_repository.get_charter(ctx, member_id, 1)
            if date_signed_minet is not None and date_signed_minet != "":
                LOG.debug("create_membership_record_switch_status_to_pending_payment_initial")
                membership.status = MembershipStatus.PENDING_PAYMENT_INITIAL.value

        if membership.status == MembershipStatus.PENDING_PAYMENT_INITIAL.value:
            if membership.duration is not None and membership.duration != 0:
                if membership.duration < 0:
                    raise IntMustBePositive('duration')
                if membership.duration not in self.duration_price:
                    LOG.warning("create_membership_record_no_price_defined", extra=log_extra(ctx, duration=membership.duration))
                    raise NoPriceAssignedToThatDuration(membership.duration)
                LOG.debug("create_membership_record_switch_status_to_pending_payment")
                membership.status = MembershipStatus.PENDING_PAYMENT.value

        if membership.status == MembershipStatus.PENDING_PAYMENT.value:
            if membership.account is not None and membership.payment_method is not None:
                self.__account_not_found(ctx, membership.account)
                self.__payment_method_not_found(ctx, membership.payment_method)
                LOG.debug("create_membership_record_switch_status_to_pending_payment_validation")
                membership.status = MembershipStatus.PENDING_PAYMENT_VALIDATION.value

        try:
            membership_created = self.membership_repository.create_membership(ctx, member_id, membership)
        except UnknownPaymentMethod:
            LOG.warning("create_membership_record_unknown_payment_method", extra=log_extra(ctx, payment_method=membership.payment_method))
            raise

        LOG.info("create_membership_record", extra=log_extra(
            ctx,
            membership_uuis=membership_created.uuid,
            membership_status=membership_created.status
        ))

        return membership_created


    @log_call
    @auto_raise
    @uses_security("membership", is_collection=True)
    def change_membership(self, ctx, member_id: int, uuid: str, abstract_membership: Optional[AbstractMembership] = None) -> None:
        self.__member_not_found(ctx, member_id)
        
        membership_fetched, _ = self.membership_repository.membership_search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractMembership(uuid=uuid)
        )
        if not membership_fetched:
            raise MembershipNotFoundError(uuid)

        membership: Membership = membership_fetched[0]

        if abstract_membership is None:
            LOG.debug("patch_membership_record_no_change")
            return

        if membership.status == MembershipStatus.PENDING_RULES.value:
            date_signed_minet = self.member_repository.get_charter(ctx, member_id, 1)
            if date_signed_minet is not None and date_signed_minet != "":
                LOG.debug("create_membership_record_switch_status_to_pending_payment_initial")
                abstract_membership.status = MembershipStatus.PENDING_PAYMENT_INITIAL.value
                membership.status = MembershipStatus.PENDING_PAYMENT_INITIAL.value
            else:
                raise CharterNotSigned(str(member_id))


        if abstract_membership.duration is not None and abstract_membership.duration != 0:
            if abstract_membership.duration < 0:
                raise IntMustBePositive('duration')
            if abstract_membership.duration not in self.duration_price:
                LOG.warning("create_membership_record_no_price_defined", extra=log_extra(ctx, duration=abstract_membership.duration))
                raise NoPriceAssignedToThatDuration(abstract_membership.duration)

        if membership.status == MembershipStatus.PENDING_PAYMENT_INITIAL.value:
            if abstract_membership.duration is not None:
                LOG.debug("create_membership_record_switch_status_to_pending_payment")
                abstract_membership.status = MembershipStatus.PENDING_PAYMENT.value
                membership.status = MembershipStatus.PENDING_PAYMENT.value

        if abstract_membership.account is not None:
            self.__account_not_found(ctx, abstract_membership.account)
        if abstract_membership.payment_method is not None:
            self.__payment_method_not_found(ctx, abstract_membership.payment_method)

        if membership.status == MembershipStatus.PENDING_PAYMENT.value:
            if abstract_membership.account is not None and abstract_membership.payment_method is not None:
                LOG.debug("create_membership_record_switch_status_to_pending_payment_validation")
                abstract_membership.status = MembershipStatus.PENDING_PAYMENT_VALIDATION.value
                membership.status = MembershipStatus.PENDING_PAYMENT_VALIDATION.value

        if membership.status == MembershipStatus.COMPLETE.value or membership.status == MembershipStatus.CANCELLED.value or membership.status == MembershipStatus.ABORTED.value:
            raise MembershipStatusNotAllowed(membership.status, "membership already completed, cancelled or aborted")

        try:
            updated_membership = self.membership_repository.update_membership(ctx, member_id, uuid, abstract_membership)
            LOG.info("patch_membership_record", extra=log_extra(
                ctx,
                membership_uuis=updated_membership.uuid,
                membership_status=updated_membership.status
            ))
        except Exception:
            raise


    @log_call
    @auto_raise
    def validate_membership(self, ctx, member_id: int, uuid: str):
        member = self.__member_not_found(ctx, member_id)

        fethed_membership, _ = self.membership_repository.membership_search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractMembership(uuid=uuid)
        )
        if not fethed_membership:
            raise MembershipNotFoundError(uuid)
        if fethed_membership[0].status != MembershipStatus.PENDING_PAYMENT_VALIDATION.value:
            raise MembershipStatusNotAllowed(fethed_membership[0].status, "status cannot be used to validate a membership")

        @uses_security("admin", is_collection=False)
        def _validate(cls, ctx, membership_uuid: str) -> None:
            self.membership_repository.validate_membership(ctx, membership_uuid)

            membership = fethed_membership[0]
            payment_method = self.__payment_method_not_found(ctx, membership.payment_method)
            LOG.debug("membership_patch_transaction", extra=log_extra(ctx, duration=membership.duration, membership_accoun=membership.account, products=membership.products))
            price = self.duration_price[int(membership.duration)]  # Expressed in EUR.
            if price == 50 and not membership.has_room:
                price = 9
            price_in_cents = price * 100  # Expressed in cents of EUR.
            duration_str = self.duration_string.get(int(membership.duration), '')
            title = f'Internet - {duration_str}'
            self.transaction_repository.add_member_payment_record(ctx, price_in_cents, title, member.username, payment_method.name, membership.uuid)
            self.transaction_repository.add_products_payment_record(ctx, member_id, membership.products, payment_method.name, membership_uuid)
            self.member_repository.add_duration(ctx, member_id, membership.duration)
            self.update_subnet(ctx, member_id)

        return _validate(self, ctx, uuid)


    def __account_not_found(self, ctx, account: int) -> None:
        _account, _ = self.account_repository.search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractAccount(id=account)
        )
        if not _account:
            raise AccountNotFoundError(str(account))

    def __payment_method_not_found(self, ctx, payment_method: int) -> PaymentMethod:
        _payment_method, _ = self.payment_method_repository.search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractPaymentMethod(id=payment_method)
        )
        if not _payment_method or len(_payment_method) == 0:
            raise PaymentMethodNotFoundError(str(payment_method))
        return _payment_method[0]
    
    def __member_not_found(self, ctx, member: int) -> Member:
        _member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member))
        if not _member:
            raise MemberNotFoundError(str(member))
        
        return _member[0]

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

        member = member[0]

        @uses_security("admin", is_collection=False)
        def _get_logs(cls, ctx, filter_: AbstractMember):
            # Do the actual log fetching.
            try:
                devices = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=filter_.id))[0]
                logs = self.logs_repository.get_logs(ctx, username=filter_.username, devices=devices, dhcp=dhcp)

                return list(map(
                    lambda x: "{} {}".format(x[0], x[1]),
                    logs
                ))

            except LogFetchError:
                LOG.warning("log_fetch_failed", extra=log_extra(ctx, username=filter_.username))
                return []  # We fail open here.

        return _get_logs(self, ctx, filter_=member)

    @log_call
    @auto_raise
    def get_statuses(self, ctx, member_id) -> List[MemberStatus]:
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)

        member = member[0]

        @uses_security("read", is_collection=False)
        def _get_statuses(cls, ctx, filter_=None):
            # Do the actual log fetching.
            try:
                devices = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=filter_))[0]
                logs = self.logs_repository.get_logs(ctx, username=filter_.username, devices=devices, dhcp=False)
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
                        login, mac = match.group(1), match.group(2).upper()
                        if login != filter_.username:
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
                    for status, object in statuses.items():
                        if mac in last_ok_login_mac and object.last_timestamp < last_ok_login_mac[mac]:
                            continue
                        all_statuses.append(object)
                return all_statuses

            except LogFetchError:
                LOG.warning("log_fetch_failed", extra=log_extra(ctx, username=filter_.username))
                return []  # We fail open here.

        return _get_statuses(self, ctx, filter_=member)

    @log_call
    def change_password(self, ctx, member_id, password=None, hashed_password=None):
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)

        member = member[0]

        @uses_security("password", is_collection=False)
        def _change_password(cls, ctx, filter_=None):
            from binascii import hexlify
            import hashlib

            pw = hashed_password or hexlify(hashlib.new('md4', password.encode('utf-16le')).digest())

            self.member_repository.update_password(ctx, member_id, pw)

            return True

        return _change_password(self, ctx, filter_=member)

    @log_call
    @auto_raise
    @uses_security("profile", is_collection=False)
    def update_charter(self, ctx, member_id, charter_id: int) -> None:
        self.member_repository.update_charter(ctx, member_id, charter_id)

    @log_call
    @auto_raise
    @uses_security("profile", is_collection=False)
    def get_charter(self, ctx, member_id, charter_id: int) -> str:
        return self.member_repository.get_charter(ctx, member_id, charter_id)

    @log_call
    @auto_raise
    @uses_security("admin", is_collection=False)
    def update_subnet(self, ctx, member_id) -> Tuple[IPv4Network, IPv4Address]:
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
    @uses_security("admin", is_collection=False)
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
