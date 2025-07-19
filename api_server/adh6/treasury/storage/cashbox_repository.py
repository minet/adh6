"""
Implements everything related to actions on the SQL database.
"""

import decimal
from datetime import datetime

from adh6.decorator import log_call
from adh6.storage import db
from adh6.storage.sql.track_modifications import track_modifications

from ..interfaces import CashboxRepository
from .models import Caisse as SQLCashbox


class CashboxSQLRepository(CashboxRepository):
    @log_call
    def update(self, value_modifier=None, transaction=None):
        now = datetime.now()

        fond, coffre = map(decimal.Decimal, self.get())

        fond += decimal.Decimal(value_modifier)

        cashbox_update = SQLCashbox(
            fond=fond,
            coffre=coffre,
            date=now,
            created_at=now,
            updated_at=now,
            linked_transaction=transaction.id if transaction is not None else None,
        )

        with db.sessionmaker.begin() as session, track_modifications(session, cashbox_update):
            session.add(cashbox_update)

    @log_call
    def get(self) -> tuple[float, float]:
        with db.sessionmaker() as session:
            query = session.query(SQLCashbox)
            query = query.order_by(SQLCashbox.id.desc())
            query = query.limit(1)
            r = query.all()[0]
        return r.fond, r.coffre  # type: ignore  # TODO: fix typing
