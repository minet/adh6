# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.account_type import AccountType
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import AccountType as SQLAccountType
from src.use_case.interface.account_type_repository import AccountTypeRepository


class AccountTypeSQLRepository(AccountTypeRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AccountType = None) -> (List[AccountType], int):
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLAccountType)

        if filter_:
            if filter_.id:
                q = q.filter(SQLAccountType.id == filter_.id)
            if filter_.name:
                q = q.filter(SQLAccountType.name.contains(filter_.name))
        if terms:
            q = q.filter(SQLAccountType.name.contains(terms))

        count = q.count()
        q = q.order_by(SQLAccountType.id.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_account_type_sql_to_entity, r)), count


def _map_account_type_sql_to_entity(a) -> AccountType:
    """
    Map an AccountType object from SQLAlchemy to an AccountType (from the entity folder/layer).
    """
    return AccountType(
        id=a.id,
        name=a.name,
    )
