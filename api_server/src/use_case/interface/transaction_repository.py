# coding=utf-8

from typing import List

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Transaction, AbstractTransaction
from src.use_case.interface.crud_repository import CRUDRepository


class TransactionRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractTransaction = None) -> (List[Transaction], int):
        raise NotImplemented

    def create(self, ctx, object_to_create: Transaction) -> object:
        raise NotImplemented

    def update(self, ctx, object_to_update: AbstractTransaction, override=False) -> object:
        raise NotImplemented

    def validate(self, ctx, transaction_id) -> None:
        raise NotImplemented

    def delete(self, ctx, object_id) -> None:
        raise NotImplemented
