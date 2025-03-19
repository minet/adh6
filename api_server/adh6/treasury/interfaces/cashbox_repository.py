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
    def get(self) -> tuple[int, int]:
        """
        Get the current value
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, value_modifier: int, transaction: AbstractTransaction):
        """
        Add or remove value
        """
        pass  # pragma: no cover
