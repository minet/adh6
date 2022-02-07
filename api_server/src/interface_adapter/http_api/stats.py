from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.stats_manager import StatsManager
from src.util.context import log_extra
from src.util.log import LOG


class StatsHandler:
    def __init__(self, stats_manager: StatsManager):
        self.stats_manager = stats_manager

    @with_context
    @require_sql
    def stats(self, ctx):
        LOG.debug("http_stats_called", extra=log_extra(ctx))
        return self.stats_manager.get_global_stats(ctx), 200
