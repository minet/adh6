from adh6.constants import CTX_ADMIN
from adh6.decorator import log_call, with_context
from adh6.exceptions import UnauthorizedError

from ..member_manager import MemberManager


class ProfileHandler:
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager

    @with_context
    @log_call
    def profile(self, ctx):
        member, roles = self.member_manager.get_profile(ctx)
        if member.id != ctx.get(CTX_ADMIN):
            raise UnauthorizedError("Not authorize to access this ressource")
        return {"member": member.to_dict(), "roles": roles}, 200
