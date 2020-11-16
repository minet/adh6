# coding=utf-8
"""
Contain all the http http_api functions.
"""

from connexion import NoContent

from src.entity import AbstractMember, Member
from src.exceptions import MemberNotFoundError, UserInputError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler, _error
from src.interface_adapter.http_api.util.error import bad_request, handle_error
from src.interface_adapter.http_api.util.serializer import serialize_response
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
    def membership_post(self, ctx, username, body):
        """ Add a membership record in the database """
        LOG.debug("http_member_post_membership_called", extra=log_extra(ctx, username=username, request=body))

        try:
            self.member_manager.new_membership(ctx, username, body.get('duration'), body.get('payment_method'),
                                               start_str=body.get('start'))
            return NoContent, 200  # 200 OK
        except Exception as e:
            return handle_error(e)

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

    def membership_get(self, ctx, member_id, uuid):
        pass

    def membership_patch(self, ctx, member_id, uuid):
        pass
