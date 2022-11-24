# coding=utf-8
import re
import logging
import typing as t
from ipaddress import IPv4Address, IPv4Network

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, SUBNET_PUBLIC_ADDRESSES_WIRELESS
from adh6.entity import (
    AbstractMember, Member,
    MemberStatus,
    AbstractAccount, 
    MemberBody, 
    MemberFilter, 
    SubscriptionBody,
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
from adh6.device import DeviceIpManager, DeviceLogsManager
from adh6.default import CRUDManager
from adh6.decorator import log_call
from adh6.treasury import AccountManager, AccountTypeManager

from . import MembershipStatus
from .mailinglist_manager import MailinglistManager
from .interfaces import MemberRepository
from .subscription_manager import SubscriptionManager


class MemberManager(CRUDManager):
    def __init__(self, member_repository: MemberRepository,
                 account_manager: AccountManager,
                 account_type_manager: AccountTypeManager,
                 device_ip_manager: DeviceIpManager, device_logs_manager: DeviceLogsManager,
                 mailinglist_manager: MailinglistManager, subscription_manager: SubscriptionManager):
        super().__init__(member_repository, MemberNotFoundError)
        self.member_repository = member_repository
        self.mailinglist_manager = mailinglist_manager
        self.device_logs_manager = device_logs_manager
        self.device_ip_manager = device_ip_manager
        self.account_manager = account_manager
        self.account_type_manager = account_type_manager
        self.subscription_manager = subscription_manager

    @log_call
    def search(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: str = "", filter_: t.Union[MemberFilter, None] = None) -> t.Tuple[t.List[int], int]:
        result, count = self.member_repository.search_by(
            limit=limit,
            offset=offset,
            terms=terms,
            filter_=filter_
        )
        return [r.id for r in result if r.id], count

    @log_call
    def get_by_id(self, id: int) -> Member:
        member = self.member_repository.get_by_id(id)
        if not member:
            raise MemberNotFoundError(id)

        latest_sub = self.subscription_manager.latest(id)
        member.membership = latest_sub.status if latest_sub else MembershipStatus.INITIAL.value
        return member

    @log_call
    def get_by_login(self, login: str):
        member = self.member_repository.get_by_login(login) 
        if not member or not member.id:
            raise MemberNotFoundError(login)
        latest_sub = self.subscription_manager.latest(member.id)
        member.membership = latest_sub.status if latest_sub else MembershipStatus.INITIAL.value
        return member

    @log_call
    def get_profile(self) -> t.Tuple[AbstractMember, t.List[str]]:
        from adh6.context import get_user, get_roles
        m = self.member_repository.get_by_id(get_user())
        if not m:
            raise MemberNotFoundError(id)
        return m, get_roles()

    @log_call
    def create(self, body: MemberBody) -> Member:
        # Check that the user exists in the system.
        fetched_member = self.member_repository.get_by_login(body.username)
        if fetched_member:
            raise MemberAlreadyExist(fetched_member.username)

        fetched_account_type, _ = self.account_type_manager.search(terms="Adhérent")
        if not fetched_account_type:
            raise AccountTypeNotFoundError("Adhérent") 
 
        from datetime import datetime
        created_member = self.member_repository.create(
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

        self.mailinglist_manager.update_member_mailinglist(created_member.id, 249)

        _ = self.account_manager.update_or_create(AbstractAccount(
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
            member_id=created_member.id, 
            body=SubscriptionBody(
                member=created_member.id
            ),
        )

        return created_member

    @log_call
    def update(self, id: int, body: MemberBody) -> None:
        member = self.member_repository.get_by_id(id)
        if not member:
            raise MemberNotFoundError(id)

        latest_sub = self.subscription_manager.latest(id)
        if not latest_sub or latest_sub.status not in [
            MembershipStatus.CANCELLED.value,
            MembershipStatus.ABORTED.value,
            MembershipStatus.COMPLETE.value
        ]:
            raise UpdateImpossible(f'member {member.username}', 'membership not validated')

        member = self.member_repository.update(AbstractMember(
                                                   id=id,
                                                   email=body.mail,
                                                   username=body.username,
                                                   first_name=body.first_name,
                                                   last_name=body.last_name
                                               ))

    @log_call
    def get_logs(self, member_id, dhcp=False) -> t.List[str]:
        """
        User story: As an admin, I can retrieve the logs of a member, so I can help him troubleshoot their connection
        issues.

        :raise MemberNotFound
        """
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        # Do the actual log fetching.
        try:
            logs = self.device_logs_manager.get(member=member, dhcp=dhcp)

            return list(map(
                lambda x: "{} {}".format(x[0], x[1]),
                logs
            ))

        except LogFetchError:
            logging.warning("log_fetch_failed")
            return []  # We fail open here.


    @log_call
    def get_statuses(self, member_id) -> t.List[MemberStatus]:
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        # Do the actual log fetching.
        try:
            logs = self.device_logs_manager.get(member=member, dhcp=False)
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
            logging.warning("log_fetch_failed")
            return []  # We fail open here.


    @log_call
    def change_password(self, member_id, password: str, hashed_password):
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        from binascii import hexlify
        import hashlib

        pw = hashed_password or hexlify(hashlib.new('md4', password.encode('utf-16le')).digest())

        self.member_repository.update_password(member_id, pw)

        return True

    @log_call
    def update_subnet(self, member_id) -> t.Optional[t.Tuple[IPv4Network, t.Union[IPv4Address, None]]]:
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        if not is_member_active(member):
            return

        used_wireles_public_ips = self.member_repository.used_wireless_public_ips()

        subnet = None
        ip = None
        if len(used_wireles_public_ips) < len(SUBNET_PUBLIC_ADDRESSES_WIRELESS):
            for i, s in SUBNET_PUBLIC_ADDRESSES_WIRELESS.items():
                if i not in used_wireles_public_ips:
                    subnet = s
                    ip = i
        
        if subnet is None:
            raise NoSubnetAvailable("wireless")

        member = self.member_repository.update(AbstractMember(id=member_id, subnet=str(subnet), ip=str(ip)))

        self.device_ip_manager.allocate_ips(member, device_type="wireless")

        return subnet, ip

    @log_call
    def reset_member(self, member_id: int) -> None:
        member = self.member_repository.update(AbstractMember(
            id=member_id,
            ip="", 
            subnet=""
        ))
        self.device_ip_manager.unallocate_ips(member=member)

    @log_call
    def ethernet_vlan_changed(self, member_id: int, vlan_number: int):
        member = self.get_by_id(id=member_id)
        self.device_ip_manager.allocate_ips(member=member, vlan_number=vlan_number)

    @log_call
    def change_comment(self, member_id: int, comment: Comment) -> None:
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        self.member_repository.update_comment(member_id, comment.comment)
    
    def get_comment(self, member_id: int) -> Comment:
        # Check that the user exists in the system.
        member = self.member_repository.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        return Comment(member.comment if member.comment else "")
