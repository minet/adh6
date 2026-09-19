"""
Membership repository.
"""

import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractMembership, Membership


class MembershipRepository(CRUDRepository[Membership, AbstractMembership, str]):
    """
    Abstract interface to handle memberships.
    """

    @abc.abstractmethod
    async def validate(self, uuid: str) -> None:
        """
        Mark a membership as complete.
        """
