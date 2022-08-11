# coding=utf-8
from adh6.entity import PaymentMethod
from adh6.default.http_handler import DefaultHandler
from adh6.treasury.payment_method_manager import PaymentMethodManager


class PaymentMethodHandler(DefaultHandler):
    def __init__(self, payment_method_manager: PaymentMethodManager):
        super().__init__(PaymentMethod, PaymentMethod, payment_method_manager)
