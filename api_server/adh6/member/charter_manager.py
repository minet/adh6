import datetime
import typing as t

from adh6.entity import SubscriptionBody, Membership
from adh6.exceptions import MemberNotFoundError
from .enums import MembershipStatus
from .interfaces import CharterRepository, MemberRepository, MembershipRepository


class CharterManager:
    def __init__(self, charter_repository: CharterRepository, member_repository: MemberRepository, membership_repository: MembershipRepository) -> None:
        self.charter_repository = charter_repository
        self.member_repository = member_repository
        self.membership_repository = membership_repository

    def get(self, charter_id: int, member_id: int) -> t.Union[datetime.datetime, None]:
        m = self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return self.charter_repository.get(charter_id, member_id)

    def sign(self, charter_id: int, member_id: int):
        m = self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        subscription: t.Union[Membership, None] = next(filter(lambda x: x.status == MembershipStatus.PENDING_RULES.value, self.membership_repository.from_member(m)))
        self.charter_repository.update(charter_id, member_id)
        if subscription:
            self.membership_repository.update(subscription.uuid, SubscriptionBody(), MembershipStatus.PENDING_PAYMENT_INITIAL)

    def get_members(self, charter_id: int) -> t.Tuple[t.List[int], int]:
        return self.charter_repository.get_members(charter_id)
