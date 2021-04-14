# coding=utf-8
""" Use cases (business rule layer) of everything related to transactions. """
from src.constants import CTX_ROLES
from src.entity import AbstractTransaction
from src.entity.roles import Roles
from src.exceptions import TransactionNotFoundError, ValidationError, IntMustBePositive
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.use_case.cashbox_manager import CashboxManager
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, uses_security
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.payment_method_manager import PaymentMethodManager


@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_ADMIN,
        "update": Roles.ADH6_TRESO,
        "delete": Roles.ADH6_TRESO
    },
    collection={
        "read": Roles.ADH6_ADMIN,
        "create": Roles.ADH6_ADMIN,
    }
))
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

    @log_call
    @auto_raise
    def update_or_create(self, ctx, abstract_transaction: AbstractTransaction, transaction_id=None):
        if abstract_transaction.src == abstract_transaction.dst:
            raise ValidationError('the source and destination accounts must not be the same')
        if abstract_transaction.value <= 0:
            raise IntMustBePositive('value')

        @uses_security("create", is_collection=True)
        def _force_invalid(cls, ctx, obj):
            roles = ctx.get(CTX_ROLES)
            if Roles.ADH6_TRESO.value not in roles:
                obj.pending_validation = True
        _force_invalid(self, ctx, abstract_transaction)

        transaction, created = super().update_or_create(ctx, abstract_transaction, transaction_id=transaction_id)

        if created:
            if abstract_transaction.cashbox == "to":
                self.cashbox_manager.update_cashbox(ctx, value_modifier=abstract_transaction.value,
                                                    transaction=transaction)
            elif abstract_transaction.cashbox == "from":
                self.cashbox_manager.update_cashbox(ctx, value_modifier=-abstract_transaction.value,
                                                    transaction=transaction)

        return transaction, created

    @log_call
    @auto_raise
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

    @log_call
    @auto_raise
    def validate(self, ctx, transaction_id=None, **kwargs):
        transaction: AbstractTransaction = self.get_by_id(ctx, transaction_id=transaction_id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to validate a transaction that is already validated")

        @uses_security("update", is_collection=False)
        def _validate(cls, ctx, transaction_id):
            self.transaction_repository.validate(ctx, transaction_id)

        return _validate(self, ctx, transaction_id)

    @log_call
    @auto_raise
    def delete(self, ctx, transaction_id=None, **kwargs):
        transaction: AbstractTransaction = self.get_by_id(ctx, transaction_id=transaction_id)
        if not transaction.pending_validation:
            raise ValidationError("you are trying to delete a transaction that is already validated")

        return super().delete(ctx, transaction_id=transaction_id)
