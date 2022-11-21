from connexion import NoContent
from adh6.authentication import Roles
from adh6.decorator import with_context
from adh6.exceptions import UnauthorizedError
from adh6.context import get_roles, get_user

from ..charter_manager import CharterManager


class CharterHandler:
    def __init__(self, charter_manager: CharterManager) -> None:
        self.charter_manager = charter_manager

    @with_context
    def member_search(self, charter_id: int):
        result, total_count = self.charter_manager.get_members(charter_id)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    def member_post(self, charter_id: int, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        self.charter_manager.sign(charter_id, id_)
        return NoContent, 201

    @with_context
    def member_get(self, charter_id: int, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.charter_manager.get(charter_id, id_), 200
