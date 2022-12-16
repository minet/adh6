import typing as t

from connexion import NoContent
from adh6.authentication import Roles
from adh6.decorator import log_call, with_context
from adh6.exceptions import UnauthorizedError
from adh6.context import get_user, get_roles

from ..mailinglist_manager import MailinglistManager
from ..member_manager import MemberManager


class MailinglistHandler:
    def __init__(self, mailinglist_manager: MailinglistManager, member_manager: MemberManager) -> None:
        self.mailinglist_manager = mailinglist_manager
        self.member_manager = member_manager

    @with_context
    @log_call
    def member_get(self, id_: int):
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        member = self.member_manager.get_by_id(id_)
        return self.mailinglist_manager.get_member_mailinglist(member=member), 200

    @with_context
    @log_call
    def member_put(self, id_: int, body: t.Dict[str, int]):
        if get_user() != id_ and Roles.ADMIN_WRITE.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        member = self.member_manager.get_by_id(id_)
        self.mailinglist_manager.update_member_mailinglist(member=member, value=body['value'])
        return NoContent, 204

    @with_context
    @log_call
    def search(self, value: int):
        return self.mailinglist_manager.get_members(value), 200
