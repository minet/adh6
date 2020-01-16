# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""
import decimal
from datetime import datetime

from src.constants import CTX_SQL_SESSION
from src.interface_adapter.sql.model.models import Caisse as SQLCaisse
from src.interface_adapter.sql.track_modifications import track_modifications
from src.use_case.interface.caisse_repository import CaisseRepository
from src.util.context import log_extra
from src.util.log import LOG


class CaisseSQLRepository(CaisseRepository):

    def update_caisse(self, ctx, value_modifier=None, transaction=None):
        LOG.debug("sql_caisse_repository_update_called", extra=log_extra(ctx, value_modifier=value_modifier))

        s = ctx.get(CTX_SQL_SESSION)

        now = datetime.now()

        fond, coffre = self.get_caisse(ctx)

        fond += decimal.Decimal(value_modifier)

        caisse_update = SQLCaisse(
            fond=fond,
            coffre=coffre,
            date=now,
            created_at=now,
            updated_at=now,
            transaction=transaction
        )

        with track_modifications(ctx, s, caisse_update):
            s.add(caisse_update)
        pass

    def get_caisse(self, ctx) -> (int, int):
        LOG.debug("sql_transaction_repository_search_called", extra=log_extra(ctx))
        s = ctx.get(CTX_SQL_SESSION)

        q = s.query(SQLCaisse)
        q = q.order_by(SQLCaisse.id.desc())
        q = q.limit(1)
        r = q.all()[0]
        return r.fond, r.coffre