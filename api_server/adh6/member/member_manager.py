# coding=utf-8
import typing as t
from ipaddress import IPv4Address, IPv4Network

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, SUBNET_PUBLIC_ADDRESSES_WIRELESS
from adh6.entity import (
    AbstractMember, Member,
    Account, 
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
    UpdateImpossible,
)
from adh6.device import DeviceIpManager
from adh6.default import CRUDManager
from adh6.decorator import log_call
from adh6.treasury import AccountManager, AccountTypeManager

from .enums import MembershipStatus
from .mailinglist_manager import MailinglistManager
from .interfaces import MemberRepository
from .subscription_manager import SubscriptionManager


class MemberManager(CRUDManager):
    def __init__(self, member_repository: MemberRepository,
                 account_manager: AccountManager,
                 account_type_manager: AccountTypeManager,
                 device_ip_manager: DeviceIpManager,
                 mailinglist_manager: MailinglistManager, subscription_manager: SubscriptionManager):
        super().__init__(member_repository, MemberNotFoundError)
        self.member_repository = member_repository
        self.mailinglist_manager = mailinglist_manager
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
    def get_profile(self) -> t.Tuple[Member, t.List[str]]:
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

        _ = self.account_manager.update_or_create(Account(
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
    def change_password(self, member_id, password: str, hashed_password):
        # Check that the user exists in the system.
        member = self.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)

        from binascii import hexlify
        import hashlib

        pw = hashed_password or hexlify(hashlib.new('md4', password.encode('utf-16le')).digest())

        self.member_repository.update_password(member_id, pw)

        return True

    @log_call
    def update_subnet(self, member: Member) -> t.Optional[t.Tuple[IPv4Network, t.Union[IPv4Address, None]]]:
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

        member = self.member_repository.update(AbstractMember(id=member.id, subnet=str(subnet), ip=str(ip)))

        self.device_ip_manager.allocate_ips(member, device_type="wireless")

        return subnet, ip

    @log_call
    def reset_member(self, member: Member) -> None:
        self.member_repository.update(AbstractMember(
            id=member.id,
            ip="", 
            subnet=""
        ))

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
