# coding=utf-8
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.account_manager import AccountManager
from src.use_case.cashbox_manager import CashboxManager
from src.util.context import log_extra
from src.util.log import LOG


class TreasuryHandler:
    def __init__(self, cashbox_manager: CashboxManager,
                 account_manager: AccountManager):
        self.cashbox_manager = cashbox_manager
        self.account_manager = account_manager

    @with_context
    @require_sql
    def get_bank(self, ctx):
        """ Get the status of MiNET's CAV account. """
        LOG.debug("http_treasury_get_bank_called", extra=log_extra(ctx))
        balance = self.account_manager.get_cav_balance(ctx)
        return {'expectedCav': balance}, 200

    @with_context
    @require_sql
    def post(self, ctx, body):
        return bad_request(), 400  # 400 Bad Request

    @with_context
    @require_sql
    def put(self, ctx, transaction_id, body):
        pass

    @with_context
    @require_sql
    def get_cashbox(self, ctx):
        """ Get the status of the cashbox. """
        LOG.debug("http_treasury_get_cashbox_called", extra=log_extra(ctx))
        fond, coffre = self.cashbox_manager.get_cashbox(ctx)
        return {"fond": fond, "coffre": coffre}, 200
