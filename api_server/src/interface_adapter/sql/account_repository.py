# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from sqlalchemy import func, case, or_
from typing import List

from src.constants import CTX_SQL_SESSION
from src.entity.account import Account
from src.exceptions import AccountNotFoundError
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Account as SQLAccount, Transaction
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.account_repository import AccountRepository
from src.util.context import log_extra
from src.util.log import LOG


class AccountSQLRepository(AccountRepository):
    """
    Represent the interface to the SQL database.
    """

    def create_account(self, ctx, name=None, actif=None, type=None, creation_date=None, compte_courant=False, pinned=False):
        """
        Create an account.

        :raise AccountTypeNotFound ?
        """

        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_account_repository_create_account_called", extra=log_extra(ctx, name=name, type=type))

        now = datetime.now()

        account = SQLAccount(
            name=name,
            actif=actif,
            type=type,
            creation_date=now,
            compte_courant=compte_courant,
            pinned=pinned
        )

        with track_modifications(ctx, s, account):
            s.add(account)

        return account

    def search_account_by(self, ctx, limit=None, offset=None, account_id=None, terms=None, pinned=None, compte_courant=None) -> (List[Account], int):
        """
        Search for an account.
        """
        LOG.debug("sql_account_repository_search_called", extra=log_extra(ctx, account_id=account_id, terms=terms))
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLAccount,
                    func.sum(case(value=Transaction.src, whens={
                        SQLAccount.id: -Transaction.value
                    }, else_=Transaction.value)).label("balance")).group_by(SQLAccount.id)

        q = q.join(Transaction, or_(Transaction.src == SQLAccount.id, Transaction.dst == SQLAccount.id))

        if pinned:
            q = q.filter(SQLAccount.pinned == pinned)
        if compte_courant:
            q = q.filter(SQLAccount.compte_courant == compte_courant)
        if account_id:
            q = q.filter(SQLAccount.id == account_id)
        if terms:
            q = q.filter(SQLAccount.name.contains(terms))

        count = q.count()
        q = q.order_by(SQLAccount.creation_date.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(lambda x: _map_account_sql_to_entity(x, True), r)), count

    def update_account(self, ctx, name=None, type=None, actif=None, creation_date=None, compte_courant=False, pinned=False,
                       account_id=None) -> None:
        """
        Update an account.
        Will raise (one day) AccountNotFound
        """
        s = ctx.get(CTX_SQL_SESSION)
        LOG.debug("sql_account_repository_update_account_called", extra=log_extra(ctx, account_id=account_id,
                                                                                  actif=actif))

        account = _get_account_by_id(s, account_id)
        if account is None:
            raise AccountNotFoundError(account_id)

        with track_modifications(ctx, s, account):
            account.name = name or account.name
            account.type = type or account.type
            account.actif = actif
            account.creation_date = creation_date or account.creation_date
            account.compte_courant = compte_courant
            account.pinned = pinned


def _map_account_sql_to_entity(a, has_balance=False) -> Account:
    """
    Map a Account object from SQLAlchemy to a Account (from the entity folder/layer).
    """
    if has_balance:
        (a, balance) = a
    return Account(
        name=a.name,
        actif=a.actif,
        type=a.type,
        creation_date=a.creation_date,
        account_id=a.id,
        adherent=_map_member_sql_to_entity(a.adherent) if a.adherent else None,
        balance=balance if has_balance else None,
        compte_courant=a.compte_courant,
        pinned=a.pinned
    )


def _get_account_by_id(s, id) -> SQLAccount:
    return s.query(SQLAccount).filter(SQLAccount.id == id).one_or_none()
