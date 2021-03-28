# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List

from sqlalchemy.orm import aliased

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET, CTX_ADMIN
from src.entity import AbstractTransaction
from src.entity.transaction import Transaction
from src.exceptions import AccountNotFoundError, PaymentMethodNotFoundError, AdminNotFoundError, \
    TransactionNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.account_repository import _map_account_sql_to_entity
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Admin as SQLAdmin
from src.interface_adapter.sql.model.models import Transaction as SQLTransaction, Account, PaymentMethod, Adherent
from src.interface_adapter.sql.payment_method_repository import _map_payment_method_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.transaction_repository import TransactionRepository


class TransactionSQLRepository(TransactionRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractTransaction = None) -> (List[Transaction], int):
        s = ctx.get(CTX_SQL_SESSION)

        account_source = aliased(Account)
        account_destination = aliased(Account)

        q = s.query(SQLTransaction)
        q = q.join(account_source, account_source.id == SQLTransaction.dst)
        q = q.join(account_destination, account_destination.id == SQLTransaction.src)

        if filter_.id is not None:
            q = q.filter(SQLTransaction.id == filter_.id)
        if filter_.payment_method is not None:
            if isinstance(filter_.payment_method, PaymentMethod):
                filter_.payment_method = filter_.payment_method.id
            q = q.filter(SQLTransaction.type == filter_.payment_method)
        if terms:
            q = q.filter(
                (SQLTransaction.name.contains(terms))
            )
        if filter_.pending_validation is not None:
            q = q.filter(
                (SQLTransaction.pending_validation == filter_.pending_validation)
            )
        if filter_.src is not None and filter_.dst is not None and filter_.src == filter_.dst:
            q = q.filter(
                (SQLTransaction.src == filter_.src) |
                (SQLTransaction.dst == filter_.dst)
            )
        elif filter_.src is not None:
            q = q.filter(SQLTransaction.src == filter_.src)
        elif filter_.dst is not None:
            q = q.filter(SQLTransaction.dst == filter_.dst)

        count = q.count()
        q = q.order_by(SQLTransaction.timestamp.desc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_transaction_sql_to_entity, r)), count

    @log_call
    def create(self, ctx, abstract_transaction: AbstractTransaction) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        admin_id = ctx.get(CTX_ADMIN).id
        author_ref = s.query(Adherent).join(SQLAdmin) \
            .filter(Adherent.id == admin_id) \
            .filter(Adherent.admin is not None).one_or_none()
        if not author_ref:
            raise AdminNotFoundError(abstract_transaction.author)

        account_src = None
        if abstract_transaction.src is not None:
            account_src = s.query(Account).filter(Account.id == abstract_transaction.src).one_or_none()
            if not account_src:
                raise AccountNotFoundError(abstract_transaction.src)

        account_dst = None
        if abstract_transaction.dst is not None:
            account_dst = s.query(Account).filter(Account.id == abstract_transaction.dst).one_or_none()
            if not account_dst:
                raise AccountNotFoundError(abstract_transaction.dst)

        method = None
        if abstract_transaction.payment_method is not None:
            method = s.query(PaymentMethod).filter(
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
            pending_validation=False
        )

        with track_modifications(ctx, s, transaction):
            s.add(transaction)
        s.flush()

        return _map_transaction_sql_to_entity(transaction)

    def update(self, ctx, abstract_transaction: AbstractTransaction, override=False) -> object:
        raise NotImplementedError

    @log_call
    def validate(self, ctx, transaction_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLTransaction)
        q = q.filter(SQLTransaction.id == transaction_id)

        transaction = q.one_or_none()
        if transaction is None:
            raise TransactionNotFoundError(str(transaction_id))

        with track_modifications(ctx, s, transaction):
            transaction.pending_validation = False

    @log_call
    def delete(self, ctx, object_id) -> None:
        s = ctx.get(CTX_SQL_SESSION)

        transaction = s.query(SQLTransaction).filter(SQLTransaction.id == object_id).one_or_none()

        if transaction is None:
            raise TransactionNotFoundError(object_id)

        with track_modifications(ctx, s, transaction):
            s.delete(transaction)


def _map_transaction_sql_to_entity(t: SQLTransaction) -> Transaction:
    """
    Map a Transaction object from SQLAlchemy to a Transaction (from the entity folder/layer).
    """
    return Transaction(
        id=t.id,
        src=_map_account_sql_to_entity(t.src_account),
        dst=_map_account_sql_to_entity(t.dst_account),
        timestamp=str(t.timestamp),
        name=t.name,
        value=t.value,
        payment_method=_map_payment_method_sql_to_entity(t.payment_method),
        attachments=[],
        author=_map_member_sql_to_entity(t.author),
        pending_validation=t.pending_validation
    )
