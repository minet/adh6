# coding=utf-8

from typing import List, Optional, Tuple, Union

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Transaction, AbstractTransaction, Product
from src.use_case.interface.crud_repository import CRUDRepository


class TransactionRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractTransaction = None) -> Tuple[List[Transaction], int]:
        raise NotImplementedError

    def create(self, ctx, object_to_create: Transaction) -> object:
        raise NotImplementedError

    def update(self, ctx, object_to_update: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    def validate(self, ctx, transaction_id) -> None:
        raise NotImplementedError

    def delete(self, ctx, object_id) -> None:
        raise NotImplementedError

    def add_member_payment_record(self, ctx, amount_in_cents: int, title: str, member_username: str, payment_method: str, membership_uuid: str) -> None:
        raise NotImplementedError

    def add_products_payment_record(self, ctx, member_id: int, products: List[Union[Product, int]], payment_method_name: str, membership_uuid: Optional[str]) -> None:
        raise NotImplementedError
