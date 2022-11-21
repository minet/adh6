from connexion import NoContent
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES
from adh6.decorator import with_context
from adh6.exceptions import UnauthorizedError

from ..charter_manager import CharterManager


class CharterHandler:
    def __init__(self, charter_manager: CharterManager) -> None:
        self.charter_manager = charter_manager

    @with_context
    def member_search(self, ctx, charter_id: int):
        result, total_count = self.charter_manager.get_members(ctx, charter_id)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    def member_post(self, ctx, charter_id: int, id_: int):
        if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource")
        self.charter_manager.sign(ctx, charter_id, id_)
        return NoContent, 201

    @with_context
    def member_get(self, ctx, charter_id: int, id_: int):
        if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.charter_manager.get(ctx, charter_id, id_), 200
