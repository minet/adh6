# coding=utf-8
from src.use_case.decorator.security import SecurityDefinition, defines_security, is_admin
from src.entity.abstract_product import AbstractProduct
from src.exceptions import ProductNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.product_repository import ProductRepository

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
    def __init__(self, product_repository: ProductRepository):
        super().__init__('product', product_repository, AbstractProduct, ProductNotFoundError)
        self.product_repository = product_repository
