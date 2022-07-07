# coding=utf-8
from typing import List

from adh6.storage import db
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.default.util.serializer import serialize_response
from adh6.treasury.product_manager import ProductManager


class ProductHandler:
    def __init__(self, product_manager: ProductManager):
        self.product_manager = product_manager

    @with_context
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None):
        try:
            result, total_count = self.product_manager.search(ctx, limit=limit, offset=offset, terms=terms)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(serialize_response, result))
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def get(self, ctx, id_: int):
        try:
            return serialize_response(self.product_manager.get_by_id(ctx, id=id_)), 200
        except Exception as e:
            return handle_error(ctx, e)


    @with_context
    @log_call
    def buy_post(self, ctx, member_id: int, payment_method: int, products: List[int]):
        try:
            self.product_manager.buy(ctx,member_id, payment_method, products)
            return None, 204
        except Exception as e:
            return handle_error(ctx, e)
