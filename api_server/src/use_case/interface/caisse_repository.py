# coding=utf-8
"""
Treasury repository.
"""
import abc
from typing import List

from src.entity.transaction import Transaction


class CaisseRepository(metaclass=abc.ABCMeta):
    """
    Abstract interface to handle devices.
    """

    @abc.abstractmethod
    def get_caisse(self, ctx,) -> (int, int):
        """
        Get the current value
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_caisse(self, ctx, value_modifier=None, transaction=None):
        """
        Add or remove value
        """
        pass  # pragma: no cover

