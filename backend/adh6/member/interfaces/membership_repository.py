"""
Membership repository.
"""

import abc

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from adh6.entity import AbstractMembership, Membership, SubscriptionBody


# TODO: This class should be derive from CRUDRepository
class MembershipRepository(abc.ABC):
    """
    Abstract interface to handle memberships.
    """

    @abc.abstractmethod
    async def create(self, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        """
        Add a membership.
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update(self, uuid: str, body: SubscriptionBody, state: MembershipStatus):
        """
        Add a membership.
        """
        # pragma: no cover

    @abc.abstractmethod
    async def search(
        self,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        terms=None,
        filter_: AbstractMembership | None = None,
    ) -> tuple[list[Membership], int]:
        """
        Add a membership.
        """
        # pragma: no cover

    @abc.abstractmethod
    async def validate(self, uuid: str) -> None:
        """
        Add a membership.
        """
        # pragma: no cover
