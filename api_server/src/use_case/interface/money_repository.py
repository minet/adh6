# coding=utf-8
"""
Money repository, stores money movement.
"""
import abc
from src.entity import Product
from typing import List


class MoneyRepository(abc.ABC):
    """
    Abstract interface to handle money movements.
    """

    @abc.abstractmethod
    def add_member_payment_record(self, ctx, amount_in_cents: int, title: str, member_username: str,
                                  payment_method: str) -> None:
        """
        Search switches.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_products_payment_record(self, ctx, products: List[Product]) -> None:
        """
        Search switches.
        """
        pass  # pragma: no cover
