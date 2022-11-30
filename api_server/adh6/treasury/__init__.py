from .account_manager import AccountManager
from .account_type_manager import AccountTypeManager
from .transaction_manager import TransactionManager
from .product_manager import ProductManager
from .cashbox_manager import CashboxManager
from .payment_method_manager import PaymentMethodManager


__all__ = [
    "AccountManager",
    "AccountTypeManager",
    "TransactionManager",
    "ProductManager",
    "CashboxManager",
    "PaymentMethodManager"
]


class Config:
    pass


def init():
    from .storage import init as init_storage
    init_storage()
