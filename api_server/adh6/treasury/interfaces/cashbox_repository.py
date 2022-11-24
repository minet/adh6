# coding=utf-8
"""
Treasury repository.
"""
import abc
import typing as t

from adh6.entity import AbstractTransaction

class CashboxRepository(abc.ABC):
    """
    Abstract interface to handle the cashbox.
    """

    @abc.abstractmethod
    def get(self) -> t.Tuple[int, int]:
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

