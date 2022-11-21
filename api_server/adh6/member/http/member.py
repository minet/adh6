# coding=utf-8
from typing import List, Optional, Tuple, Any, Union

from connexion import NoContent
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES, DEFAULT_LIMIT, DEFAULT_OFFSET

from adh6.entity import AbstractMember, Member, SubscriptionBody, Comment
from adh6.decorator import log_call, with_context
from adh6.default.http_handler import DefaultHandler
from adh6.exceptions import NotFoundError, UnauthorizedError
from adh6.misc import log_extra, LOG

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
    def search(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Union[str, None] = None, filter_: Optional[Any] = None):
        filter_ = MemberFilter.from_dict(filter_) if filter_ else None
        result, total_count = self.main_manager.search(ctx, limit=limit, offset=offset, terms=terms, filter_=filter_)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return result, 200, headers

    @with_context
    @log_call
    def get(self, ctx, id_: int, only: Optional[List[str]]=None):
        try:
            def remove(entity: Any) -> Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id"]:
                            del entity[k]
                return entity
            return remove(self.main_manager.get_by_id(ctx, id=id_).to_dict()), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES):
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def post(self, ctx, body):
        return self.member_manager.create(ctx, MemberBody.from_dict(body)).id, 201

    @with_context
    @log_call
    def patch(self, ctx, id_, body):
        self.member_manager.update(ctx, id_, MemberBody.from_dict(body))
        return NoContent, 204

    @with_context
    @log_call
    def subscription_post(self, ctx, id_: int, body: dict):
        """ Add a membership record in the database """
        LOG.debug("http_member_post_membership_called", extra=log_extra(ctx, id=id_, request=body))
        created_membership = self.subscription_manager.create(ctx, id_, SubscriptionBody.from_dict(body))
        return created_membership.to_dict(), 200  # 200 OK

    @with_context
    @log_call
    def password_put(self, ctx, id_, body):
        """ Set the password of a member. """
        try:
            self.member_manager.change_password(ctx, id_, body.get('password'), body.get("hashedPassword"))
            return NoContent, 204  # 204 No Content
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES):
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def logs_search(self, ctx, id_, dhcp=False):
        """ Get logs from a member. """
        return self.member_manager.get_logs(ctx, id_, dhcp=dhcp), 200

    @with_context
    @log_call
    def statuses_search(self, ctx, id_: int):
        try:
            return list(map(lambda x: x.to_dict(), self.member_manager.get_statuses(ctx, id_))), 200
        except Exception as e:
            if isinstance(e, NotFoundError) and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES):
                e = UnauthorizedError("cannot access this resource")
            raise e

    @with_context
    @log_call
    def subscription_patch(self, ctx, id_, body):
        self.subscription_manager.update(ctx, id_, SubscriptionBody.from_dict(body))
        return NoContent, 204

    @with_context
    @log_call
    def subscription_validate(self, ctx, id_: int, free: bool = False):
        self.subscription_manager.validate(ctx, id_, free)
        self.member_manager.update_subnet(ctx, id_)
        return NoContent, 204

    @with_context
    @log_call
    def charter_get(self, ctx, id_, charter_id) -> Tuple[Any, int]:
        if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.charter_manager.get(ctx, charter_id=charter_id, member_id=id_), 200

    @with_context
    @log_call
    def charter_put(self, ctx, id_, charter_id) -> Tuple[Any, int]:
        try:
            if ctx.get(CTX_ADMIN) != id_ and Roles.ADMIN_READ.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")
            self.charter_manager.sign(ctx, charter_id=charter_id, member_id=id_)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def comment_put(self, ctx, id_, body):
        """ Set the comment of a member. """
        try:
            self.member_manager.change_comment(ctx, id_, Comment.from_dict(body))
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def comment_search(self, ctx, id_):
        try:
            return self.member_manager.get_comment(ctx, member_id=id_).to_dict(), 200
        except Exception as e:
            return handle_error(ctx, e)
