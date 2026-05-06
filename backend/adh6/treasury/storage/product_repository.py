"""
Implements everything related to actions on the SQL database.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity.abstract_product import AbstractProduct
from adh6.entity.product import Product
from adh6.exceptions import ProductNotFoundError

from ..interfaces import ProductRepository
from .models import Product as SQLProduct


class ProductSQLRepository(ProductRepository):
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

        count_result = await self.session.execute(stmt)
        count = len(count_result.all())

        stmt = stmt.order_by(SQLProduct.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        r = result.scalars().all()

        return [_map_product_sql_to_entity(i) for i in r], count

    async def create(self, abstract_product: AbstractProduct) -> Product:
        product = SQLProduct(
            name=abstract_product.name,
            buying_price=abstract_product.buying_price or 0,
            selling_price=abstract_product.selling_price,
        )
        self.session.add(product)
        await self.session.flush()
        return _map_product_sql_to_entity(product)

    async def update(self, abstract_product: AbstractProduct, product_id: int) -> None:
        stmt = select(SQLProduct).where(SQLProduct.id == product_id)
        product = await self.session.scalar(stmt)
        if not product:
            raise ProductNotFoundError(product_id)
        if abstract_product.name is not None:
            product.name = abstract_product.name
        if abstract_product.selling_price is not None:
            product.selling_price = abstract_product.selling_price
        if abstract_product.buying_price is not None:
            product.buying_price = abstract_product.buying_price

    async def delete(self, product_id: int) -> None:
        stmt = select(SQLProduct).where(SQLProduct.id == product_id)
        product = await self.session.scalar(stmt)
        if not product:
            raise ProductNotFoundError(product_id)
        await self.session.delete(product)


def _map_product_sql_to_entity(p: SQLProduct) -> Product:
    return Product(
        id=p.id,
        name=p.name,
        buyingPrice=p.buying_price,
        sellingPrice=p.selling_price,
    )
