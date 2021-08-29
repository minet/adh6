# coding=utf-8
from src.use_case.decorator.security import SecurityDefinition, defines_security
from src.entity.roles import Roles
from src.entity.abstract_product import AbstractProduct
from src.exceptions import ProductNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.product_repository import ProductRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security
from src.entity.roles import Roles

@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_ADMIN,
        "update": Roles.ADH6_ADMIN,
    },
    collection={
        "read": Roles.ADH6_ADMIN,
        "create" : Roles.ADH6_ADMIN,
    }
))
class ProductManager(CRUDManager):
    def __init__(self, product_repository: ProductRepository):
        super().__init__('product', product_repository, AbstractProduct, ProductNotFoundError)
        self.product_repository = product_repository
