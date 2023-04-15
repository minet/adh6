from .account_manager import AccountManager
from .account_type_manager import AccountTypeManager
from .product_manager import ProductManager
from .cashbox_manager import CashboxManager
from .payment_method_manager import PaymentMethodManager


__all__ = [
    "AccountManager",
    "AccountTypeManager",
    "ProductManager",
    "CashboxManager",
    "PaymentMethodManager"
]


class Config:
    pass


def init():
    from .storage import init_storage
    init_storage()
