# coding=utf-8
from src.entity.abstract_payment_method import AbstractPaymentMethod
from src.entity.roles import Roles
from src.exceptions import PaymentMethodNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.security import defines_security, SecurityDefinition
from src.use_case.interface.payment_method_repository import PaymentMethodRepository


@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_USER
    },
    collection={
        "read": Roles.ADH6_USER
    }
))
class PaymentMethodManager(CRUDManager):
    def __init__(self, payment_method_repository: PaymentMethodRepository):
        super().__init__('payment_method', payment_method_repository, AbstractPaymentMethod, PaymentMethodNotFoundError)
        self.payment_method_repository = payment_method_repository
