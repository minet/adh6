import datetime
import typing as t

from adh6.entity import AbstractMembership, SubscriptionBody
from adh6.exceptions import MemberNotFoundError, MembershipNotFoundError
from . import MembershipStatus
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
        subscriptions, _ = self.membership_repository.search(limit=1, filter_=AbstractMembership(member=member_id, status=MembershipStatus.PENDING_RULES.value))
        if not subscriptions:
            raise MembershipNotFoundError(member_id)
        self.charter_repository.update(charter_id, member_id)
        if subscriptions[0].status == MembershipStatus.PENDING_RULES.value:
            self.membership_repository.update(subscriptions[0].uuid, SubscriptionBody(), MembershipStatus.PENDING_PAYMENT_INITIAL)

    def get_members(self, charter_id: int) -> t.Tuple[t.List[int], int]:
        return self.charter_repository.get_members(charter_id)
