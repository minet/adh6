# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.account_type import AccountType
from src.exceptions import AccountTypeNotFoundError, PaymentMethodNotFoundError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import AccountType as SQLAccountType
from src.use_case.interface.account_type_repository import AccountTypeRepository


class AccountTypeSQLRepository(AccountTypeRepository):
    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[AccountType] = None) -> Tuple[List[AccountType], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLAccountType)

        if filter_:
            if filter_.id:
                query = query.filter(SQLAccountType.id == filter_.id)
            if filter_.name:
                query = query.filter(SQLAccountType.name.contains(filter_.name))
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

    def create(self, ctx, object_to_create: AccountType) -> AccountType:
        raise NotImplementedError

    def update(self, ctx, object_to_update: AccountType, override: bool = False) -> AccountType:
        raise NotImplementedError

    def delete(self, ctx, object_id: int) -> AccountType:
        raise NotImplementedError


def _map_account_type_sql_to_entity(a) -> AccountType:
    """
    Map an AccountType object from SQLAlchemy to an AccountType (from the entity folder/layer).
    """
    return AccountType(
        id=a.id,
        name=a.name,
    )
