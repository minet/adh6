# coding=utf-8
from src.entity.abstract_product import AbstractProduct
from src.exceptions import ProductNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.product_repository import ProductRepository


class ProductManager(CRUDManager):
    def __init__(self, product_repository: ProductRepository):
        super().__init__('product', product_repository, AbstractProduct, ProductNotFoundError)
        self.product_repository = product_repository

    def delete(self, ctx, *args, **kwargs):
        raise NotImplementedError()

    def update_or_create(self, ctx, obj, **kwargs):
        raise NotImplementedError()

    def partially_update(self, ctx, obj, override=False, **kwargs):
        raise NotImplementedError()
