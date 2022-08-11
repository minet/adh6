# coding=utf-8
from typing import List
from adh6.entity import AbstractAccount, AbstractTransaction
from adh6.default.decorator.log_call import log_call
from adh6.constants import KnownAccountExpense
from adh6.default.decorator.auto_raise import auto_raise
from adh6.exceptions import AccountNotFoundError, ProductNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.treasury.interfaces.product_repository import ProductRepository
from adh6.treasury.interfaces.account_repository import AccountRepository
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.treasury.interfaces.transaction_repository import TransactionRepository


class ProductManager(CRUDManager):
    def __init__(self, 
                 product_repository: ProductRepository, 
                 transaction_repository: TransactionRepository,
                 payment_method_repository: PaymentMethodRepository,
                 account_repository: AccountRepository):
        super().__init__(product_repository, ProductNotFoundError)
        self.transaction_repository = transaction_repository
        self.payment_method_repository = payment_method_repository
        self.product_repository = product_repository
        self.account_repository = account_repository

    @log_call
    @auto_raise
    def buy(self, ctx, member_id: int, payment_method_id: int, product_ids: List[int] = []) -> None:
        if not product_ids:
            raise ProductNotFoundError("None")

        payment_method = self.payment_method_repository.get_by_id(ctx, payment_method_id)
        dst_accounts, _ = self.account_repository.search_by(ctx, limit=1, filter_=AbstractAccount(name=KnownAccountExpense.TECHNICAL_EXPENSE.value))
        if not dst_accounts:
            raise AccountNotFoundError(KnownAccountExpense.TECHNICAL_EXPENSE.value)
        src_accounts, _ = self.account_repository.search_by(ctx, limit=1, filter_=AbstractAccount(member=member_id))
        if not src_accounts:
            raise AccountNotFoundError(KnownAccountExpense.TECHNICAL_EXPENSE.value)

        for i in product_ids:
            product = self.product_repository.get_by_id(ctx, i)

            _ = self.transaction_repository.create(
                ctx, 
                AbstractTransaction(
                    src=src_accounts[0].id,
                    dst=dst_accounts[0].id,
                    name=product.name,
                    value=product.selling_price,
                    payment_method=payment_method.id,
                ))

