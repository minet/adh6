from adh6.authentication.enums import Roles
from adh6.context import get_roles, get_user
from adh6.decorator import log_call, with_context
from adh6.exceptions import UnauthorizedError

from ..mailinglist_manager import MailinglistManager


class MailinglistHandler:
    def __init__(self, mailinglist_manager: MailinglistManager) -> None:
        self.mailinglist_manager = mailinglist_manager

    @with_context
    @log_call
    async def member_get(self, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return await self.mailinglist_manager.get_member_mailinglist(id_), 200

    @with_context
    @log_call
    async def member_put(self, id_: int, body: dict[str, int]):
        if get_user() != id_ and Roles.ADMIN_WRITE.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        await self.mailinglist_manager.update_member_mailinglist(id_, body["value"])
        return None, 204

    @with_context
    @log_call
    async def search(self, value: int):
        return await self.mailinglist_manager.get_members(value), 200
