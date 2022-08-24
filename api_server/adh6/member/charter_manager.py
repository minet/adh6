from datetime import datetime
from typing import List, Tuple, Union
from adh6.constants import MembershipStatus
from adh6.entity.abstract_membership import AbstractMembership
from adh6.entity.subscription_body import SubscriptionBody
from adh6.exceptions import MemberNotFoundError, MembershipNotFoundError
from adh6.member.interfaces.charter_repository import CharterRepository
from adh6.member.interfaces.member_repository import MemberRepository
from adh6.member.interfaces.membership_repository import MembershipRepository


class CharterManager:
    def __init__(self, charter_repository: CharterRepository, member_repository: MemberRepository, membership_repository: MembershipRepository) -> None:
        self.charter_repository = charter_repository
        self.member_repository = member_repository
        self.membership_repository = membership_repository

    def get(self, ctx, charter_id: int, member_id: int) -> Union[datetime, None]:
        m = self.member_repository.get_by_id(ctx, member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return self.charter_repository.get(ctx, charter_id, member_id)

    def sign(self, ctx, charter_id: int, member_id: int):
        m = self.member_repository.get_by_id(ctx, member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        subscriptions, _ = self.membership_repository.search(ctx, limit=1, filter_=AbstractMembership(member=member_id, status=MembershipStatus.PENDING_RULES.value))
        if not subscriptions:
            raise MembershipNotFoundError(member_id)
        self.charter_repository.update(ctx, charter_id, member_id)
        if subscriptions[0].status == MembershipStatus.PENDING_RULES.value:
            self.membership_repository.update(ctx, subscriptions[0].uuid, SubscriptionBody(), MembershipStatus.PENDING_PAYMENT_INITIAL)

    def get_members(self, ctx, charter_id: int) -> Tuple[List[int], int]:
        return self.charter_repository.get_members(ctx, charter_id)
