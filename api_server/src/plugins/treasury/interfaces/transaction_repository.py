# coding=utf-8

import abc

from src.entity import Transaction, AbstractTransaction
from src.use_case.interface.crud_repository import CRUDRepository


class TransactionRepository(CRUDRepository[Transaction, AbstractTransaction]):
    @abc.abstractmethod
    def validate(self, ctx, id: int) -> None:
        pass  # pragma: no cover
