# coding=utf-8
""" Use cases (business rule layer) of everything related to members. """
import datetime
from typing import List, Union, Optional

from src.constants import CTX_ADMIN, CTX_ROLES, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractMember, AbstractDevice, MemberStatus, Member, Admin, PaymentMethod, Membership, \
    AbstractMembership
from src.entity.roles import Roles
from src.exceptions import InvalidAdmin, UnknownPaymentMethod, LogFetchError, NoPriceAssignedToThatDuration, \
    MemberNotFoundError, IntMustBePositive, UnauthorizedError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Account
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.logs_repository import LogsRepository
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.use_case.interface.money_repository import MoneyRepository
from src.util.context import log_extra
from src.util.date import string_to_date
from src.util.log import LOG
import re


@defines_security(SecurityDefinition(
    item={
        "read": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "admin": Roles.ADH6_ADMIN,
        "profile": Roles.ADH6_USER,
        "password": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "create": (Member.id == Admin.member) | Roles.ADH6_ADMIN
    },
    collection={
        "read": (Member.id == Admin.member) | Roles.ADH6_ADMIN,
        "create": (Member.id == Admin.member) | Roles.ADH6_ADMIN
    }
))
class MemberManager(CRUDManager):
    """
    Implements all the use cases related to member management.
    """

    def __init__(self, member_repository: MemberRepository, membership_repository: MembershipRepository,
                 logs_repository: LogsRepository, money_repository: MoneyRepository,
                 device_repository: DeviceRepository, configuration):
        super().__init__("member", member_repository, AbstractMember, MemberNotFoundError)
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.logs_repository = logs_repository
        self.money_repository = money_repository
        self.device_repository = device_repository
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
    @uses_security("read", is_collection=True)
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: AbstractMembership=None) -> (list, int):
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        return self._search(ctx, limit=limit,
                            offset=offset,
                            terms=terms,
                            filter_=filter_)

    def _search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None) -> (list, int):
        return self.membership_repository.membership_search_by(ctx, limit=limit,
                                         offset=offset,
                                         terms=terms,
                                         filter_=filter_)

    def new_membership(self, ctx, member_id: int, abstract_membership: AbstractMembership) -> Membership:
        """
        Core use case of ADH. Registers a membership.

        User story: As an admin, I can create a new membership record, so that a member can have internet access.
        :param ctx: context
        :param member_id: member_id
        :param abstract_membership: entity AbstractMembership

        :raise IntMustBePositiveException
        :raise NoPriceAssignedToThatDurationException
        :raise MemberNotFound
        :raise InvalidAdmin
        :raise UnknownPaymentMethod
        """

        if abstract_membership.duration is not None:
            if abstract_membership.duration < 0:
                raise IntMustBePositive('duration')
            if abstract_membership.duration not in self.config.PRICES:
                LOG.warning("create_membership_record_no_price_defined", extra=log_extra(ctx,
                                                                                         duration=abstract_membership.duration))
                raise NoPriceAssignedToThatDuration(abstract_membership.duration)

        start = datetime.datetime.now().isoformat()

        membership_created: Optional[Membership] = None
        # TODO check price.
        try:
            membership_created = self.membership_repository.create_membership(ctx, member_id, abstract_membership)

            # TODO: Check the member has signed before setting-up the transaction
            # TODO: if first-time and no account create an account

            """
            price = self.config.PRICES[membership.duration]  # Expressed in EUR.
            price_in_cents = price * 100  # Expressed in cents of EUR.
            duration_str = self.config.DURATION_STRING.get(membership.duration, '')
            title = f'Internet - {duration_str}'
            self.money_repository.add_member_payment_record(ctx, price_in_cents, title,
                                                            membership_created.member.username,
                                                            membership_created.payment_method)
            """

        except InvalidAdmin:
            LOG.warning("create_membership_record_admin_not_found", extra=log_extra(ctx))
            raise

        except UnknownPaymentMethod:
            LOG.warning("create_membership_record_unknown_payment_method",
                        extra=log_extra(ctx, payment_method=abstract_membership.payment_method))
            raise

        LOG.info("create_membership_record", extra=log_extra(
            ctx,
            membership_uuis=membership_created.uuid,
            start_date=abstract_membership.created_at.datetime.isoformat()
        ))

        return membership_created

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
                    if status not in device_to_statuses[mac] or device_to_statuses[mac][status].last_timestamp < timestamp:
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
                        match = re.search(r'.*?EAP sub-module failed\):\s*\[(.*?)\].*?cli ([a-f0-9\-]+)\).*', prev_log[1])
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
    @uses_security("read", is_collection=False)
    def get_charter(self, ctx, member_id: int, charter_id: int) -> str:
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(str(member_id))

        return str(self.member_repository.get_charter(ctx, member_id, charter_id))

    @log_call
    @auto_raise
    @uses_security("create", is_collection=False)
    def put_charter(self, ctx, member_id: int, charter_id: int):
        # Check that the user exists in the system.
        member, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(id=member_id))
        if not member:
            raise MemberNotFoundError(str(member_id))

        self.member_repository.update_charter(ctx, member_id, charter_id)