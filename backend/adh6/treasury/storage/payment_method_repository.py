"""
Implements everything related to actions on the SQL database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import PaymentMethod
from adh6.exceptions import PaymentMethodNotFoundError

from ..interfaces import PaymentMethodRepository
from .models import PaymentMethod as SQLPaymentMethod


class PaymentMethodSQLRepository(PaymentMethodRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, object_id: int) -> PaymentMethod:
        stmt = select(SQLPaymentMethod).where(SQLPaymentMethod.id == object_id)
        obj = await self.session.scalar(stmt)
        if obj is None:
            raise PaymentMethodNotFoundError(object_id)
        return _map_payment_method_sql_to_entity(obj)

    async def search_by(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        filter_: PaymentMethod | None = None,
    ) -> tuple[list[PaymentMethod], int]:
        stmt = select(SQLPaymentMethod)

        if filter_:
            if filter_.id:
                stmt = stmt.where(SQLPaymentMethod.id == filter_.id)
            if filter_.name:
                stmt = stmt.where(SQLPaymentMethod.name.contains(filter_.name))
        if terms:
            stmt = stmt.where(SQLPaymentMethod.name.contains(terms))

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLPaymentMethod.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return list(map(_map_payment_method_sql_to_entity, r)), count

    def create(self, object_to_create: PaymentMethod) -> PaymentMethod:
        raise NotImplementedError  # pragma: no cover

    def update(self, object_to_update: PaymentMethod, override: bool = False) -> PaymentMethod:
        raise NotImplementedError  # pragma: no cover

    def delete(self, object_id: int) -> PaymentMethod:
        raise NotImplementedError  # pragma: no cover


def _map_payment_method_sql_to_entity(a) -> PaymentMethod:
    """
    Map an PaymentMethod object from SQLAlchemy to an PaymentMethod (from the entity folder/layer).
    """
    return PaymentMethod(
        id=a.id,
        name=a.name,
    )
