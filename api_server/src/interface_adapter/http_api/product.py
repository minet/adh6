# coding=utf-8
from src.entity import Product
from src.interface_adapter.http_api.default import DefaultHandler
from src.use_case.product_manager import ProductManager


class ProductHandler(DefaultHandler):
    def __init__(self, product_manager: ProductManager):
        super().__init__(Product, Product, product_manager)
