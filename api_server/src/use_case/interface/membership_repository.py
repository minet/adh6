# coding=utf-8
"""
Membership repository.
"""
import abc
from typing import List, Optional, Tuple

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Membership, AbstractMembership

# TODO: This class should be derive from CRUDRepository
class MembershipRepository(abc.ABC):
    """
    Abstract interface to handle memberships.
    """

    @abc.abstractmethod
    def create_membership(self, ctx, member_id: int, membership: Membership) -> Membership:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_membership(self, ctx, member_id: int, membership_uuid: str, abstract_membership: AbstractMembership) -> Membership:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def membership_search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractMembership] = None) -> Tuple[List[Membership], int]:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_latest_membership(self, ctx, member_id: int) -> Optional[Membership]:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def validate_membership(self, ctx, membership_uuid: str) -> None:
        """
        Add a membership.
        """
        pass  # pragma: no cover
