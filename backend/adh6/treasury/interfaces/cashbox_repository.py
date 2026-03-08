"""
Treasury repository.
"""

import abc

from adh6.entity.abstract_transaction import AbstractTransaction


class CashboxRepository(abc.ABC):
    """
    Abstract interface to handle the cashbox.
    """

    @abc.abstractmethod
    async def get(self) -> tuple[int, int]:
        """
        Get the current value
        """
        # pragma: no cover

    @abc.abstractmethod
    async def update(self, value_modifier: int, transaction: AbstractTransaction):
        """
        Add or remove value
        """
        # pragma: no cover
