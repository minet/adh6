# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
import typing as t

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.storage import session
from adh6.entity import AccountType
from adh6.exceptions import AccountTypeNotFoundError
from adh6.decorator import log_call

from .models import AccountType as SQLAccountType
from ..interfaces import AccountTypeRepository


class AccountTypeSQLRepository(AccountTypeRepository):
    @log_call
    def search_by(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: t.Optional[str] = None) -> t.Tuple[t.List[AccountType], int]:
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
    def get_by_id(self, object_id: int) -> AccountType:
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
