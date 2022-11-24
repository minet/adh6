import typing as t

from connexion import NoContent
from adh6.authentication import Roles
from adh6.decorator import log_call, with_context
from adh6.exceptions import UnauthorizedError
from adh6.context import get_user, get_roles

from ..mailinglist_manager import MailinglistManager


class MailinglistHandler:
    def __init__(self, mailinglist_manager: MailinglistManager) -> None:
        self.mailinglist_manager = mailinglist_manager

    @with_context
    @log_call
    def member_get(self, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.mailinglist_manager.get_member_mailinglist(id_), 200

    @with_context
    @log_call
    def member_put(self, id_: int, body: t.Dict[str, int]):
        if get_user() != id_ and Roles.ADMIN_WRITE.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        self.mailinglist_manager.update_member_mailinglist(id_, body['value'])
        return NoContent, 204

    @with_context
    @log_call
    def search(self, value: int):
        return self.mailinglist_manager.get_members(value), 200
