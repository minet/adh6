# coding=utf-8
""" Use cases (business rule layer) of everything related to transactions. """

from src.entity import AbstractTransaction
from src.exceptions import TransactionNotFoundError, ValidationError, IntMustBePositive
from src.use_case.cashbox_manager import CashboxManager
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.payment_method_manager import PaymentMethodManager


class cashboxManager(object):
    def update_cashbox(self, ctx, value_modifier, transaction):
        pass


class TransactionManager(CRUDManager):
    """
    Implements all the use cases related to transaction management.
    """

    def __init__(self,
                 transaction_repository: TransactionRepository,
                 payment_method_manager: PaymentMethodManager,
                 cashbox_manager: CashboxManager
                 ):
        super().__init__('transaction', transaction_repository, AbstractTransaction, TransactionNotFoundError)
        self.transaction_repository = transaction_repository
        self.payment_method_manager = payment_method_manager
        self.cashbox_manager = cashbox_manager

    def update_or_create(self, ctx, abstract_transaction: AbstractTransaction, transaction_id=None):
        if abstract_transaction.src == abstract_transaction.dst:
            raise ValidationError('the source and destination accounts must not be the same')
        if abstract_transaction.value <= 0:
            raise IntMustBePositive('value')

        transaction, created = super().update_or_create(ctx, abstract_transaction, transaction_id=transaction_id)

        if created:
            if abstract_transaction.cashbox == "to":
                self.cashbox_manager.update_cashbox(ctx, value_modifier=abstract_transaction.value,
                                                  transaction=transaction)
            elif abstract_transaction.cashbox == "from":
                self.cashbox_manager.update_cashbox(ctx, value_modifier=-abstract_transaction.value,
                                                  transaction=transaction)

        return transaction, created

    def partially_update(self, ctx, abstract_transaction: AbstractTransaction, transaction_id=None, override=False,
                         **kwargs):
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
        raise NotImplemented

    def delete(self, ctx, *args, **kwargs):
        raise NotImplemented
