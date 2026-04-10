import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractTransaction, Transaction


class TransactionRepository(CRUDRepository[Transaction, AbstractTransaction]):
    @abc.abstractmethod
    async def validate(self, id: int) -> None:
        pass  # pragma: no cover
