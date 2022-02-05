# coding=utf-8
from src.entity import Product
from src.use_case.interface.crud_repository import CRUDRepository


class ProductRepository(CRUDRepository[Product, Product]):
    pass
