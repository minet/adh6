# coding=utf-8
"""
Treasury repository.
"""
import abc
from typing import Tuple

from adh6.entity.abstract_transaction import AbstractTransaction

class CashboxRepository(abc.ABC):
    """
    Abstract interface to handle the cashbox.
    """

    @abc.abstractmethod
    def get(self) -> Tuple[int, int]:
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

