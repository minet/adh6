# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime
from typing import List

from sqlalchemy import func, case, or_

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractAccount
from src.entity.account import Account
from src.entity.null import Null
from src.exceptions import AccountNotFoundError, MemberNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Account as SQLAccount, Transaction, AccountType, Adherent
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.account_repository import AccountRepository


class AccountSQLRepository(AccountRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractAccount = None) -> (List[Account], int):
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLAccount,
                    func.sum(case(value=Transaction.src, whens={
                        SQLAccount.id: -Transaction.value
                    }, else_=Transaction.value)).label("balance")).group_by(SQLAccount.id)
        q = q.join(AccountType, AccountType.id == SQLAccount.type)
        q = q.join(Adherent, Adherent.id == SQLAccount.adherent_id)
        q = q.join(Transaction, or_(Transaction.src == SQLAccount.id, Transaction.dst == SQLAccount.id))

        if terms:
            q = q.filter(SQLAccount.name.contains(terms))
        if filter_:
            if filter_.id is not None:
                q = q.filter(SQLAccount.id == filter_.id)
            if filter_.name:
                q = q.filter(SQLAccount.name.contains(filter_.name))
            if filter_.compte_courant is not None:
                q = q.filter(SQLAccount.compte_courant == filter_.compte_courant)
            if filter_.actif is not None:
                q = q.filter(SQLAccount.actif == filter_.actif)
            if filter_.pinned is not None:
                q = q.filter(SQLAccount.pinned == filter_.pinned)

        count = q.count()
        q = q.order_by(SQLAccount.creation_date.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(lambda item: _map_account_sql_to_entity(item, True), r)), count

    @log_call
    def create(self, ctx, abstract_account: Account) -> object:
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        account_type = None
        if abstract_account.account_type is not None:
            account_type = s.query(AccountType).filter(AccountType.id == abstract_account.account_type).one_or_none()
            if not account_type:
                raise AccountNotFoundError(abstract_account.account_type)

        adherent = None
        if abstract_account.member is not None:
            adherent = s.query(Adherent).filter(Adherent.id == abstract_account.member).one_or_none()
            if not adherent:
                raise MemberNotFoundError(abstract_account.member)

        account = SQLAccount(
            name=abstract_account.name,
            actif=abstract_account.actif,
            type=account_type,
            creation_date=now,
            compte_courant=abstract_account.compte_courant,
            pinned=abstract_account.pinned,
            adherent=adherent
        )

        with track_modifications(ctx, s, account):
            s.add(account)

        return _map_account_sql_to_entity(account)

    @log_call
    def update(self, ctx, object_to_update: AbstractAccount, override=False) -> object:
        raise NotImplementedError

    @log_call
    def delete(self, ctx, object_id) -> None:
        raise NotImplementedError


def _map_account_sql_to_entity(a, has_balance=False) -> Account:
    """
    Map a, Account object from SQLAlchemy to an Account (from the entity folder/layer).
    """
    balance = None
    if has_balance:
        (a, balance) = a
    return Account(
        id=a.id,
        name=a.name,
        actif=a.actif,
        account_type=a.type,
        creation_date=a.creation_date,
        member=_map_member_sql_to_entity(a.adherent) if a.adherent else Null(),
        balance=balance or 0,
        pending_balance=balance or 0,
        compte_courant=a.compte_courant,
        pinned=a.pinned
    )
