# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
import decimal
from datetime import datetime

from src.constants import CTX_SQL_SESSION
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.sql.model.models import Caisse as SQLCashbox
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.cashbox_repository import CashboxRepository
from src.util.context import log_extra
from src.util.log import LOG


class CashboxSQLRepository(CashboxRepository):

    @log_call
    def update_cashbox(self, ctx, value_modifier=None, transaction=None):
        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        fond, coffre = self.get_cashbox(ctx)

        fond += decimal.Decimal(value_modifier)

        cashbox_update = SQLCashbox(
            fond=fond,
            coffre=coffre,
            date=now,
            created_at=now,
            updated_at=now,
            transaction=transaction
        )

        with track_modifications(ctx, s, cashbox_update):
            s.add(cashbox_update)
        pass

    @log_call
    def get_cashbox(self, ctx) -> (int, int):
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLCashbox)
        q = q.order_by(SQLCashbox.id.desc())
        q = q.limit(1)
        r = q.all()[0]
        return r.fond, r.coffre