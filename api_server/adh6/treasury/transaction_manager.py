# coding=utf-8
""" Use cases (business rule layer) of everything related to transactions. """
import typing as t

from adh6.authentication import Roles
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import TransactionNotFoundError, ValidationError, IntMustBePositive
from adh6.decorator import log_call
from adh6.default import CRUDManager
import logging

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
    def update_or_create(self, abstract_transaction: AbstractTransaction, id: t.Optional[int] = None) -> t.Tuple[Transaction, bool]:
        if abstract_transaction.src == abstract_transaction.dst:
            raise ValidationError('the source and destination accounts must not be the same')
        if abstract_transaction.value is None:
            raise ValidationError('the value field should not be None')
        if abstract_transaction.value <= 0:
            raise IntMustBePositive('value')

        from adh6.context import get_roles, get_user
        if Roles.TRESO_WRITE.value not in get_roles():
            abstract_transaction.pending_validation = True
        admin_id = get_user()
        abstract_transaction.author = admin_id

        transaction, created = super().update_or_create(abstract_transaction, id=id)

        if created:
            logging.debug('cashbox_update')
            if transaction.cashbox == "to":
                self.cashbox_repository.update(value_modifier=transaction.value, transaction=transaction)
            elif transaction.cashbox == "from":
                self.cashbox_repository.update(value_modifier=-transaction.value, transaction=transaction)
                
        return transaction, created

    @log_call
    def partially_update(self, abstract_transaction: AbstractTransaction, id=None, override=False, **kwargs):
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
    def validate(self, id: int):
        transaction = self.get_by_id(id=id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to validate a transaction that is already validated")
        return self.transaction_repository.validate(id)

    @log_call
    def delete(self, id: int):
        transaction = self.get_by_id(id=id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to delete a transaction that is already validated")

        return super().delete(id=id)
