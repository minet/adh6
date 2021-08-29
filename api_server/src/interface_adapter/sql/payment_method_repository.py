# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
from typing import List, Tuple

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, CTX_SQL_SESSION
from src.entity.payment_method import PaymentMethod
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import PaymentMethod as SQLPaymentMethod
from src.use_case.interface.payment_method_repository import PaymentMethodRepository


class PaymentMethodSQLRepository(PaymentMethodRepository):

    @log_call
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: PaymentMethod = None) -> Tuple[List[PaymentMethod], int]:
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLPaymentMethod)

        if filter_ is not None:
            if filter_.id:
                q = q.filter(SQLPaymentMethod.id == filter_.id)
            if filter_.name:
                q = q.filter(SQLPaymentMethod.name.contains(filter_.name))
        if terms:
            q = q.filter(SQLPaymentMethod.name.contains(terms))

        count = q.count()
        q = q.order_by(SQLPaymentMethod.id.asc())
        q = q.offset(offset)
        q = q.limit(limit)
        r = q.all()

        return list(map(_map_payment_method_sql_to_entity, r)), count


def _map_payment_method_sql_to_entity(a) -> PaymentMethod:
    """
    Map an PaymentMethod object from SQLAlchemy to an PaymentMethod (from the entity folder/layer).
    """
    return PaymentMethod(
        id=a.id,
        name=a.name,
    )
