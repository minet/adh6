from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

from adh6.constants import CTX_SQL_SESSION
from adh6.metrics.interfaces.ping_repository import PingRepository
from adh6.misc.context import log_extra
from adh6.misc.log import LOG


class PingSQLRepository(PingRepository):
    def ping(self, ctx) -> bool:
        LOG.debug("sql_ping", extra=log_extra(ctx))

        session: Session = ctx.get(CTX_SQL_SESSION)
        try:
            result = session.execute('SELECT 42 AS result').fetchall()
            if 1 != len(result):
                return False

            return [(42,)] == result

        except SQLAlchemyError:
            return False
