"""
Implements everything related to actions on the SQL database.
"""

from datetime import datetime

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractAccount, Account
from adh6.exceptions import AccountNotFoundError, MemberNotFoundError
from adh6.member.storage.models import Adherent

from ..interfaces import AccountRepository
from .models import Account as SQLAccount, AccountType, Transaction


class AccountSQLRepository(AccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_by(
        self,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        terms=None,
        filter_: AbstractAccount | None = None,
    ) -> tuple[list[Account], int]:
        stmt = (
            select(
                SQLAccount,
                func.sum(
                    case(
                        (Transaction.src == SQLAccount.id, -Transaction.value),
                        else_=Transaction.value,
                    )
                ).label("balance"),
            )
            .outerjoin(
                Transaction,
                or_(Transaction.src == SQLAccount.id, Transaction.dst == SQLAccount.id),
            )
            .group_by(SQLAccount.id)
        )

        if terms:
            stmt = stmt.where(SQLAccount.name.contains(terms))
        if filter_:
            if filter_.id is not None:
                stmt = stmt.where(SQLAccount.id == filter_.id)
            if filter_.name:
                stmt = stmt.where(SQLAccount.name.contains(filter_.name))
            if filter_.compte_courant is not None:
                stmt = stmt.where(SQLAccount.compte_courant == filter_.compte_courant)
            if filter_.actif is not None:
                stmt = stmt.where(SQLAccount.actif == filter_.actif)
            if filter_.pinned is not None:
                stmt = stmt.where(SQLAccount.pinned == filter_.pinned)
            if filter_.account_type is not None:
                stmt = stmt.where(SQLAccount.type == filter_.account_type)
            if filter_.member is not None:
                stmt = stmt.where(SQLAccount.adherent_id == filter_.member)

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLAccount.creation_date.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.all()

        return [_map_account_sql_to_entity(item, True) for item in r], count  # type: ignore  # TODO: typing

    async def get_by_id(self, object_id: int) -> Account | None:
        stmt = (
            select(
                SQLAccount,
                func.sum(
                    case(
                        (Transaction.src == SQLAccount.id, -Transaction.value),  # type: ignore  # TODO: typing / deprecated
                        else_=Transaction.value,
                    )
                ).label("balance"),  # type: ignore  # TODO: typing / deprecated
            )
            .outerjoin(
                Transaction,
                or_(Transaction.src == SQLAccount.id, Transaction.dst == SQLAccount.id),
            )
            .where(SQLAccount.id == object_id)
        )

        result = await self.session.execute(stmt)
        obj = result.one()  # type: ignore  # TODO: typing
        return _map_account_sql_to_entity(obj, True) if obj[0] else None  # type: ignore  # TODO: typing

    async def create(self, abstract_account: Account) -> object:
        now = datetime.now()

        # Query account type
        account_type_stmt = select(AccountType)
        if abstract_account.account_type is not None:
            account_type_stmt = account_type_stmt.where(AccountType.id == abstract_account.account_type)
        else:
            account_type_stmt = account_type_stmt.where(AccountType.name == "Adherent")

        account_type = await self.session.scalar(account_type_stmt)
        if account_type is None:
            raise AccountNotFoundError(abstract_account.account_type)

        adherent = None
        if abstract_account.member is not None:
            adherent_stmt = select(Adherent).where(Adherent.id == abstract_account.member)
            adherent = await self.session.scalar(adherent_stmt)
            if not adherent:
                raise MemberNotFoundError(abstract_account.member)

        account = SQLAccount(
            name=abstract_account.name,
            actif=abstract_account.actif,
            type=account_type.id,
            creation_date=now,
            compte_courant=abstract_account.compte_courant,
            pinned=abstract_account.pinned,
            adherent_id=adherent.id if adherent else None,
        )
        self.session.add(account)
        await self.session.flush()
        mapped_account = _map_account_sql_to_entity(account)
        return mapped_account

    async def update(self, object_to_update: AbstractAccount, override=False) -> object:
        raise NotImplementedError  # pragma: no cover

    async def delete(self, object_id) -> None:
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
        accountType=a.type,
        creationDate=a.creation_date,
        member=a.adherent_id if a.adherent_id else None,
        balance=balance or 0,
        pendingBalance=balance or 0,
        compteCourant=a.compte_courant,
        pinned=a.pinned,
    )


def _map_account_sql_to_abstract_entity(a: SQLAccount, has_balance=False) -> AbstractAccount:
    """
    Map a, Account object from SQLAlchemy to an Account (from the entity folder/layer).
    """
    balance = None
    if has_balance:
        (a, balance) = a  # type: ignore  # TODO: typing
    return AbstractAccount(
        id=a.id,
        name=a.name,
        actif=a.actif,
        accountType=a.type,
        creationDate=a.creation_date,
        member=a.adherent_id if a.adherent_id else None,
        balance=balance or 0,
        pendingBalance=balance or 0,
        compteCourant=a.compte_courant,
        pinned=a.pinned,
    )
