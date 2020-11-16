from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.device_manager import DeviceManager
from src.use_case.member_manager import MemberManager
from src.use_case.stats_manager import StatsManager
from src.use_case.transaction_manager import TransactionManager
from src.util.context import log_extra
from src.util.log import LOG


class StatsHandler:
    def __init__(self, transaction_manager: TransactionManager, device_manager: DeviceManager, member_manager: MemberManager, stats_manager: StatsManager):
        self.transaction_manager = transaction_manager
        self.device_manager = device_manager
        self.member_manager = member_manager
        self.stats_manager = stats_manager

    @with_context
    @require_sql
    def stats(self, ctx):
        LOG.debug("http_stats_called", extra=log_extra(ctx))
        return self.stats_manager.get_global_stats(ctx), 200
