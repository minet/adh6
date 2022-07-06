# coding=utf-8
from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.plugins.treasury.use_cases.account_type_manager import AccountTypeManager


class AccountTypeHandler:
    def __init__(self, account_type_manager: AccountTypeManager):
        self.account_type_manager = account_type_manager

    @with_context
    @require_sql
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None):
        try:
            result, total_count = self.account_type_manager.search(ctx, limit=limit, offset=offset, terms=terms)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(serialize_response, result))
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def get(self, ctx, id_: int):
        try:
            return serialize_response(self.account_type_manager.get_by_id(ctx, id=id_)), 200
        except Exception as e:
            return handle_error(ctx, e)

