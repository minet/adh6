# coding=utf-8
from typing import List

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call, with_context
from adh6.treasury.product_manager import ProductManager


class ProductHandler:
    """
    Handler for the product endpoint
    """

    # Constructor method that initializes the class with a ProductManager object
    def __init__(self, product_manager: ProductManager):
        self.product_manager = product_manager

    # Method to search for products
    @with_context
    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None):
        # Call the search method of the ProductManager object and stores the result and total count in variables
        result, total_count = self.product_manager.search(limit=limit, offset=offset, terms=terms)
        # Set the headers to be returned with the result
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        # Map each product in the result to a dictionnary representation and return the result and headers
        result = list(map(lambda x: x.to_dict(), result))
        return result, 200, headers

    # Method to get a product by its id
    @with_context
    @log_call
    def get(self, id_: int):
        # Calls the get_by_id method of the ProductManager object and returns the result and a status code
        return self.product_manager.get_by_id(id=id_).to_dict(), 200

    # Method to buy products
    @with_context
    @log_call
    def buy_post(self, member_id: int, payment_method: int, products: List[int]):
        # Calls the buy method of the ProductManager object with the provided parameters
        self.product_manager.buy(member_id, payment_method, products)
        # Return None and a status code indicating success
        return None, 204
