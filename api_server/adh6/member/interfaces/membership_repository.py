# coding=utf-8
"""
Membership repository.
"""
import abc
import typing as t

from adh6.entity import Membership, AbstractMembership, SubscriptionBody
from .. import MembershipStatus

# TODO: This class should be derive from CRUDRepository
class MembershipRepository(abc.ABC):
    """
    Abstract interface to handle memberships.
    """

    @abc.abstractmethod
    def create(self, body: SubscriptionBody, state: MembershipStatus) -> Membership:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, uuid: str, body: SubscriptionBody, state: MembershipStatus):
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def search(self, limit: int, offset: int, terms=None, filter_: t.Optional[AbstractMembership] = None) -> t.Tuple[t.List[Membership], int]:
        """
        Add a membership.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def validate(self, uuid: str) -> None:
        """
        Add a membership.
        """
        pass  # pragma: no cover
