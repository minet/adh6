# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Optional, Tuple, Union

from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity.product import Product
from adh6.decorator import log_call

from .models import Product as SQLProduct
from ..interfaces import ProductRepository


class ProductSQLRepository(ProductRepository):
    """
    Represent the interface to the SQL database.
    """
    @log_call
    def get_by_id(self, ctx, object_id: int) -> Union[Product, None]:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLProduct).filter(SQLProduct.id == object_id).one_or_none()
        return _map_product_sql_to_entity(obj) if obj else obj

    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms: Optional[str]=None) -> Tuple[List[Product], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLProduct)

        if terms:
            query = query.filter(SQLProduct.name.contains(terms))

        count = query.count()
        query = query.order_by(SQLProduct.id.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return [_map_product_sql_to_entity(i) for i in r], count

def _map_product_sql_to_entity(p: SQLProduct) -> Product:
    """
    Map a Product object from SQLAlchemy to a Product (from the entity folder/layer).
    """
    return Product(
        id=p.id,
        name=p.name,
        buying_price=p.buying_price,
        selling_price=p.selling_price,
    )
