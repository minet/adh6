from .payment_method_repository import PaymentMethodSQLRepository as PaymentMethodRepository
from .product_repository import ProductSQLRepository as ProductRepository
from .transaction_repository import TransactionSQLRepository as TransactionRepository

__all__ = [
    "PaymentMethodRepository",
    "ProductRepository",
    "TransactionRepository",
]


def init_storage():
    from adh6.storage import db

    from .models import PaymentMethod

    with db.sessionmaker.begin() as session:
        payment_methods = ["Liquide", "Chèque", "Carte bancaire", "Virement", "Stripe", "Aucun"]
        for e in payment_methods:
            if session.query(PaymentMethod).filter(PaymentMethod.name == e).one_or_none() is None:
                session.add(PaymentMethod(name=e))
