# coding=utf-8
from src.entity.abstract_payment_method import AbstractPaymentMethod
from src.exceptions import PaymentMethodNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.security import defines_security, SecurityDefinition, Roles, has_any_role
from src.use_case.interface.payment_method_repository import PaymentMethodRepository


@defines_security(SecurityDefinition(
    item={
        "read": has_any_role([Roles.USER])
    },
    collection={
        "read": has_any_role([Roles.USER])
    }
))
class PaymentMethodManager(CRUDManager):
    def __init__(self, payment_method_repository: PaymentMethodRepository):
        super().__init__('payment_method', payment_method_repository, AbstractPaymentMethod, PaymentMethodNotFoundError)
        self.payment_method_repository = payment_method_repository
