"""
Implements everything related to actions on the SQL database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AccountType
from adh6.exceptions import AccountTypeNotFoundError

from ..interfaces import AccountTypeRepository
from .models import AccountType as SQLAccountType


class AccountTypeSQLRepository(AccountTypeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_by(
        self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: str | None = None
    ) -> tuple[list[AccountType], int]:
        stmt = select(SQLAccountType)

        if terms:
            stmt = stmt.where(SQLAccountType.name.contains(terms))

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLAccountType.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return list(map(_map_account_type_sql_to_entity, r)), count

    async def get_by_id(self, object_id: int) -> AccountType:
        stmt = select(SQLAccountType).where(SQLAccountType.id == object_id)
        obj = await self.session.scalar(stmt)
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
