from .payment_method_manager import PaymentMethodManager
from .product_manager import ProductManager

__all__ = ["PaymentMethodManager", "ProductManager"]


class Config:
    pass


def init():
    from .storage import init_storage

    init_storage()
