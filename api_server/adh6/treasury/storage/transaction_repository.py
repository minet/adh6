"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.entity import AbstractTransaction, Transaction
from adh6.exceptions import AccountNotFoundError, PaymentMethodNotFoundError
from adh6.storage import db
from adh6.storage.sql.track_modifications import track_modifications

from ..interfaces import TransactionRepository
from .models import Account, PaymentMethod, Transaction as SQLTransaction

auto_validate_payment_method = ["Liquide", "Carte bancaire"]


class TransactionSQLRepository(TransactionRepository):
    @log_call
    def get_by_id(self, object_id: int) -> Transaction | None:
        with db.sessionmaker.begin() as session:
            obj = session.query(SQLTransaction).filter(SQLTransaction.id == object_id).one_or_none()
            return _map_transaction_sql_to_entity(obj) if obj else obj

    @log_call
    def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: AbstractTransaction | None = None,
    ) -> tuple[list[Transaction], int]:
        with db.sessionmaker.begin() as session:
            query = session.query(SQLTransaction)

            if filter_:
                if filter_.id is not None:
                    query = query.filter(SQLTransaction.id == filter_.id)
                if filter_.payment_method is not None:
                    query = query.filter(SQLTransaction.type == filter_.payment_method)
                if filter_.pending_validation is not None:
                    query = query.filter(SQLTransaction.pending_validation == filter_.pending_validation)
                if filter_.src is not None and filter_.dst is not None and filter_.src == filter_.dst:
                    query = query.filter((SQLTransaction.src == filter_.src) | (SQLTransaction.dst == filter_.dst))
                elif filter_.src is not None:
                    query = query.filter(SQLTransaction.src == filter_.src)
                elif filter_.dst is not None:
                    query = query.filter(SQLTransaction.dst == filter_.dst)

            if terms:
                query = query.filter(SQLTransaction.name.like(f"%{terms}%"))

            count = query.count()
            query = query.offset(offset)
            query = query.limit(limit)
            r = query.all()

            return [_map_transaction_sql_to_entity(i) for i in r], count

    @log_call
    def create(self, abstract_transaction: AbstractTransaction) -> object:
        now = datetime.now()

        account_src_id = None
        if abstract_transaction.src is not None:
            with db.sessionmaker.begin() as session:
                account_src = session.query(Account).filter(Account.id == abstract_transaction.src).one_or_none()
                if not account_src:
                    raise AccountNotFoundError(abstract_transaction.src)
                account_src_id = account_src.id

        account_dst_id = None
        if abstract_transaction.dst is not None:
            with db.sessionmaker.begin() as session:
                account_dst = session.query(Account).filter(Account.id == abstract_transaction.dst).one_or_none()
                if not account_dst:
                    raise AccountNotFoundError(abstract_transaction.dst)
                account_dst_id = account_dst.id

        method_id = None
        if abstract_transaction.payment_method is not None:
            with db.sessionmaker.begin() as session:
                method = (
                    session.query(PaymentMethod).filter(PaymentMethod.id == abstract_transaction.payment_method).one_or_none()
                )
                if not method:
                    raise PaymentMethodNotFoundError(abstract_transaction.payment_method)
                method_id = method.id

        transaction = SQLTransaction(
            src=account_src_id,
            dst=account_dst_id,
            value=abstract_transaction.value,
            name=abstract_transaction.name,
            timestamp=now,
            attachments="",
            type=method_id,
            author_id=abstract_transaction.author,
            pending_validation=abstract_transaction.pending_validation if abstract_transaction.pending_validation else False,
        )
        with db.sessionmaker.begin() as session, track_modifications(session, transaction):
            session.add(transaction)
            session.flush()
            mapped_transaction = _map_transaction_sql_to_entity(transaction)

        return mapped_transaction

    def update(self, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    @log_call
    def validate(self, id) -> None:
        with db.sessionmaker.begin() as session:
            query = session.query(SQLTransaction)
            query = query.filter(SQLTransaction.id == id)

            transaction = query.one()
            with track_modifications(session, transaction):
                transaction.pending_validation = False

    @log_call
    def delete(self, object_id) -> None:
        with db.sessionmaker.begin() as session:
            transaction = session.query(SQLTransaction).filter(SQLTransaction.id == object_id).one()

            with track_modifications(session, transaction):
                session.delete(transaction)


def _map_transaction_sql_to_entity(t: SQLTransaction) -> Transaction:
    """
    Map a Transaction object from SQLAlchemy to a Transaction (from the entity folder/layer).
    """
    return Transaction(
        id=t.id,
        src=t.src,
        dst=t.dst,
        timestamp=str(t.timestamp),
        name=t.name,
        value=t.value,
        payment_method=t.type,
        attachments=[],
        author=t.author_id,
        pending_validation=t.pending_validation,
    )
