# coding=utf-8
from typing import List
from src.entity import Product
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.product_manager import ProductManager


class ProductHandler(DefaultHandler):
    def __init__(self, product_manager: ProductManager):
        super().__init__(Product, Product, product_manager)
        self.product_manager = product_manager


    @with_context
    @require_sql
    @log_call
    def buy_post(self, ctx, member_id: int, payment_method: int, products: List[int]):
        try:
            self.product_manager.buy(ctx,member_id, payment_method, products)
            return None, 204
        except Exception as e:
            return handle_error(ctx, e)
