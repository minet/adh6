from .account_manager import AccountManager
from .account_type_manager import AccountTypeManager
from .cashbox_manager import CashboxManager
from .payment_method_manager import PaymentMethodManager
from .product_manager import ProductManager

__all__ = ["AccountManager", "AccountTypeManager", "CashboxManager", "PaymentMethodManager", "ProductManager"]


class Config:
    pass


def init():
    from .storage import init_storage

    init_storage()
