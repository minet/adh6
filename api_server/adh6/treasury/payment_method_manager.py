# coding=utf-8
from adh6.entity.abstract_payment_method import AbstractPaymentMethod
from adh6.exceptions import PaymentMethodNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository


class PaymentMethodManager(CRUDManager):
    def __init__(self, payment_method_repository: PaymentMethodRepository):
        super().__init__(payment_method_repository, AbstractPaymentMethod, PaymentMethodNotFoundError)
        self.payment_method_repository = payment_method_repository
