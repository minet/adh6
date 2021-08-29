# coding=utf-8
""" Use cases (business rule layer) of everything related to members. """
from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.entity.account_type import AccountType
from typing import List, Optional, Tuple, Union

from src.constants import CTX_ADMIN, CTX_ROLES, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from src.entity import AbstractMember, AbstractDevice, MemberStatus, Member, Admin, PaymentMethod, Membership, \
    AbstractMembership, AbstractAccount, AbstractTransaction, Account
from src.entity.roles import Roles
from src.exceptions import AccountTypeNotFoundError, InvalidAdmin, MemberAlreadyExist, UnknownPaymentMethod, LogFetchError, NoPriceAssignedToThatDuration, \
    MemberNotFoundError, IntMustBePositive, MembershipStatusNotAllowed, AccountNotFoundError, \
    PaymentMethodNotFoundError, MembershipAlreadyExist, MembershipNotFoundError, CharterNotSigned
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.use_case.interface.account_repository import AccountRepository
from src.use_case.interface.account_type_repository import AccountTypeRepository
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.logs_repository import LogsRepository
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.use_case.interface.money_repository import MoneyRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.util.context import log_extra
from src.util.log import LOG
import re


@defines_security(SecurityDefinition(
    item={
        "read": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "admin": Roles.ADH6_ADMIN,
        "profile": Roles.ADH6_USER,
        "password": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "membership": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "create": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "update": (Member.id == Admin.member) | Roles.ADH6_ADMIN
    },
    collection={
        "read": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "create": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "membership": (Member.id == Admin.member) | Roles.ADH6_ADMIN
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
                 configuration):
        super().__init__("member", member_repository, AbstractMember, MemberNotFoundError)
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.logs_repository = logs_repository
        self.device_repository = device_repository
        self.payment_method_repository = payment_method_repository
        self.account_repository = account_repository
        self.account_type_repository = account_type_repository
        self.transaction_repository = transaction_repository
        self.config = configuration

    @log_call
    @auto_raise
    @uses_security("profile", is_collection=False)
    def get_profile(self, ctx):
        admin = ctx.get(CTX_ADMIN)
        roles = ctx.get(CTX_ROLES)

        return admin, roles

    @log_call
    @auto_raise
    @uses_security("create", is_collection=True)
    def new_member(self, ctx, member: Member) -> Member:
        LOG.debug("create_member_records", extra=log_extra(ctx, username=member.username))
        # Check that the user exists in the system.
        fetched_member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(username=member.username))
        if fetched_member:
            raise MemberAlreadyExist(fetched_member[0].username)

        fetched_account_type, _ = self.account_type_repository.search_by(ctx, filter_=AccountType(name="Adhérent"))
        if not fetched_account_type:
            raise AccountTypeNotFoundError("Adhérent")
        created_member: Member = self.member_repository.create(ctx, member)
        _: Account = self.account_repository.create(ctx, Account(
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
    def get_latest_membership(self, ctx, member_id: int) -> Membership:
        LOG.debug("get_latest_membership_records", extra=log_extra(ctx,member_id=member_id))
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)
        
        membership = self.membership_repository.get_latest_membership(ctx, member_id)
        if membership is None:
            raise MembershipNotFoundError(str(member_id))
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
        :raise InvalidAdmin
        :raise UnknownPaymentMethod
        """

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
                if membership.duration not in self.config.PRICES:
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
        except InvalidAdmin:
            LOG.warning("create_membership_record_admin_not_found", extra=log_extra(ctx))
            raise

        except UnknownPaymentMethod:
            LOG.warning("create_membership_record_unknown_payment_method",
                        extra=log_extra(ctx, payment_method=membership.payment_method))
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
    def change_membership(self, ctx, member_id: int, uuid: str, abstract_membership: Optional[AbstractMembership]) -> None:
        # Check the member and membership exist
        member: Member = self.member_repository.search_by(
            ctx=ctx,
            filter_=AbstractMember(id=member_id)
        )
        if not member:
            raise MemberNotFoundError(str(member_id))
        membership_fetched, _ = self.membership_search(
            ctx=ctx,
            limit=1,
            filter_=AbstractMembership(uuid=uuid)
        )
        if not membership_fetched:
            raise MembershipNotFoundError(uuid)

        membership: Membership = membership_fetched[0]

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
            if abstract_membership.duration not in self.config.PRICES:
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
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)
        fethed_membership, _ = self.membership_repository.membership_search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractMembership(uuid=uuid)
        )
        if not fethed_membership:
            raise MembershipNotFoundError(uuid)

        @uses_security("admin", is_collection=False)
        def _validate(cls, ctx, membership_uuid: str) -> None:
            self.membership_repository.validate_membership(ctx, membership_uuid)

            membership = fethed_membership[0]
            LOG.debug("membership_patch_transaction", extra=log_extra(ctx, duration=membership.duration, membership_accoun=membership.account, products=membership.products))
            price = self.config.PRICES[int(membership.duration)]  # Expressed in EUR.
            price_in_cents = price * 100  # Expressed in cents of EUR.
            duration_str = self.config.DURATION_STRING.get(int(membership.duration), '')
            title = f'Internet - {duration_str}'
            self.transaction_repository.add_member_payment_record(ctx, price_in_cents, title,
                                                                membership.member.username,
                                                                membership.payment_method.name)
            self.transaction_repository.add_products_payment_record(ctx, member_id, membership.products, membership.payment_method.name)
            self.member_repository.add_duration(ctx, member_id, membership.duration)

        return _validate(self, ctx, uuid)


    def __account_not_found(self, ctx, account: Union[int, Account]) -> None:
        if isinstance(account, Account):
            account = account.id
        _account, _ = self.account_repository.search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractAccount(id=account)
        )
        if not _account:
            raise AccountNotFoundError(str(account))

    def __payment_method_not_found(self, ctx, payment_method: Union[int, PaymentMethod]) -> None:
        if isinstance(payment_method, PaymentMethod):
            payment_method = payment_method.id
        _payment_method, _ = self.payment_method_repository.search_by(
            ctx=ctx,
            limit=1,
            filter_=AbstractTransaction(id=payment_method)
        )
        if not _payment_method:
            raise PaymentMethodNotFoundError(str(payment_method))

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
        # q = s.query(all_devices, Adherent.login.label("login"))
        # q = q.join(Adherent, Adherent.id == all_devices.columns.adherent_id)
        # q = q.filter(Adherent.login == username)
        # mac_tbl = list(map(lambda x: x.mac, q.all()))

        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(member_id)

        member = member[0]

        @uses_security("admin", is_collection=False)
        def _get_logs(cls, ctx, filter_=None):
            # Do the actual log fetching.
            try:
                devices = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=filter_))[0]
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
        #TODO: Update of the membership here instead of in the member_repository
        self.member_repository.update_charter(ctx, member_id, charter_id)

    @log_call
    @auto_raise
    @uses_security("profile", is_collection=False)
    def get_charter(self, ctx, member_id, charter_id: int) -> str:
        return self.member_repository.get_charter(ctx, member_id, charter_id)
