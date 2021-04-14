from src.constants import CTX_ADMIN, CTX_ROLES
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.member_manager import MemberManager
from src.util.context import log_extra
from src.util.log import LOG


class ProfileHandler:
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager

    @with_context
    @require_sql
    @log_call
    def profile(self, ctx):
        try:
            member, roles = self.member_manager.get_profile(ctx)
            return {'member': serialize_response(member)}, 200
        except Exception as e:
            return handle_error(ctx, e)
