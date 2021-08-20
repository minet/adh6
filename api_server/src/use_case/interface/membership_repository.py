# coding=utf-8
"""
Membership repository.
"""
import abc
from typing import List

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Membership, AbstractMembership


class MembershipRepository(metaclass=abc.ABCMeta):
    """
    Abstract interface to handle memberships.
    """

    @abc.abstractmethod
    def create_membership(self, ctx, username, start, end):
        """
        Add a membership.
        """
        pass  # pragma: no cover

    def membership_search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractMembership = None) -> (List[Membership], int):
        """
        Add a membership.
        """
        pass  # pragma: no cover