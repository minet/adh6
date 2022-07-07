# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity.product import AbstractProduct
from adh6.exceptions import ProductNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.models import Product as SQLProduct
from adh6.treasury.interfaces.product_repository import ProductRepository


class ProductSQLRepository(ProductRepository):
    """
    Represent the interface to the SQL database.
    """
    @log_call
    def get_by_id(self, ctx, object_id: int) -> AbstractProduct:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLProduct).filter(SQLProduct.id == object_id).one_or_none()
        if obj is None:
            raise ProductNotFoundError(object_id)
        return _map_product_sql_to_abstract_entity(obj)

    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms: Optional[str]=None) -> Tuple[List[AbstractProduct], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLProduct)

        if terms:
            query = query.filter(SQLProduct.name.contains(terms))

        count = query.count()
        query = query.order_by(SQLProduct.id.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_product_sql_to_abstract_entity, r)), count

def _map_product_sql_to_abstract_entity(p) -> AbstractProduct:
    """
    Map a Product object from SQLAlchemy to a Product (from the entity folder/layer).
    """
    return AbstractProduct(
        id=p.id,
        name=p.name,
        buying_price=p.buying_price,
        selling_price=p.selling_price,
    )
