# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Tuple

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.product import Product
from src.exceptions import ProductNotFoundError
from src.interface_adapter.sql.model.models import Product as SQLProduct
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.product_repository import ProductRepository
from src.util.context import log_extra
from src.util.log import LOG


class ProductSQLRepository(ProductRepository):
    """
    Represent the interface to the SQL database.
    """

    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: Product = None) -> Tuple[List[Product], int]:
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLProduct)

        if filter_ is not None:
            if filter_.id:
                q = q.filter(SQLProduct.id == filter_.id)
            if terms:
                q = q.filter(SQLProduct.name.contains(terms))
            if filter_.name:
                q = q.filter(SQLProduct.name.contains(filter_.name))

        count = q.count()
        q = q.order_by(SQLProduct.id.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_product_sql_to_entity, r)), count


def _map_product_sql_to_entity(p) -> Product:
    """
    Map a Product object from SQLAlchemy to a Product (from the entity folder/layer).
    """
    return Product(
        id=p.id,
        name=p.name,
        buying_price=p.buying_price,
        selling_price=p.selling_price,
    )
