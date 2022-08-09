from typing import Dict
from connexion import NoContent
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.exceptions import UnauthorizedError
from adh6.member.mailinglist_manager import MailinglistManager


class MailinglistHandler:
    def __init__(self, mailinglist_manager: MailinglistManager) -> None:
        self.mailinglist_manager = mailinglist_manager

    @with_context
    @log_call
    def member_get(self, ctx, id_: int):
        try:
            if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            return self.mailinglist_manager.get_member_mailinglist(ctx, id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def member_put(self, ctx, id_: int, body: Dict[str, int]):
        try:
            if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            self.mailinglist_manager.update_member_mailinglist(ctx, id_, body['value'])
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def search(self, ctx, value: int):
        try: 
            return self.mailinglist_manager.get_members(ctx, value), 200
        except Exception as e:
            return handle_error(ctx, e)
