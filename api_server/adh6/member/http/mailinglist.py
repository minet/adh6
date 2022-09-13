from typing import Dict
from connexion import NoContent
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES
from adh6.decorator import log_call, with_context
from adh6.exceptions import UnauthorizedError

from ..mailinglist_manager import MailinglistManager


class MailinglistHandler:
    def __init__(self, mailinglist_manager: MailinglistManager) -> None:
        self.mailinglist_manager = mailinglist_manager

    @with_context
    @log_call
    def member_get(self, ctx, id_: int):
        if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.mailinglist_manager.get_member_mailinglist(ctx, id_), 200

    @with_context
    @log_call
    def member_put(self, ctx, id_: int, body: Dict[str, int]):
        if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource")
        self.mailinglist_manager.update_member_mailinglist(ctx, id_, body['value'])
        return NoContent, 204

    @with_context
    @log_call
    def search(self, ctx, value: int):
        return self.mailinglist_manager.get_members(ctx, value), 200
