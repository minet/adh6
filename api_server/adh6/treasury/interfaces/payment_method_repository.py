# coding=utf-8
from adh6.entity import PaymentMethod
from adh6.default.crud_repository import CRUDRepository


class PaymentMethodRepository(CRUDRepository[PaymentMethod, PaymentMethod]):
    pass  # pragma: no cover
