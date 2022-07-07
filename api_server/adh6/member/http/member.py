# coding=utf-8
"""
Contain all the http http_api functions.
"""
from typing import Dict, List, Optional, Tuple, Any

from connexion import NoContent

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractMember, Member, Membership, AbstractMembership
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.http_handler import DefaultHandler
from adh6.default.util.error import handle_error
from adh6.default.util.serializer import serialize_response, deserialize_request
from adh6.member.member_manager import MemberManager
from adh6.util.context import log_extra
from adh6.util.log import LOG


class MemberHandler(DefaultHandler):
    def __init__(self, member_manager: MemberManager):
        super().__init__(Member, AbstractMember, member_manager)
        self.member_manager = member_manager

    @with_context
    @log_call
    def post(self, ctx, body):
        try:
            body['id'] = 0  # Set a dummy id to pass the initial validation
            to_create = deserialize_request(body, self.entity_class)
            return serialize_response(self.member_manager.new_member(ctx, to_create)), 201
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def put(self, ctx, id_, body):
        try:
            body['id'] = id_  # Set a dummy id to pass the initial validation
            to_update = deserialize_request(body, self.entity_class)
            self.member_manager.update_member(ctx, id_, to_update, True)
            return NoContent, 201
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def patch(self, ctx, id_, body):
        try:
            body['id'] = id_  # Set a dummy id to pass the initial validation
            to_update = deserialize_request(body, self.abstract_entity_class)
            self.member_manager.update_member(ctx, id_, to_update, False)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def mailinglist_put(self, ctx, id_: int, body: int):
        LOG.debug("http_member_put_mailinglist_called", extra=log_extra(ctx, id=id_, request=body))
        try:
            self.member_manager.update_mailinglist(ctx, id_, body)
            return None, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def membership_post(self, ctx, id_: int, body: dict):
        """ Add a membership record in the database """
        LOG.debug("http_member_post_membership_called", extra=log_extra(ctx, id=id_, request=body))

        try:
            if 'uuid' not in body:
                body['uuid'] = "123e4567-e89b-12d3-a456-426614174000"
            to_create: AbstractMembership = deserialize_request(body, AbstractMembership)

            created_membership = self.member_manager.new_membership(ctx, id_, to_create)
            return serialize_response(created_membership), 200  # 200 OK
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
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
    @log_call
    def statuses_search(self, ctx, id_: int):
        try:
            return serialize_response(self.member_manager.get_statuses(ctx, id_)), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def membership_search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None, only: Optional[List[str]]=None):
        try:
            def remove(entity: Dict[str, Any]) -> Dict[str, Any]:
                if only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id", "__typename"]:
                            del entity[k]
                return entity

            filter_ = deserialize_request(filter_, AbstractMembership)
            result, total_count = self.member_manager.membership_search(ctx, limit=limit, offset=offset, terms=terms, filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(remove, map(serialize_response, result)))
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def get_latest_membership(self, ctx, id_: int):
        try:
            membership: Membership = self.member_manager.get_latest_membership(ctx, id_)
            LOG.debug("get_latest_membership", extra=log_extra(ctx, membership_uuid=membership.uuid))
            return serialize_response(membership), 200
        except Exception as e:
            LOG.debug("get_latest_membership_error", extra=log_extra(ctx,error=str(e)))
            return handle_error(ctx, e)

    @with_context
    @log_call
    def membership_patch(self, ctx, id_, uuid, body):
        try:
            LOG.debug("membership_patch_called", extra=log_extra(ctx, body=body, uuid=uuid, id=id_))
            body['uuid'] = uuid
            to_update: AbstractMembership = deserialize_request(body, AbstractMembership)
            self.member_manager.change_membership(ctx, id_, uuid, to_update)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def membership_validate(self, ctx, id_: int, uuid: str, free: bool = False):
        try:
            self.member_manager.validate_membership(ctx, id_, uuid, free)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def charter_get(self, ctx, id_, charter_id) -> Tuple[Any, int]:
        try:
            return self.member_manager.get_charter(ctx, id_, charter_id), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def charter_put(self, ctx, id_, charter_id) -> Tuple[Any, int]:
        try:
            self.member_manager.update_charter(ctx, id_, charter_id)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)
