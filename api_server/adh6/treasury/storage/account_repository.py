# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from datetime import datetime

from sqlalchemy.orm.session import Session
from typing import List, Optional, Tuple, Union

from sqlalchemy import func, case, or_

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractAccount, Account
from adh6.exceptions import AccountNotFoundError, MemberNotFoundError
from adh6.decorator import log_call
from adh6.storage import session
from adh6.member.storage.models import Adherent

from .models import Account as SQLAccount, Transaction, AccountType
from ..interfaces import AccountRepository


class AccountSQLRepository(AccountRepository):
    @log_call
    def search_by(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AbstractAccount] = None) -> Tuple[List[AbstractAccount], int]:
        query = session.query(SQLAccount,
                    func.sum(case(value=Transaction.src, whens={
                        SQLAccount.id: -Transaction.value
                    }, else_=Transaction.value)).label("balance")).group_by(SQLAccount.id)
        query = query.outerjoin(Transaction, or_(Transaction.src == SQLAccount.id, Transaction.dst == SQLAccount.id))

        if terms:
            query = query.filter(SQLAccount.name.contains(terms))
        if filter_:
            if filter_.id is not None:
                query = query.filter(SQLAccount.id == filter_.id)
            if filter_.name:
                query = query.filter(SQLAccount.name.contains(filter_.name))
            if filter_.compte_courant is not None:
                query = query.filter(SQLAccount.compte_courant == filter_.compte_courant)
            if filter_.actif is not None:
                query = query.filter(SQLAccount.actif == filter_.actif)
            if filter_.pinned is not None:
                query = query.filter(SQLAccount.pinned == filter_.pinned)
            if filter_.account_type is not None:
                query = query.filter(SQLAccount.type == filter_.account_type)
            if filter_.member is not None:
                query = query.filter(SQLAccount.adherent_id == filter_.member)

        count = query.count()
        query = query.order_by(SQLAccount.creation_date.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(lambda item: _map_account_sql_to_abstract_entity(item, True), r)), count

    @log_call
    def get_by_id(self, object_id: int) -> Union[AbstractAccount, None]:
        obj = session.query(SQLAccount, func.sum(case(value=Transaction.src, whens={ SQLAccount.id: -Transaction.value }, else_=Transaction.value)).label("balance")).outerjoin(Transaction, or_(Transaction.src == SQLAccount.id, Transaction.dst == SQLAccount.id)).filter(SQLAccount.id == object_id).one_or_none()
        return _map_account_sql_to_abstract_entity(obj, True) if obj[0] else None

    @log_call
    def create(self, abstract_account: Account) -> object:
        now = datetime.now()

        account_type_query = session.query(AccountType)
        if abstract_account.account_type is not None:
            account_type_query = account_type_query.filter(AccountType.id == abstract_account.account_type)
        else:
            account_type_query = account_type_query.filter(AccountType.name == "Adherent")

        account_type = account_type_query.one_or_none()
        if account_type is None:
            raise AccountNotFoundError(abstract_account.account_type)

        adherent = None
        if abstract_account.member is not None:
            adherent = session.query(Adherent).filter(Adherent.id == abstract_account.member).one_or_none()
            if not adherent:
                raise MemberNotFoundError(abstract_account.member)

        account = SQLAccount(
            name=abstract_account.name,
            actif=abstract_account.actif,
            type=account_type.id,
            creation_date=now,
            compte_courant=abstract_account.compte_courant,
            pinned=abstract_account.pinned,
            adherent_id=adherent.id if adherent else None
        )
        session.add(account)
        session.flush()
        return _map_account_sql_to_entity(account)

    @log_call
    def update(self, object_to_update: AbstractAccount, override=False) -> object:
        raise NotImplementedError  # pragma: no cover

    @log_call
    def delete(self, object_id) -> None:
        raise NotImplementedError  # pragma: no cover


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
        member=a.adherent_id if a.adherent_id else None,
        balance=balance or 0,
        pending_balance=balance or 0,
        compte_courant=a.compte_courant,
        pinned=a.pinned
    )
def _map_account_sql_to_abstract_entity(a: SQLAccount, has_balance=False) -> AbstractAccount:
    """
    Map a, Account object from SQLAlchemy to an Account (from the entity folder/layer).
    """
    balance = None
    if has_balance:
        (a, balance) = a
    return AbstractAccount(
        id=a.id,
        name=a.name,
        actif=a.actif,
        account_type=a.type,
        creation_date=a.creation_date,
        member=a.adherent_id if a.adherent_id else None,
        balance=balance or 0,
        pending_balance=balance or 0,
        compte_courant=a.compte_courant,
        pinned=a.pinned
    )
