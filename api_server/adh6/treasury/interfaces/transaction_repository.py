# coding=utf-8

import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractTransaction, Transaction


class TransactionRepository(CRUDRepository[Transaction, AbstractTransaction]):
    @abc.abstractmethod
    def validate(self, id: int) -> None:
        pass  # pragma: no cover
