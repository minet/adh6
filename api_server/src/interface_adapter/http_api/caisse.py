# coding=utf-8
from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.caisse_manager import CaisseManager
from src.util.context import log_extra
from src.util.log import LOG


class CaisseHandler:
    def __init__(self, caisse_manager: CaisseManager):
        self.caisse_manager = caisse_manager

    @with_context
    @require_sql
    @auth_regular_admin
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, account=None, terms=None):
        """ Get the status of the caisse. """
        LOG.debug("http_caisse_get_called", extra=log_extra(ctx))
        f, c = self.caisse_manager.get(ctx)
        return {'fond': f, 'coffre': c}, 200

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
    def get(self, ctx):
        """ Get the status of the caisse. """
        LOG.debug("http_caisse_get_called", extra=log_extra(ctx))
        fond, coffre = self.caisse_manager.get(ctx)
        return {fond: fond, coffre: coffre}, 200
