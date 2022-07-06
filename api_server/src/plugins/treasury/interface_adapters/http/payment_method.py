# coding=utf-8
from src.entity import PaymentMethod
from src.interface_adapter.http_api.default import DefaultHandler
from src.plugins.treasury.use_cases.payment_method_manager import PaymentMethodManager


class PaymentMethodHandler(DefaultHandler):
    def __init__(self, payment_method_manager: PaymentMethodManager):
        super().__init__(PaymentMethod, PaymentMethod, payment_method_manager)
