"""Use cases (business rule layer) of everything related to transactions."""

from adh6.decorator import log_call
from adh6.default import CRUDManager
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import IntMustBePositive, TransactionNotFoundError, ValidationError

from .interfaces import TransactionRepository


class TransactionManager(CRUDManager):
    def __init__(self, transaction_repository: TransactionRepository):
        super().__init__(transaction_repository, TransactionNotFoundError)
        self.transaction_repository = transaction_repository

    @log_call
    async def update_or_create(
        self, abstract_transaction: AbstractTransaction, id: int | None = None
    ) -> tuple[Transaction, bool]:
        if abstract_transaction.value is None:
            raise ValidationError("the value field should not be None")
        if abstract_transaction.value < 0:
            raise IntMustBePositive("value")

        return await super().update_or_create(abstract_transaction, id=id)

    @log_call
    async def partially_update(self, obj: AbstractTransaction, id: int, override: bool = False):
        # author cannot be changed after creation
        if obj.author is not None:
            raise ValidationError("author is a read-only field")
        raise NotImplementedError("transactions do not support partial updates")

    @log_call
    async def delete(self, id: int):
        return await super().delete(id=id)
