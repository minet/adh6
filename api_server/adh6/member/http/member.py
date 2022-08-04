# coding=utf-8
"""
Contain all the http http_api functions.
"""
from typing import List, Optional, Tuple, Any, Union

from connexion import NoContent
from adh6.authentication import Method
from adh6.authentication.security import with_security
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

from adh6.entity import AbstractMember, Member, SubscriptionBody
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.http_handler import DefaultHandler
from adh6.default.util.error import handle_error
from adh6.entity.member_body import MemberBody
from adh6.entity.member_filter import MemberFilter
from adh6.member.charter_manager import CharterManager
from adh6.member.member_manager import MemberManager
from adh6.misc.context import log_extra
from adh6.misc.log import LOG


class MemberHandler(DefaultHandler):
    def __init__(self, member_manager: MemberManager, charter_manager: CharterManager):
        super().__init__(Member, AbstractMember, member_manager)
        self.member_manager = member_manager
        self.charter_manager = charter_manager

    @with_context
    @log_call
    def search(self, ctx, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: Union[str, None] = None, filter_: Optional[Any] = None):
        try:
            filter_ = MemberFilter.from_dict(filter_) if filter_ else None
            result, total_count = self.main_manager.search(ctx, limit=limit, offset=offset, terms=terms, filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @with_security(method=Method.READ)
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
            return handle_error(ctx, e)

    @with_context
    @log_call
    def post(self, ctx, body):
        try:
            to_create = MemberBody.from_dict(body)
            return self.member_manager.create(ctx, to_create).to_dict(), 201
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @with_security()
    @log_call
    def patch(self, ctx, id_, body):
        try:
            to_update = MemberBody.from_dict(body)
            self.member_manager.update(ctx, id_, to_update)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def subscription_post(self, ctx, id_: int, body: dict):
        """ Add a membership record in the database """
        LOG.debug("http_member_post_membership_called", extra=log_extra(ctx, id=id_, request=body))

        try:
            to_create = SubscriptionBody.from_dict(body)
            created_membership = self.member_manager.create_subscription(ctx, id_, to_create)
            return created_membership.to_dict(), 200  # 200 OK
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @with_security()
    @log_call
    def password_put(self, ctx, id_, body):
        """ Set the password of a member. """

        try:
            self.member_manager.change_password(ctx, id_, body.get('password'), body.get("hashedPassword"))
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def logs_search(self, ctx, id_, dhcp=False):
        """ Get logs from a member. """
        try:
            return self.member_manager.get_logs(ctx, id_, dhcp=dhcp), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @with_security()
    @log_call
    def statuses_search(self, ctx, id_: int):
        try:
            return list(map(lambda x: x.to_dict(), self.member_manager.get_statuses(ctx, id_))), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def subscription_patch(self, ctx, id_, body):
        try:
            LOG.debug("membership_patch_called", extra=log_extra(ctx, body=body, id=id_))
            to_update = SubscriptionBody.from_dict(body)
            self.member_manager.update_subscription(ctx, id_, to_update)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def subscription_validate(self, ctx, id_: int, free: bool = False):
        try:
            self.member_manager.validate_subscription(ctx, id_, free)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def charter_get(self, ctx, id_, charter_id) -> Tuple[Any, int]:
        try:
            return self.charter_manager.get(ctx, charter_id=charter_id, member_id=id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def charter_put(self, ctx, id_, charter_id) -> Tuple[Any, int]:
        try:
            self.charter_manager.sign(ctx, charter_id=charter_id, member_id=id_)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)
