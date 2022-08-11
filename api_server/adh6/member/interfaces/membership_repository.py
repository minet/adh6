# coding=utf-8
"""
Membership repository.
"""
import abc
from typing import List, Optional, Tuple

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, MembershipStatus
from adh6.entity import Membership, AbstractMembership, SubscriptionBody

# TODO: This class should be derive from CRUDRepository
class MembershipRepository(abc.ABC):
    """
    Abstract interface to handle memberships.
    """

    @abc.abstractmethod
    def create(self, ctx, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, ctx, uuid: str, body: SubscriptionBody, state: MembershipStatus):
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractMembership] = None) -> Tuple[List[Membership], int]:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def validate(self, ctx, uuid: str) -> None:
        """
        Add a membership.
        """
        pass  # pragma: no cover
