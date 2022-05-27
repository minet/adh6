# coding=utf-8

import abc
from typing import List, Optional, Union

from src.entity import Transaction, AbstractTransaction, Product
from src.use_case.interface.crud_repository import CRUDRepository


class TransactionRepository(CRUDRepository[Transaction, AbstractTransaction]):
    @abc.abstractmethod
    def validate(self, ctx, id: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_member_payment_record(self, ctx, amount_in_cents: int, title: str, member_username: str, payment_method: str, membership_uuid: str) -> None:
        """
        deprecated, payment record will be done in the manager
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_products_payment_record(self, ctx, member_id: int, products: List[Union[Product, int]], payment_method_name: str, membership_uuid: Optional[str]) -> None:
        """
        deprecated, payment record will be done in the manager
        """
        pass  # pragma: no cover
