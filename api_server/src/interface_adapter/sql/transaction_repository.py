# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime

from sqlalchemy.orm.session import Session
from typing import List, Optional, Tuple

from sqlalchemy.orm import aliased

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, CTX_ADMIN
from src.entity import AbstractTransaction, Transaction
from src.exceptions import AccountNotFoundError, MemberNotFoundError, PaymentMethodNotFoundError, TransactionNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Transaction as SQLTransaction, Account, PaymentMethod, Adherent
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.transaction_repository import TransactionRepository

auto_validate_payment_method = ["Liquide", "Carte bancaire"]

class TransactionSQLRepository(TransactionRepository):
    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractTransaction:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLTransaction).filter(SQLTransaction.id == object_id).one_or_none()
        if obj is None:
            raise TransactionNotFoundError(object_id)
        return _map_transaction_sql_to_abstract_entity(obj)

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_:  Optional[AbstractTransaction] = None) -> Tuple[List[AbstractTransaction], int]:
        session: Session= ctx.get(CTX_SQL_SESSION)

        account_source = aliased(Account)
        account_destination = aliased(Account)

        query= session.query(SQLTransaction)
        query= query.join(account_source, account_source.id == SQLTransaction.dst)
        query= query.join(account_destination, account_destination.id == SQLTransaction.src)

        if terms:
            query= query.filter((SQLTransaction.name.contains(terms)))

        if filter_:
            if filter_.id is not None:
                query= query.filter(SQLTransaction.id == filter_.id)
            if filter_.payment_method is not None:
                query= query.filter(SQLTransaction.type == filter_.payment_method)
            if filter_.pending_validation is not None:
                query= query.filter(
                    (SQLTransaction.pending_validation == filter_.pending_validation)
                )
            if filter_.src is not None and filter_.dst is not None and filter_.src == filter_.dst:
                query= query.filter(
                    (SQLTransaction.src == filter_.src) |
                    (SQLTransaction.dst == filter_.dst)
                )
            elif filter_.src is not None:
                query= query.filter(SQLTransaction.src == filter_.src)
            elif filter_.dst is not None:
                query= query.filter(SQLTransaction.dst == filter_.dst)

        count = query.count()
        query= query.order_by(SQLTransaction.timestamp.desc())
        query= query.offset(offset)
        query= query.limit(limit)
        r = query.all()

        return list(map(_map_transaction_sql_to_abstract_entity, r)), count

    @log_call
    def create(self, ctx, abstract_transaction: AbstractTransaction) -> object:
        session: Session= ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        admin_id = ctx.get(CTX_ADMIN).id
        author_ref = session.query(Adherent).filter(Adherent.id == admin_id).one_or_none()
        if not author_ref:
            raise MemberNotFoundError(abstract_transaction.author)

        account_src = None
        if abstract_transaction.src is not None:
            account_src = session.query(Account).filter(Account.id == abstract_transaction.src).one_or_none()
            if not account_src:
                raise AccountNotFoundError(abstract_transaction.src)

        account_dst = None
        if abstract_transaction.dst is not None:
            account_dst = session.query(Account).filter(Account.id == abstract_transaction.dst).one_or_none()
            if not account_dst:
                raise AccountNotFoundError(abstract_transaction.dst)

        method = None
        if abstract_transaction.payment_method is not None:
            method = session.query(PaymentMethod).filter(
                PaymentMethod.id == abstract_transaction.payment_method).one_or_none()
            if not method:
                raise PaymentMethodNotFoundError(abstract_transaction.payment_method)

        transaction = SQLTransaction(
            src_account=account_src,
            dst_account=account_dst,
            value=abstract_transaction.value,
            name=abstract_transaction.name,
            timestamp=now,
            attachments="",
            payment_method=method,
            author=author_ref,
            pending_validation=abstract_transaction.pending_validation if abstract_transaction.pending_validation else False
        )

        with track_modifications(ctx, session, transaction):
            session.add(transaction)
        session.flush()

        return _map_transaction_sql_to_entity(transaction)

    def update(self, ctx, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    @log_call
    def validate(self, ctx, id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query= session.query(SQLTransaction)
        query= query.filter(SQLTransaction.id == id)

        transaction = query.one_or_none()
        if transaction is None:
            raise TransactionNotFoundError(str(id))

        with track_modifications(ctx, session, transaction):
            transaction.pending_validation = False
        session.flush()

    @log_call
    def delete(self, ctx, object_id) -> None:
        session: Session = ctx.get(CTX_SQL_SESSION)

        transaction = session.query(SQLTransaction).filter(SQLTransaction.id == object_id).one_or_none()

        if transaction is None:
            raise TransactionNotFoundError(object_id)

        with track_modifications(ctx, session, transaction):
            session.delete(transaction)
        session.flush()
    

def _map_transaction_sql_to_entity(t: SQLTransaction) -> Transaction:
    """
    Map a Transaction object from SQLAlchemy to a Transaction (from the entity folder/layer).
    """
    return Transaction(
        id=t.id,
        src=t.src_account.id,
        dst=t.dst_account.id,
        timestamp=str(t.timestamp),
        name=t.name,
        value=t.value,
        payment_method=t.payment_method.id,
        attachments=[],
        author=t.author.id,
        pending_validation=t.pending_validation
    )

def _map_transaction_sql_to_abstract_entity(t: SQLTransaction) -> AbstractTransaction:
    """
    Map a Transaction object from SQLAlchemy to a Transaction (from the entity folder/layer).
    """
    return AbstractTransaction(
        id=t.id,
        src=t.src_account.id,
        dst=t.dst_account.id,
        timestamp=str(t.timestamp),
        name=t.name,
        value=t.value,
        payment_method=t.payment_method.id,
        attachments=[],
        author=t.author.id,
        pending_validation=t.pending_validation
    )
