"""Use cases (business rule layer) of everything related to transactions."""

import logging

from adh6.decorator import log_call
from adh6.default import CRUDManager
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import IntMustBePositive, TransactionNotFoundError, ValidationError

from .interfaces import CashboxRepository, TransactionRepository


class TransactionManager(CRUDManager):
    """
    Implements all the use cases related to transaction management.
    """

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        cashbox_repository: CashboxRepository,
    ):
        super().__init__(transaction_repository, TransactionNotFoundError)
        self.transaction_repository = transaction_repository
        self.cashbox_repository = cashbox_repository

    @log_call
    async def update_or_create(
        self, abstract_transaction: AbstractTransaction, id: int | None = None
    ) -> tuple[Transaction, bool]:
        if abstract_transaction.src == abstract_transaction.dst:
            raise ValidationError("the source and destination accounts must not be the same")
        if abstract_transaction.value is None:
            raise ValidationError("the value field should not be None")
        if abstract_transaction.value < 0:
            raise IntMustBePositive("value")

        # Context-based role resolution from legacy Connexion handlers is not
        # available in FastAPI; keep conservative defaults if not provided.
        if abstract_transaction.pending_validation is None:
            abstract_transaction.pending_validation = True

        transaction, created = await super().update_or_create(abstract_transaction, id=id)

        if created:
            logging.debug("cashbox_update")  # noqa: LOG015  # TODO: use a dedicated logger
            if transaction.cashbox == "to":
                await self.cashbox_repository.update(value_modifier=transaction.value, transaction=transaction)
            elif transaction.cashbox == "from":
                await self.cashbox_repository.update(value_modifier=-transaction.value, transaction=transaction)

        return transaction, created

    @log_call
    async def partially_update(self, abstract_transaction: AbstractTransaction, id=None, override=False, **kwargs):
        if any(
            True
            for _ in filter(
                lambda e: e is not None,
                [
                    abstract_transaction.value,
                    abstract_transaction.src,
                    abstract_transaction.dst,
                    abstract_transaction.timestamp,
                    abstract_transaction.payment_method,
                    abstract_transaction.cashbox,
                    abstract_transaction.author,
                ],
            )
        ):
            raise ValidationError("you are trying to update a transaction with fields that cannot be updated")
        raise NotImplementedError

    @log_call
    async def validate(self, id: int):
        transaction = await self.get_by_id(id=id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to validate a transaction that is already validated")
        return await self.transaction_repository.validate(id)

    @log_call
    async def delete(self, id: int):
        transaction = await self.get_by_id(id=id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to delete a transaction that is already validated")

        return await super().delete(id=id)
