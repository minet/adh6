# coding=utf-8
""" Use cases (business rule layer) of everything related to members. """
import datetime
from typing import List

from src.entity import AbstractMember, AbstractDevice
from src.exceptions import InvalidAdmin, UnknownPaymentMethod, LogFetchError, NoPriceAssignedToThatDuration, \
    MemberNotFoundError, IntMustBePositive, UnauthorizedError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auth import auth_required, Roles
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.logs_repository import LogsRepository
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.membership_repository import MembershipRepository
from src.use_case.interface.money_repository import MoneyRepository
from src.util.context import log_extra
from src.util.date import string_to_date
from src.util.log import LOG


@auto_raise
def _owner_check(filter_: AbstractMember, admin_id):
    if filter_.id is not None and filter_.id != admin_id:
        raise UnauthorizedError("You may only read or write to your own profile")
    filter_.id = admin_id


class MemberManager(CRUDManager):
    """
    Implements all the use cases related to member management.
    """

    def __init__(self, member_repository: MemberRepository, membership_repository: MembershipRepository,
                 logs_repository: LogsRepository, money_repository: MoneyRepository,
                 device_repository: DeviceRepository, configuration):
        super().__init__("member", member_repository, AbstractMember, MemberNotFoundError, _owner_check)
        self.member_repository = member_repository
        self.membership_repository = membership_repository
        self.logs_repository = logs_repository
        self.money_repository = money_repository
        self.device_repository = device_repository
        self.config = configuration

    def new_membership(self, ctx, username, duration, payment_method, start_str=None) -> None:
        """
        Core use case of ADH. Registers a membership.

        User story: As an admin, I can create a new membership record, so that a member can have internet access.
        :param payment_method:
        :param ctx: context
        :param username: username
        :param duration: duration of the membership in days
        :param start_str: optional start date of the membership

        :raise IntMustBePositiveException
        :raise NoPriceAssignedToThatDurationException
        :raise MemberNotFound
        :raise InvalidAdmin
        :raise UnknownPaymentMethod
        """
        if start_str is None:
            return self.new_membership(ctx, username, duration, payment_method,
                                       start_str=datetime.datetime.now().isoformat())

        if duration < 0:
            raise IntMustBePositive('duration')

        if duration not in self.config.PRICES:
            LOG.warning("create_membership_record_no_price_defined", extra=log_extra(ctx, duration=duration))
            raise NoPriceAssignedToThatDuration(duration)

        start = string_to_date(start_str)
        end = start + datetime.timedelta(days=duration)

        # TODO check price.
        try:
            price = self.config.PRICES[duration]  # Expresed in EUR.
            price_in_cents = price * 100  # Expressed in cents of EUR.
            duration_str = self.config.DURATION_STRING.get(duration, '')
            title = f'Internet - {duration_str}'

            self.money_repository.add_member_payment_record(ctx, price_in_cents, title, username, payment_method)
            self.membership_repository.create_membership(ctx, username, start, end)

        except InvalidAdmin:
            LOG.warning("create_membership_record_admin_not_found", extra=log_extra(ctx))
            raise

        except UnknownPaymentMethod:
            LOG.warning("create_membership_record_unknown_payment_method",
                        extra=log_extra(ctx, payment_method=payment_method))
            raise

        LOG.info("create_membership_record", extra=log_extra(
            ctx,
            username=username,
            duration_in_days=duration,
            start_date=start.isoformat()
        ))

    @log_call
    @auto_raise
    @auth_required(roles=[Roles.ADH6_ADMIN])
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

        # Do the actual log fetching.
        try:
            devices = self.device_repository.search_by(ctx, filter_=AbstractDevice(member=member))[0]
            logs = self.logs_repository.get_logs(ctx, username=member.username, devices=devices, dhcp=dhcp)

            return logs

        except LogFetchError:
            LOG.warning("log_fetch_failed", extra=log_extra(ctx, username=member.username))
            return []  # We fail open here.

    @log_call
    def change_password(self, ctx, member_id, password=None, hashedPassword=None):
        from binascii import hexlify
        import hashlib

        password = hashedPassword or hexlify(hashlib.new('md4', password.encode('utf-16le')).digest())

        self.member_repository.update_password(ctx, member_id, password)

        return True
