# coding=utf-8
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.account_manager import AccountManager
from src.use_case.caisse_manager import TreasuryManager
from src.util.context import log_extra
from src.util.log import LOG


class TreasuryHandler:
    def __init__(self, treasury_manager: TreasuryManager,
                 account_manager: AccountManager):
        self.treasury_manager = treasury_manager
        self.account_manager = account_manager

    @with_context
    @require_sql
    @auth_regular_admin
    def caisse_search(self, ctx):
        """ Get the status of the caisse. """
        LOG.debug("http_treasury_caisse_search_called", extra=log_extra(ctx))
        f, c = self.treasury_manager.get_caisse(ctx)
        return {'fond': f, 'coffre': c}, 200

    @with_context
    @require_sql
    @auth_regular_admin
    def bank_search(self, ctx):
        """ Get the status of the caisse. """
        LOG.debug("http_treasury_caisse_search_called", extra=log_extra(ctx))
        balance = self.account_manager.get_cav_balance(ctx)
        return {'balance': balance}, 200

    @with_context
    @require_sql
    @auth_regular_admin
    def bank_get(self, ctx):
        """ Get the status of the caisse. """
        LOG.debug("http_treasury_caisse_search_called", extra=log_extra(ctx))
        balance = self.account_manager.get_cav_balance(ctx)
        return {'expected_cav': balance}, 200

    @with_context
    @require_sql
    @auth_regular_admin
    def post(self, ctx, body):
        return bad_request(), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def put(self, ctx, transaction_id, body):
        pass

    @with_context
    @require_sql
    @auth_regular_admin
    def caisse_get(self, ctx):
        """ Get the status of the caisse. """
        LOG.debug("http_treasury_caisse_get_called", extra=log_extra(ctx))
        fond, coffre = self.treasury_manager.get_caisse(ctx)
        return {fond: fond, coffre: coffre}, 200
