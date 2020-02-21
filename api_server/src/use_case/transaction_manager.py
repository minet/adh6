# coding=utf-8
""" Use cases (business rule layer) of everything related to transactions. """

from src.entity import AbstractTransaction
from src.exceptions import TransactionNotFoundError, ValidationError, IntMustBePositive
from src.use_case.base_manager import BaseManager
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.payment_method_manager import PaymentMethodManager


class CaisseManager(object):
    def update_caisse(self, ctx, value_modifier, transaction):
        pass


class TransactionManager(BaseManager):
    """
    Implements all the use cases related to transaction management.
    """

    def __init__(self,
                 transaction_repository: TransactionRepository,
                 payment_method_manager: PaymentMethodManager,
                 caisse_manager: CaisseManager
                 ):
        super().__init__('transaction', transaction_repository, AbstractTransaction, TransactionNotFoundError)
        self.transaction_repository = transaction_repository
        self.payment_method_manager = payment_method_manager
        self.caisse_manager = caisse_manager

    def update_or_create(self, ctx, abstract_transaction: AbstractTransaction, transaction_id=None):
        if abstract_transaction.src == abstract_transaction.dst:
            raise ValidationError('the source and destination accounts must not be the same')
        if abstract_transaction.value <= 0:
            raise IntMustBePositive()

        transaction, created = super().update_or_create(ctx, abstract_transaction, transaction_id=transaction_id)

        if created:
            liquide, _ = self.payment_method_manager.search(ctx, limit=1, terms='Liquide')
            if abstract_transaction.payment_method == liquide[0].id:
                if abstract_transaction.caisse == "to":
                    self.caisse_manager.update_caisse(ctx, value_modifier=abstract_transaction.value,
                                                      transaction=transaction)
                elif abstract_transaction.caisse == "from":
                    self.caisse_manager.update_caisse(ctx, value_modifier=-abstract_transaction.value,
                                                      transaction=transaction)

        return transaction

    def partially_update(self, ctx, abstract_transaction: AbstractTransaction, transaction_id=None, override=False,
                         **kwargs):
        if any(True for _ in filter(lambda e: e is not None, [
            abstract_transaction.value,
            abstract_transaction.src,
            abstract_transaction.dst,
            abstract_transaction.timestamp,
            abstract_transaction.payment_method,
            abstract_transaction.caisse,
            abstract_transaction.author,
        ])):
            raise ValidationError('you are trying to update a transaction with fields that cannot be updated')
        pass

    def delete(self, ctx, *args, **kwargs):
        raise NotImplemented
