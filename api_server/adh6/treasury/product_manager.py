# coding=utf-8
import typing as t

from adh6.entity import AbstractTransaction
from adh6.decorator import log_call
from adh6.constants import KnownAccountExpense
from adh6.exceptions import ProductNotFoundError
from adh6.default import CRUDManager

from .account_manager import AccountManager
from .interfaces import ProductRepository, PaymentMethodRepository, TransactionRepository


class ProductManager(CRUDManager):
    def __init__(self, 
                 product_repository: ProductRepository, 
                 transaction_repository: TransactionRepository,
                 payment_method_repository: PaymentMethodRepository,
                 account_manager: AccountManager):
        super().__init__(product_repository, ProductNotFoundError)
        self.transaction_repository = transaction_repository
        self.payment_method_repository = payment_method_repository
        self.product_repository = product_repository
        self.account_manager = account_manager

    @log_call
    def buy(self, member_id: int, payment_method_id: int, product_ids: t.List[int] = []) -> None:
        if not product_ids:
            raise ProductNotFoundError("None")

        payment_method = self.payment_method_repository.get_by_id(payment_method_id)
        dst_account = self.account_manager.get_by_name(KnownAccountExpense.TECHNICAL_EXPENSE.value)
        src_account = self.account_manager.get_by_member(member_id)
        for i in product_ids:
            product = self.product_repository.get_by_id(i)
            _ = self.transaction_repository.create(
                AbstractTransaction(
                    src=src_account.id,
                    dst=dst_account.id,
                    name=product.name,
                    value=product.selling_price,
                    payment_method=payment_method.id,
                ))

