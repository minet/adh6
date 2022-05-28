# coding=utf-8
"""
Treasury repository.
"""
import abc
from typing import Tuple

from src.entity.abstract_transaction import AbstractTransaction

class CashboxRepository(abc.ABC):
    """
    Abstract interface to handle the cashbox.
    """

    @abc.abstractmethod
    def get(self, ctx) -> Tuple[int, int]:
        """
        Get the current value
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update(self, ctx, value_modifier: int, transaction: AbstractTransaction):
        """
        Add or remove value
        """
        pass  # pragma: no cover

