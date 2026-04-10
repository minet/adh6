from datetime import datetime

from adh6.constants import MembershipStatus
from adh6.entity.abstract_membership import AbstractMembership
from adh6.entity.subscription_body import SubscriptionBody
from adh6.exceptions import (
    MemberNotFoundError,
    MembershipNotFoundError,
    ValidationError,
)

from .interfaces import CharterRepository, MemberRepository, MembershipRepository


def _validate_charter_id(charter_id: int) -> None:
    """Validate that charter_id is 1 (network) or 2 (conditions)."""
    if charter_id not in (1, 2):
        raise ValidationError(f"Invalid charter_id: {charter_id}. Valid values are 1 or 2.")


class CharterManager:
    def __init__(
        self,
        charter_repository: CharterRepository,
        member_repository: MemberRepository,
        membership_repository: MembershipRepository,
    ) -> None:
        self.charter_repository = charter_repository
        self.member_repository = member_repository
        self.membership_repository = membership_repository

    async def get(self, charter_id: int, member_id: int) -> datetime | None:
        _validate_charter_id(charter_id)
        m = await self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        return await self.charter_repository.get(charter_id, member_id)

    async def sign(self, charter_id: int, member_id: int):
        _validate_charter_id(charter_id)
        m = await self.member_repository.get_by_id(member_id)
        if not m:
            raise MemberNotFoundError(member_id)
        subscriptions, _ = await self.membership_repository.search(
            limit=1,
            filter_=AbstractMembership(member=member_id, status=MembershipStatus.PENDING_RULES.value),
        )
        if not subscriptions:
            raise MembershipNotFoundError(member_id)
        await self.charter_repository.update(charter_id, member_id)
        if subscriptions[0].status == MembershipStatus.PENDING_RULES.value:
            await self.membership_repository.update(
                subscriptions[0].uuid,
                SubscriptionBody(),
                MembershipStatus.PENDING_PAYMENT_INITIAL,
            )

    async def get_members(self, charter_id: int) -> tuple[list[int], int]:
        _validate_charter_id(charter_id)
        return await self.charter_repository.get_members(charter_id)
