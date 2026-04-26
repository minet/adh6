import abc
from datetime import date

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractTransaction, Transaction


class TransactionRepository(CRUDRepository[Transaction, AbstractTransaction]):
    @abc.abstractmethod
    async def search_for_export(self, from_date: date, to_date: date) -> list[Transaction]:
        pass  # pragma: no cover
