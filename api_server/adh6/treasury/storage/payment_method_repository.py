# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm.session import Session

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, CTX_SQL_SESSION
from adh6.entity import PaymentMethod
from adh6.exceptions import PaymentMethodNotFoundError
from adh6.decorator import log_call

from .models import PaymentMethod as SQLPaymentMethod
from ..interfaces import PaymentMethodRepository


class PaymentMethodSQLRepository(PaymentMethodRepository):
    @log_call
    def get_by_id(self, ctx, object_id: int) -> PaymentMethod:
        session: Session = ctx.get(CTX_SQL_SESSION)
        obj = session.query(SQLPaymentMethod).filter(SQLPaymentMethod.id == object_id).one_or_none()
        if obj is None:
            raise PaymentMethodNotFoundError(object_id)
        return _map_payment_method_sql_to_entity(obj)

    @log_call
    def search_by(self, ctx, limit:int=DEFAULT_LIMIT, offset:int=DEFAULT_OFFSET, terms: Optional[str]=None, filter_: Optional[PaymentMethod] = None) -> Tuple[List[PaymentMethod], int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLPaymentMethod)

        if filter_:
            if filter_.id:
                query = query.filter(SQLPaymentMethod.id == filter_.id)
            if filter_.name:
                query = query.filter(SQLPaymentMethod.name.contains(filter_.name))
        if terms:
            query = query.filter(SQLPaymentMethod.name.contains(terms))

        count = query.count()
        query = query.order_by(SQLPaymentMethod.id.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        r = query.all()

        return list(map(_map_payment_method_sql_to_entity, r)), count

    def create(self, ctx, object_to_create: PaymentMethod) -> PaymentMethod:
        raise NotImplementedError  # pragma: no cover

    def update(self, ctx, object_to_update: PaymentMethod, override: bool = False) -> PaymentMethod:
        raise NotImplementedError  # pragma: no cover

    def delete(self, ctx, object_id: int) -> PaymentMethod:
        raise NotImplementedError  # pragma: no cover


def _map_payment_method_sql_to_entity(a) -> PaymentMethod:
    """
    Map an PaymentMethod object from SQLAlchemy to an PaymentMethod (from the entity folder/layer).
    """
    return PaymentMethod(
        id=a.id,
        name=a.name,
    )
