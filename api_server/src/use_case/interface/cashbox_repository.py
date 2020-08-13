# coding=utf-8
"""
Treasury repository.
"""
import abc


class CashboxRepository(metaclass=abc.ABCMeta):
    """
    Abstract interface to handle the cashbox.
    """

    @abc.abstractmethod
    def get_cashbox(self, ctx,) -> (int, int):
        """
        Get the current value
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_cashbox(self, ctx, value_modifier=None, transaction=None):
        """
        Add or remove value
        """
        pass  # pragma: no cover

