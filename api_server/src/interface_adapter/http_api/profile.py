from src.entity.abstract_member import AbstractMember
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import handle_error
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.member_manager import MemberManager


class ProfileHandler:
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager

    @with_context
    @require_sql
    @log_call
    def profile(self, ctx):
        try:
            admin = self.member_manager.get_profile(ctx)
            if isinstance(admin.member, int):
                l, _ = self.member_manager.search(ctx=ctx, limit=1, filter_ = AbstractMember(username=admin.login))
                admin.member = l[0]
            return {'admin': {
                'login': admin.login,
                'member': serialize_response(admin.member),
                'roles': admin.roles
            }}, 200
        except Exception as e:
            return handle_error(ctx, e)
