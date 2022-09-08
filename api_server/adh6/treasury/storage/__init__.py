from .account_repository import AccountSQLRepository as AccountRepository
from .account_type_repository import AccountTypeSQLRepository as AccountTypeRepository
from .payment_method_repository import PaymentMethodSQLRepository as PaymentMethodRepository
from .transaction_repository import TransactionSQLRepository as TransactionRepository
from .cashbox_repository import CashboxSQLRepository as CashboxRepository
from .product_repository import ProductSQLRepository as ProductRepository

__all__ = ["AccountRepository", "AccountTypeRepository", "PaymentMethodRepository", "TransactionRepository", "CashboxRepository", "ProductRepository"]

def init_storage():
    from adh6.storage import db
    from .models import PaymentMethod, AccountType, Account

    session = db.session()
    payment_methods = ["Liquide", "Chèque", "Carte bancaire", "Virement", "Stripe", "Aucun"]
    for e in payment_methods:
        if session.query(PaymentMethod).filter(PaymentMethod.name == e).one_or_none() is None:
            session.add(PaymentMethod(name=e))

    account_types = ["Special", "Adherent", "Club interne", "Club externe", "Association externe"]
    for e in account_types:
        if session.query(AccountType).filter(AccountType.name == e).one_or_none() is None:
            session.add(AccountType(name=e))

    special = session.query(AccountType).filter(AccountType.name == account_types[0]).one()
    accounts = ["MiNET frais techniques", "MiNET frais asso"]
    for e in accounts:
        if session.query(Account).filter(Account.name == e).one_or_none() is None:
            session.add(
                Account(
                    type=special.id,
                    name=e,
                    actif=True,
                    compte_courant=True,
                    pinned=True
                )
            )
    session.commit()
