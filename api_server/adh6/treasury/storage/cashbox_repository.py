# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
import decimal
from datetime import datetime
from typing import Tuple

from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION
from adh6.default.decorator.log_call import log_call
from adh6.storage.sql.track_modifications import track_modifications
from adh6.treasury.storage.models import Caisse as SQLCashbox
from adh6.treasury.interfaces.cashbox_repository import CashboxRepository

class CashboxSQLRepository(CashboxRepository):

    @log_call
    def update(self, ctx, value_modifier=None, transaction=None):
        session: Session = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        fond, coffre = self.get(ctx)

        fond += decimal.Decimal(value_modifier)

        cashbox_update = SQLCashbox(
            fond=fond,
            coffre=coffre,
            date=now,
            created_at=now,
            updated_at=now,
            linked_transaction=transaction.id if transaction is not None else None
        )

        with track_modifications(ctx, session, cashbox_update):
            session.add(cashbox_update)
        pass

    @log_call
    def get(self, ctx) -> Tuple[int, int]:
        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SQLCashbox)
        query = query.order_by(SQLCashbox.id.desc())
        query = query.limit(1)
        r = query.all()[0]
        return r.fond, r.coffre
