# coding=utf-8

from src.entity.product import Product
from src.exceptions import ProductNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.product_repository import ProductRepository


class ProductManager(CRUDManager):
    def __init__(self, product_repository: ProductRepository):
        super().__init__('product', product_repository, Product, ProductNotFoundError)
        self.product_repository = product_repository

    def delete(self, ctx, *args, **kwargs):
        raise NotImplemented

    def update_or_create(self, ctx, obj, **kwargs):
        raise NotImplemented

    def partially_update(self, ctx, obj, override=False, **kwargs):
        raise NotImplemented
