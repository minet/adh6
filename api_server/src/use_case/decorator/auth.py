# coding=utf-8
"""
Auth decorators.
"""
import datetime
import sys
from enum import Enum
from functools import wraps

import connexion
from connexion import NoContent
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

from src.constants import CTX_SQL_SESSION
from src.entity.admin import Admin
from src.exceptions import AdminNotFoundError, MemberNotFoundError, UnauthorizedError, UnauthenticatedError
from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Admin as AdminSQL, Adherent
from src.util.context import build_context, log_extra
from src.util.log import LOG


class Roles(Enum):
    ADH6_USER = "adh6_user"
    ADH6_ADMIN = "adh6_admin"


def _find_admin(s, username):
    """
    Get the specified admin, if it does not exist, create it.

    The SQL table 'Utilisateurs' is not the source of truth for all the admins. That means that it is populated just so
    we can use admin_id for the entries. This table is not used for access control at all!

    This means when a new admin connects to ADH, she/he is not in the table yet, and we must create it. Here we also
    assume that the admin is authenticated before this function is called.

    """

    try:
        q = s.query(Adherent)
        q = q.filter(Adherent.login == username)
        adherent = q.one_or_none()

        if adherent is not None:
            roles = [Roles.ADH6_USER.value] if adherent.admin is None else adherent.admin.roles.split(",")
            return _map_member_sql_to_entity(adherent), roles
        else:
            raise AdminNotFoundError(username)

    except AdminNotFoundError:
        if current_app.config['TESTING']:
            new_admin = AdminSQL(
                roles="adh6_user,adh6_admin"
            )
            new_adherent = Adherent(
                login=TESTING_CLIENT,
                mail="test@example.com",
                nom="Test",
                prenom="test",
                password="",
                admin=new_admin
            )
            s.add(new_admin)
            s.add(new_adherent)

            return _find_admin(s, username)
        raise MemberNotFoundError()


def auth_required(roles=None, access_control_function=lambda cls, ctx, f, a, kw: (a, kw, True)):
    """
    Authenticate a user checking their roles.
    """

    if roles is None:
        roles = []

    def decorator(f):

        @wraps(f)
        def auth_wrapper(cls, ctx, *args, **kwargs):
            if hasattr(sys, "_called_from_unit_test"):
                return f(cls, ctx, *args, **kwargs)

            user = connexion.context["user"] or None
            token_info = connexion.context["token_info"] or None
            LOG.warning('auth_required_called', extra=log_extra(ctx, token_info=token_info))

            if not current_app.config["TESTING"] and (user is None or token_info is None):
                LOG.warning('could_not_extract_user_and_token_info_kwargs', extra=log_extra(ctx))
                raise UnauthenticatedError("You are not authenticated correctly")

            assert ctx.get(CTX_SQL_SESSION) is not None, 'You need SQL for authentication.'
            adherent, admin_roles = _find_admin(ctx.get(CTX_SQL_SESSION), user)
            LOG.warning('found_roles', extra=log_extra(ctx, roles=admin_roles))

            roles_check = all(role.value in admin_roles for role in roles)
            if not current_app.config["TESTING"] and not roles_check:
                # User is not in the right group(s) and we are not testing, do not allow.
                raise UnauthorizedError("You do not have enough permissions to access this")

            ctx = build_context(ctx=ctx, admin=adherent)

            new_args, new_kwargs, status = access_control_function(cls, ctx, f, args, kwargs)

            status = status or Roles.ADH6_ADMIN.value in admin_roles or current_app.config["TESTING"]
            if not status:
                raise UnauthorizedError("You do not have enough permissions for this specific request")

            return f(cls, ctx, *new_args, **new_kwargs)  # Discard the user and token_info.

        return auth_wrapper

    return decorator
