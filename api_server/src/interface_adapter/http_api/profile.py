from src.constants import CTX_ADMIN, CTX_ROLES
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.decorator.auth import auth_required
from src.use_case.member_manager import MemberManager
from src.util.context import log_extra
from src.util.log import LOG


class ProfileHandler:
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager

    @with_context
    @require_sql
    @auth_required()
    def profile(self, ctx):
        LOG.debug("http_profile_called", extra=log_extra(ctx))
        admin = ctx.get(CTX_ADMIN)
        roles = ctx.get(CTX_ROLES)

        return {'admin': {
            'login': admin.username,
            'roles': roles
        }}, 200
