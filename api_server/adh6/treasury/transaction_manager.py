# coding=utf-8
""" Use cases (business rule layer) of everything related to transactions. """
from typing import Optional, Tuple
from adh6.authentication import Roles
from adh6.constants import CTX_ROLES
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import TransactionNotFoundError, ValidationError, IntMustBePositive
from adh6.decorator import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.misc import log_extra, LOG

from .interfaces import CashboxRepository, TransactionRepository


class TransactionManager(CRUDManager):
    """
    Implements all the use cases related to transaction management.
    """

    def __init__(self, transaction_repository: TransactionRepository, cashbox_repository: CashboxRepository):
        super().__init__(transaction_repository, TransactionNotFoundError)
        self.transaction_repository = transaction_repository
        self.cashbox_repository = cashbox_repository

    @log_call
    def update_or_create(self, ctx, abstract_transaction: AbstractTransaction, id: Optional[int] = None) -> Tuple[Transaction, bool]:
        if abstract_transaction.src == abstract_transaction.dst:
            raise ValidationError('the source and destination accounts must not be the same')
        if abstract_transaction.value is None:
            raise ValidationError('the value field should not be None')
        if abstract_transaction.value <= 0:
            raise IntMustBePositive('value')

        if Roles.TRESO_WRITE.value not in ctx.get(CTX_ROLES):
            abstract_transaction.pending_validation = True

        transaction, created = super().update_or_create(ctx, abstract_transaction, id=id)

        if created:
            LOG.info('cashbox_update', extra=log_extra(
                ctx,
                value_modifier=abstract_transaction.value,
                transaction=transaction,
            ))
            if transaction.cashbox == "to":
                self.cashbox_repository.update(ctx, value_modifier=transaction.value, transaction=transaction)
            elif transaction.cashbox == "from":
                self.cashbox_repository.update(ctx, value_modifier=-transaction.value, transaction=transaction)
                
        return transaction, created

    @log_call
    def partially_update(self, ctx, abstract_transaction: AbstractTransaction, id=None, override=False, **kwargs):
        if any(True for _ in filter(lambda e: e is not None, [
            abstract_transaction.value,
            abstract_transaction.src,
            abstract_transaction.dst,
            abstract_transaction.timestamp,
            abstract_transaction.payment_method,
            abstract_transaction.cashbox,
            abstract_transaction.author,
        ])):
            raise ValidationError('you are trying to update a transaction with fields that cannot be updated')
        raise NotImplementedError

    @log_call
    def validate(self, ctx, id: int):
        transaction = self.get_by_id(ctx, id=id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to validate a transaction that is already validated")
        return self.transaction_repository.validate(ctx, id)

    @log_call
    def delete(self, ctx, id: int):
        transaction = self.get_by_id(ctx, id=id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to delete a transaction that is already validated")

        return super().delete(ctx, id=id)
