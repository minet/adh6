# coding=utf-8
from src.entity import PaymentMethod
from src.use_case.interface.crud_repository import CRUDRepository


class PaymentMethodRepository(CRUDRepository[PaymentMethod, PaymentMethod]):
    pass  # pragma: no cover
