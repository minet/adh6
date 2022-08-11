from adh6.constants import CTX_ADMIN
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.exceptions import UnauthorizedError
from adh6.member.member_manager import MemberManager


class ProfileHandler:
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager

    @with_context
    @log_call
    def profile(self, ctx):
        try:
            member, roles = self.member_manager.get_profile(ctx)
            if member.id != ctx.get(CTX_ADMIN):
                raise UnauthorizedError("Not authorize to access this ressource")
            return {"member": member.to_dict(), "roles": roles}, 200
        except Exception as e:
            return handle_error(ctx, e)
