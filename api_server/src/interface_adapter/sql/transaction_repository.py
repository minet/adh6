# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List

from sqlalchemy.orm import aliased

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractTransaction
from src.entity.transaction import Transaction
from src.exceptions import AccountNotFoundError, PaymentMethodNotFoundError, AdminNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.account_repository import _map_account_sql_to_entity
from src.use_case.decorator.handles import Handles
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Admin as SQLAdmin
from src.interface_adapter.sql.model.models import Transaction as SQLTransaction, Account, PaymentMethod, Adherent
from src.interface_adapter.sql.payment_method_repository import _map_payment_method_sql_to_entity
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.transaction_repository import TransactionRepository


class TransactionSQLRepository(TransactionRepository):

    @Handles.SEARCH
    @log_call
    def search_transaction_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                              filter_: AbstractTransaction = None) \
            -> (List[Transaction], int):
        s = ctx.get(CTX_SQL_SESSION)

        account_source = aliased(Account)
        account_destination = aliased(Account)

        q = s.query(SQLTransaction)
        q = q.join(account_source, account_source.id == SQLTransaction.dst)
        q = q.join(account_destination, account_destination.id == SQLTransaction.src)

        if filter_.id is not None:
            q = q.filter(SQLTransaction.id == filter_.id)
        if terms:
            q = q.filter(
                (SQLTransaction.name.contains(terms))
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

    @Handles.CREATE
    @log_call
    def create_transaction(self, ctx, author=None, abstract_transaction: AbstractTransaction = None):
        """
        Create a transaction.

        :raise AccountNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        author_ref = None
        if author is not None:
            author_ref = s.query(Adherent).join(SQLAdmin) \
                .filter(Adherent.login == author) \
                .filter(Adherent.admin is not None).one_or_none()
            if not author_ref:
                raise AdminNotFoundError(author)

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
        return _map_transaction_sql_to_entity(transaction)

    @Handles.UPDATE
    @log_call
    def update_transaction(self, ctx, transaction_to_update, override=False):
        pass


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
        author=_map_member_sql_to_entity(t.author)
    )
