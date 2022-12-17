import datetime
import typing as t

from adh6.decorator import log_call
from adh6.entity import SubscriptionBody, Membership, Member
from .enums import MembershipStatus
from .interfaces import CharterRepository, MembershipRepository


class CharterManager:
    def __init__(self, charter_repository: CharterRepository, membership_repository: MembershipRepository) -> None:
        self.charter_repository = charter_repository
        self.membership_repository = membership_repository

    @log_call
    def get(self, charter_id: int, member: Member) -> t.Union[datetime.datetime, None]:
        return self.charter_repository.get(charter_id, member.id)

    @log_call
    def sign(self, charter_id: int, member: Member):
        subscription: t.Union[Membership, None] = next(filter(lambda x: x.status == MembershipStatus.PENDING_RULES.value, self.membership_repository.from_member(member=member)))
        self.charter_repository.update(charter_id, member.id)
        if subscription:
            self.membership_repository.update(subscription.uuid, SubscriptionBody(), MembershipStatus.PENDING_PAYMENT_INITIAL)

    @log_call
    def get_members(self, charter_id: int) -> t.Tuple[t.List[int], int]:
        return self.charter_repository.get_members(charter_id)
