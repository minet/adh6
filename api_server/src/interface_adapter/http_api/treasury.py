# coding=utf-8
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import bad_request, handle_error
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
    @log_call
    def get_bank(self, ctx):
        try:
            balance = self.account_manager.get_cav_balance(ctx)
            return {'expectedCav': balance}, 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    def post(self, ctx, body):
        return bad_request(), 400  # 400 Bad Request

    @with_context
    @require_sql
    def put(self, ctx, id_, body):
        pass

    @with_context
    @require_sql
    @log_call
    def get_cashbox(self, ctx):
        try:
            fond, coffre = self.cashbox_manager.get_cashbox(ctx)
            return {"fond": fond, "coffre": coffre}, 200
        except Exception as e:
            return handle_error(ctx, e)
