# coding=utf-8
"""
Contain all the http http_api functions.
"""

from connexion import NoContent

from src.entity import AbstractMember, Member
from src.exceptions import MemberNotFoundError, UserInputError
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.default import DefaultHandler
from src.interface_adapter.http_api.util.error import bad_request
from src.interface_adapter.sql.decorator.auth import auth_regular_admin
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
    @auth_regular_admin
    def membership_post(self, ctx, username, body):
        """ Add a membership record in the database """
        LOG.debug("http_member_post_membership_called", extra=log_extra(ctx, username=username, request=body))

        try:
            self.member_manager.new_membership(ctx, username, body.get('duration'), body.get('payment_method'),
                                               start_str=body.get('start'))
            return NoContent, 200  # 200 OK

        except MemberNotFoundError:
            return NoContent, 404  # 404 Not Found

        except UserInputError as e:
            return bad_request(e), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def password_put(self, ctx, username, body):
        """ Set the password of a member. """
        # Careful not to log the body here!
        LOG.debug("http_member_put_password_called", extra=log_extra(ctx, username=username, body=None))

        try:
            self.member_manager.change_password(ctx, username, body.get('password'))
            return NoContent, 204  # 204 No Content

        except MemberNotFoundError:
            return NoContent, 404  # 404 Not Found

        except UserInputError as e:
            return bad_request(e), 400  # 400 Bad Request

    @with_context
    @require_sql
    @auth_regular_admin
    def logs_search(self, ctx, username, dhcp=False):
        """ Get logs from a member. """
        LOG.debug("http_member_get_logs_called", extra=log_extra(ctx, username=username, dhcp=dhcp))
        try:
            return self.member_manager.get_logs(ctx, username, dhcp=dhcp), 200
        except MemberNotFoundError:
            return NoContent, 404
