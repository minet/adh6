# coding=utf-8
from typing import List
from src.entity import AbstractProduct
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import SecurityDefinition, defines_security, is_admin, uses_security
from src.exceptions import ProductNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.use_case.interface.product_repository import ProductRepository
from src.use_case.interface.transaction_repository import TransactionRepository

@defines_security(SecurityDefinition(
    item={
        "read": is_admin(),
        "update": is_admin(),
    },
    collection={
        "read": is_admin(),
        "create" : is_admin(),
    }
))
class ProductManager(CRUDManager):
    def __init__(self, 
                 product_repository: ProductRepository, 
                 transaction_repository: TransactionRepository,
                 payment_method_repository: PaymentMethodRepository):
        super().__init__(product_repository, AbstractProduct, ProductNotFoundError)
        self.transaction_repository = transaction_repository
        self.payment_method_repository = payment_method_repository

    @log_call
    @auto_raise
    @uses_security("create", is_collection=True)
    def buy(self, ctx, member_id: int, payment_method_id: int, product_ids: List[int] = []) -> None:
        if not product_ids:
            raise ProductNotFoundError("None")

        payment_method = self.payment_method_repository.get_by_id(ctx, payment_method_id)

        self.transaction_repository.add_products_payment_record(
            ctx=ctx,
            member_id=member_id,
            products=product_ids,
            payment_method_name=payment_method.name,
            membership_uuid=None
        )
