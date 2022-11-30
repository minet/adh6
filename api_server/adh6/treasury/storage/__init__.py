from .account_repository import AccountSQLRepository as AccountRepository
from .account_type_repository import AccountTypeSQLRepository as AccountTypeRepository
from .payment_method_repository import PaymentMethodSQLRepository as PaymentMethodRepository
from .transaction_repository import TransactionSQLRepository as TransactionRepository
from .cashbox_repository import CashboxSQLRepository as CashboxRepository
from .product_repository import ProductSQLRepository as ProductRepository

__all__ = ["AccountRepository", "AccountTypeRepository", "PaymentMethodRepository", "TransactionRepository", "CashboxRepository", "ProductRepository"]

def init():
    from adh6.storage import session
    from .models import PaymentMethod, AccountType, Account
    from ..config import Config

    import logging

    logging.info(f"--- Setup payment methods: {Config.DEFAULT_PAYMENT_METHOD} ---")
    for e in Config.DEFAULT_PAYMENT_METHOD:
        if session.query(PaymentMethod).filter(PaymentMethod.name == e).one_or_none() is None:
            logging.warning(f"Payment method not found creating it: {e}")
            session.add(PaymentMethod(name=e))

    logging.info(f"--- Setup account types: {Config.DEFAULT_ACCOUNT_TYPES} ---")
    for e in Config.DEFAULT_ACCOUNT_TYPES:
        if session.query(AccountType).filter(AccountType.name == e).one_or_none() is None:
            logging.warning(f"account types not found creating it: {e}")
            session.add(AccountType(name=e))

    special = session.query(AccountType).filter(AccountType.name == Config.DEFAULT_ACCOUNT_TYPES[0]).one()
    logging.info(f"--- Setup default accounts: {Config.DEFAULT_ACCOUNT_TYPES} ---")
    for e in Config.DEFAULT_ACCOUNT_TYPES:
        if session.query(Account).filter(Account.name == e).one_or_none() is None:
            logging.warning(f"default account not found creating it: {e}")
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
