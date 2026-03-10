"""
Implements everything related to actions on the SQL database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity.product import Product

from ..interfaces import ProductRepository
from .models import Product as SQLProduct


class ProductSQLRepository(ProductRepository):
    """
    Represent the interface to the SQL database.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, object_id: int) -> Product | None:
        stmt = select(SQLProduct).where(SQLProduct.id == object_id)
        obj = await self.session.scalar(stmt)
        return _map_product_sql_to_entity(obj) if obj else obj

    async def search_by(
        self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms: str | None = None
    ) -> tuple[list[Product], int]:
        stmt = select(SQLProduct)

        if terms:
            stmt = stmt.where(SQLProduct.name.contains(terms))

        # Count
        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        # Apply ordering and pagination
        stmt = stmt.order_by(SQLProduct.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_product_sql_to_entity(i) for i in r], count


def _map_product_sql_to_entity(p: SQLProduct) -> Product:
    """
    Map a Product object from SQLAlchemy to a Product (from the entity folder/layer).
    """
    return Product(
        id=p.id,
        name=p.name,
        buyingPrice=p.buying_price,
        sellingPrice=p.selling_price,
    )
