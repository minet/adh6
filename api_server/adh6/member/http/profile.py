from adh6.decorator import log_call, with_context
from adh6.exceptions import UnauthorizedError
from adh6.context import get_user

from ..member_manager import MemberManager


class ProfileHandler:
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager

    @with_context
    @log_call
    def profile(self):
        member, roles = self.member_manager.get_profile()
        if member.id != get_user():
            raise UnauthorizedError("Not authorize to access this ressource")
        return {"member": member.to_dict(), "roles": roles}, 200
