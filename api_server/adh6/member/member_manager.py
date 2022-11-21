# coding=utf-8
import re
from datetime import datetime
from ipaddress import IPv4Address, IPv4Network
from typing import List, Optional, Tuple, Union

from adh6.constants import CTX_ADMIN, CTX_ROLES, DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus, SUBNET_PUBLIC_ADDRESSES_WIRELESS
from adh6.entity import (
    AbstractMember, Member,
    MemberStatus,
    AbstractAccount,
    MemberFilter,
    MemberBody,
    Comment,
)
from adh6.entity.validators.member_validators import is_member_active
from adh6.exceptions import (
    AccountTypeNotFoundError,
    NoSubnetAvailable,
    MemberNotFoundError,
    MemberAlreadyExist,
    LogFetchError,
    UpdateImpossible,
)
from adh6.device.interfaces.device_repository import DeviceRepository
from adh6.device.device_manager import DeviceManager
from adh6.default.crud_manager import CRUDManager
from adh6.decorator import log_call
from adh6.misc import LOG, log_extra
from adh6.treasury.interfaces import AccountRepository, AccountTypeRepository

from .interfaces import LogsRepository, MailinglistRepository, MemberRepository
from .subscription_manager import SubscriptionManager


class MemberManager(CRUDManager):
    def __init__(self, member_repository: MemberRepository,
                 logs_repository: LogsRepository,
                 device_repository: DeviceRepository, account_repository: AccountRepository,
                 account_type_repository: AccountTypeRepository,
                 device_manager: DeviceManager, mailinglist_repository: MailinglistRepository, subscription_manager: SubscriptionManager):
        super().__init__(member_repository, MemberNotFoundError)
        self.member_repository = member_repository
        self.mailinglist_repository = mailinglist_repository
        self.logs_repository = logs_repository
        self.device_repository = device_repository
        self.account_repository = account_repository
        self.account_type_repository = account_type_repository
        self.device_manager = device_manager
        self.subscription_manager = subscription_manager

    @log_call
    def search(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: str = "", filter_: Union[MemberFilter, None] = None) -> Tuple[List[int], int]:
        result, count = self.member_repository.search_by(
            ctx, 
            limit=limit,
            offset=offset,
            terms=terms,
            filter_=filter_
        )
        return [r.id for r in result if r.id], count

    @log_call
    def get_by_id(self, ctx, id: int) -> Member:
        member = self.member_repository.get_by_id(ctx, id)
        if not member:
            raise MemberNotFoundError(id)

        latest_sub = self.subscription_manager.latest(ctx, id)
        member.membership = latest_sub.status if latest_sub else MembershipStatus.INITIAL.value
        return member

    @log_call
    def get_by_login(self, ctx, login: str):
        member = self.member_repository.get_by_login(ctx, login) 
        if not member or not member.id:
            raise MemberNotFoundError(id)
        latest_sub = self.subscription_manager.latest(ctx, member.id)
        member.membership = latest_sub.status if latest_sub else MembershipStatus.INITIAL.value
        return member

    @log_call
    def get_profile(self, ctx) -> Tuple[AbstractMember, List[str]]:
        user = ctx.get(CTX_ADMIN)
        m = self.member_repository.get_by_id(ctx, user)
        if not m:
            raise MemberNotFoundError(id)
        return m, ctx.get(CTX_ROLES)

    @log_call
    def create(self, ctx, body: MemberBody) -> Member:
        LOG.debug("create_member_records", extra=log_extra(ctx, username=body.username))
        # Check that the user exists in the system.
        fetched_member = self.member_repository.get_by_login(ctx, body.username)
        if fetched_member:
            raise MemberAlreadyExist(fetched_member.username)

        fetched_account_type, _ = self.account_type_repository.search_by(ctx, terms="Adhérent")
        if not fetched_account_type:
            raise AccountTypeNotFoundError("Adhérent") 
 
        created_member = self.member_repository.create(
            ctx=ctx, 
            object_to_create=AbstractMember(
                id=0,
                username=body.username,
                first_name=body.first_name,
                last_name=body.last_name,
                email=body.mail,
                departure_date=datetime.now(),
                ip='',
                subnet='',
                comment='',
                membership=MembershipStatus.INITIAL.value
            )
        )

        self.mailinglist_repository.update_from_member(ctx, created_member.id, 249)

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

        _ = self.subscription_manager.create(
            ctx=ctx, 
            member_id=created_member.id, 
            body=SubscriptionBody(
                member=created_member.id
            ),
        )

        return created_member

    @log_call
    def update(self, ctx, id: int, body: MemberBody) -> None:
        member = self.member_repository.get_by_id(ctx, id)
        if not member:
            raise MemberNotFoundError(id)

        latest_sub = self.subscription_manager.latest(ctx, id)
        if not latest_sub or latest_sub.status not in [
            MembershipStatus.CANCELLED.value,
            MembershipStatus.ABORTED.value,
            MembershipStatus.COMPLETE.value
        ]:
            raise UpdateImpossible(f'member {member.username}', 'membership not validated')

        member = self.member_repository.update(ctx, AbstractMember(
                                                   id=id,
                                                   email=body.mail,
                                                   username=body.username,
                                                   first_name=body.first_name,
                                                   last_name=body.last_name
                                               ))

    @log_call
    def get_logs(self, ctx, member_id, dhcp=False) -> List[str]:
        """
        User story: As an admin, I can retrieve the logs of a member, so I can help him troubleshoot their connection
        issues.

        :raise MemberNotFound
        """
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(ctx, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        # Do the actual log fetching.
        try:
            devices = self.device_repository.search_by(ctx, limit=100, offset=0, device_filter=DeviceFilter(member=member.id))[0]
            logs = self.logs_repository.get_logs(ctx, username=member.username, devices=devices, dhcp=dhcp)

            return list(map(
                lambda x: "{} {}".format(x[0], x[1]),
                logs
            ))

        except LogFetchError:
            LOG.warning("log_fetch_failed", extra=log_extra(ctx, username=member.username))
            return []  # We fail open here.


    @log_call
    def get_statuses(self, ctx, member_id) -> List[MemberStatus]:
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(ctx, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        # Do the actual log fetching.
        try:
            devices = self.device_repository.search_by(ctx, limit=100, offset=0, device_filter=DeviceFilter(member=member.id))[0]
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
        member = self.member_repository.get_by_id(ctx, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        from binascii import hexlify
        import hashlib

        pw = hashed_password or hexlify(hashlib.new('md4', password.encode('utf-16le')).digest())

        self.member_repository.update_password(ctx, member_id, pw)

        return True

    @log_call
    def update_subnet(self, ctx, member_id) -> Optional[Tuple[IPv4Network, Union[IPv4Address, None]]]:
        member = self.member_repository.get_by_id(ctx, member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        if not is_member_active(ctx, member):
            return

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

        member = self.member_repository.update(ctx, AbstractMember(id=member_id, subnet=str(subnet), ip=str(ip)))

        self.device_manager.allocate_wireless_ips(ctx, member_id, str(subnet))

        return subnet, ip

    @log_call
    def reset_member(self, ctx, member_id: int) -> None:
        self.member_repository.update(ctx, AbstractMember(
            id=member_id,
            ip="", 
            subnet=""
        ))
        self.device_manager.unallocate_ip_addresses(ctx, member_id)

    @log_call
    def ethernet_vlan_changed(self, ctx, member_id: int, vlan_number: int):
        member = self.get_by_id(ctx, id=member_id)
        self.device_manager.allocate_new_vlan_ips(ctx, member_id=member_id, wireless_subnet=member.subnet if member.subnet else "", vlan_number=vlan_number)

    @log_call
    def change_comment(self, ctx, member_id: int, comment: Comment) -> None:
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(ctx, member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        self.member_repository.update_comment(ctx, member_id, comment.comment)
    
    def get_comment(self, ctx, member_id: int) -> Comment:
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(ctx, member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        return Comment(member.comment if member.comment else "")