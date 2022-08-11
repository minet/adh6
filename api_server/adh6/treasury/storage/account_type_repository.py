# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity.account_type import AccountType
from adh6.exceptions import AccountTypeNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import AccountType as SQLAccountType
from adh6.treasury.interfaces.account_type_repository import AccountTypeRepository


class AccountTypeSQLRepository(AccountTypeRepository):
    @log_call
    def search_by(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Optional[str] = None) -> Tuple[List[AccountType], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLAccountType)

        if terms:
            query = query.filter(SQLAccountType.name.contains(terms))

        count = query.count()
        query = query.order_by(SQLAccountType.id.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_account_type_sql_to_entity, r)), count

    @log_call
    def get_by_id(self, ctx, object_id: int) -> AccountType:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLAccountType).filter(SQLAccountType.id == object_id).one_or_none()
        if obj is None:
            raise AccountTypeNotFoundError(object_id)
        return _map_account_type_sql_to_entity(obj)


def _map_account_type_sql_to_entity(a) -> AccountType:
    """
    Map an AccountType object from SQLAlchemy to an AccountType (from the entity folder/layer).
    """
    return AccountType(
        id=a.id,
        name=a.name,
    )
