# coding=utf-8
import typing as t

from connexion import NoContent
from adh6.authentication import Roles
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

from adh6.entity import AbstractMember, Member, SubscriptionBody, Comment, MemberFilter, MemberBody
from adh6.decorator import log_call, with_context
from adh6.default import DefaultHandler
from adh6.exceptions import NotFoundError, UnauthorizedError
from adh6.context import get_roles, get_user

from ..charter_manager import CharterManager
from ..member_manager import MemberManager
from ..subscription_manager import SubscriptionManager


class MemberHandler(DefaultHandler):
    def __init__(self, member_manager: MemberManager, charter_manager: CharterManager, subscription_manager: SubscriptionManager):
        super().__init__(Member, AbstractMember, member_manager)
        self.member_manager = member_manager
        self.charter_manager = charter_manager
        self.subscription_manager = subscription_manager

    @with_context
    @log_call
    def search(self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: t.Union[str, None] = None, filter_: t.Optional[t.Any] = None):
        filter_ = MemberFilter.from_dict(filter_) if filter_ else None
        result, total_count = self.main_manager.search(limit=limit, offset=offset, terms=terms, filter_=filter_)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    @log_call
    def get(self, id_: int, only: t.Optional[t.List[str]]=None):
        try:
            def remove(entity: t.Any) -> t.Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id"]:
                            del entity[k]
                return entity
            return remove(self.main_manager.get_by_id(id=id_).to_dict()), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def post(self, body):
        return self.member_manager.create(MemberBody.from_dict(body)).id, 201

    @with_context
    @log_call
    def patch(self, id_, body):
        self.member_manager.update(id_, MemberBody.from_dict(body))
        return NoContent, 204

    @with_context
    @log_call
    def subscription_post(self, id_: int, body: dict):
        """ Add a membership record in the database """
        created_membership = self.subscription_manager.create(id_, SubscriptionBody.from_dict(body))
        return created_membership.to_dict(), 200  # 200 OK

    @with_context
    @log_call
    def password_put(self, id_, body):
        """ Set the password of a member. """
        try:
            self.member_manager.change_password(id_, body.get('password'), body.get("hashedPassword"))
            return NoContent, 204  # 204 No Content
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_WRITE.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def logs_search(self, id_, dhcp=False):
        """ Get logs from a member. """
        return self.member_manager.get_logs(id_, dhcp=dhcp), 200

    @with_context
    @log_call
    def statuses_search(self, id_: int):
        try:
            return list(map(lambda x: x.to_dict(), self.member_manager.get_statuses(id_))), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in get_roles():
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def subscription_patch(self, id_, body):
        self.subscription_manager.update(id_, SubscriptionBody.from_dict(body))
        return NoContent, 204

    @with_context
    @log_call
    def subscription_validate(self, id_: int, free: bool = False):
        from adh6.context import get_roles
        if free and not Roles.TRESO_WRITE.value in get_roles():
            raise UnauthorizedError("Impossibilité de faire une cotisation gratuite")
        self.subscription_manager.validate(id_, free)
        self.member_manager.update_subnet(self.member_manager.get_by_id(id_))
        return NoContent, 204

    @with_context
    @log_call
    def charter_get(self, id_, charter_id) -> t.Tuple[t.Any, int]:
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.charter_manager.get(charter_id=charter_id, member_id=id_), 200

    @with_context
    @log_call
    def charter_put(self, id_, charter_id) -> t.Tuple[t.Any, int]:
        if get_user() != id_ and Roles.ADMIN_READ.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        self.charter_manager.sign(charter_id=charter_id, member_id=id_)
        return NoContent, 204

    @with_context
    @log_call
    def comment_put(self, id_, body):
        """ Set the comment of a member. """
        self.member_manager.change_comment(id_, Comment.from_dict(body))
        return NoContent, 204  # 204 No Content

    @with_context
    @log_call
    def comment_search(self, id_):
        return self.member_manager.get_comment(member_id=id_).to_dict(), 200
