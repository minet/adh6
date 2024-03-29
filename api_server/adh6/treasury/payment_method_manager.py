# coding=utf-8
from adh6.exceptions import PaymentMethodNotFoundError
from adh6.default.crud_manager import CRUDManager

from .interfaces import PaymentMethodRepository


class PaymentMethodManager(CRUDManager):
    def __init__(self, payment_method_repository: PaymentMethodRepository):
        super().__init__(payment_method_repository, PaymentMethodNotFoundError)
