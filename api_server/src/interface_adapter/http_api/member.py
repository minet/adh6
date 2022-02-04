# coding=utf-8
"""
Contain all the http http_api functions.
"""
from typing import Tuple, Any

from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractMember, Member, Membership, AbstractMembership, membership_request
from src.exceptions import ValidationError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler, _error
from src.interface_adapter.http_api.util.error import bad_request, handle_error
from src.interface_adapter.http_api.util.serializer import serialize_response, deserialize_request
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.member_manager import MemberManager
from src.util.context import log_extra
from src.util.log import LOG


class MemberHandler(DefaultHandler):
    def __init__(self, member_manager: MemberManager):
        super().__init__(Member, AbstractMember, member_manager)
        self.member_manager = member_manager

    @with_context
    @require_sql
    @log_call
    def post(self, ctx, body):
        try:
            body['id'] = 0  # Set a dummy id to pass the initial validation
            to_create = deserialize_request(body, self.entity_class)
            return serialize_response(self.member_manager.new_member(ctx, to_create)), 201
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def put(self, ctx, member_id, body):
        try:
            body['id'] = member_id  # Set a dummy id to pass the initial validation
            to_update = deserialize_request(body, self.entity_class)
            self.member_manager.update_member(ctx, member_id, to_update, True)
            return NoContent, 201
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def patch(self, ctx, member_id, body):
        try:
            body['id'] = member_id  # Set a dummy id to pass the initial validation
            to_update = deserialize_request(body, self.abstract_entity_class)
            self.member_manager.update_member(ctx, member_id, to_update, False)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def membership_post(self, ctx, member_id: int, body):
        """ Add a membership record in the database """
        LOG.debug("http_member_post_membership_called", extra=log_extra(ctx, member_id=member_id, request=body))

        try:
            if 'uuid' not in body:
                body['uuid'] = "123e4567-e89b-12d3-a456-426614174000"
            print(body)
            to_create: Membership = deserialize_request(body, Membership)

            created_membership = self.member_manager.new_membership(ctx, member_id, to_create)
            return serialize_response(created_membership), 200  # 200 OK
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def password_put(self, ctx, member_id, body):
        """ Set the password of a member. """

        try:
            self.member_manager.change_password(ctx, member_id, body.get('password'), body.get("hashedPassword"))
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def logs_search(self, ctx, member_id, dhcp=False):
        """ Get logs from a member. """
        try:
            return self.member_manager.get_logs(ctx, member_id, dhcp=dhcp), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def statuses_search(self, ctx, member_id):
        try:
            return serialize_response(self.member_manager.get_statuses(ctx, member_id)), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def membership_search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None):
        try:
            filter_ = deserialize_request(filter_, AbstractMembership)
            result, total_count = self.member_manager.membership_search(ctx, limit=limit, offset=offset, terms=terms,
                                                                        filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(serialize_response, result))
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def get_latest_membership(self, ctx, member_id: int) -> Membership:
        try:
            membership: Membership = self.member_manager.get_latest_membership(ctx, member_id)
            LOG.debug("get_latest_membership", extra=log_extra(ctx,membership_uuid=membership.uuid))
            return serialize_response(membership), 200
        except Exception as e:
            LOG.debug("get_latest_membership_error", extra=log_extra(ctx,error=str(e)))
            return handle_error(ctx, e)


    @with_context
    @require_sql
    @log_call
    def membership_get(self, ctx, member_id, uuid):
        pass

    @with_context
    @require_sql
    @log_call
    def membership_patch(self, ctx, member_id, uuid, body):
        try:
            LOG.debug("membership_patch_called", extra=log_extra(ctx, body=body, uuid=uuid, member_id=member_id))
            body['uuid'] = uuid
            to_update: AbstractMembership = deserialize_request(body, AbstractMembership)
            self.member_manager.change_membership(ctx, member_id, uuid, to_update)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def membership_validate(self, ctx, member_id, uuid):
        try:
            self.member_manager.validate_membership(ctx, member_id, uuid)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def charter_get(self, ctx, member_id, charter_id) -> Tuple[str, int]:
        try:
            return self.member_manager.get_charter(ctx, member_id, charter_id), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def charter_put(self, ctx, member_id, charter_id) -> Tuple[Any, int]:
        try:
            self.member_manager.update_charter(ctx, member_id, charter_id)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)
