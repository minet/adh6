from connexion import NoContent
from adh6.authentication import Roles
from adh6.decorator import with_context, log_call
from adh6.exceptions import UnauthorizedError
from adh6.context import get_roles, get_user

from ..charter_manager import CharterManager
from ..member_manager import MemberManager


class CharterHandler:
    def __init__(self, charter_manager: CharterManager, member_manager: MemberManager) -> None:
        self.charter_manager = charter_manager
        self.member_manager = member_manager

    @with_context
    @log_call
    def member_search(self, charter_id: int):
        result, total_count = self.charter_manager.get_members(charter_id)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    @log_call
    def member_post(self, charter_id: int, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        member = self.member_manager.get_by_id(id_)
        self.charter_manager.sign(charter_id, member)
        return NoContent, 201

    @with_context
    @log_call
    def member_get(self, charter_id: int, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        member = self.member_manager.get_by_id(id_)
        return self.charter_manager.get(charter_id, member), 200
