# coding=utf-8
"""
Auth decorators.
"""
import datetime
from functools import wraps

from connexion import NoContent
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

from src.constants import CTX_SQL_SESSION
from src.entity.admin import Admin
from src.exceptions import AdminNotFoundError
from src.interface_adapter.http_api.auth import TESTING_CLIENT, ADH6_USER
from src.interface_adapter.sql.model.models import Admin as AdminSQL, Adherent
from src.util.context import build_context, log_extra
from src.util.log import LOG


def _find_admin(s, username):
    """
    Get the specified admin, if it does not exist, create it.

    The SQL table 'Utilisateur' is not the source of truth for all the admins. That means that it is populated just so
    we can use admin_id for the entries. This table is not used for access control at all!

    This means when a new admin connects to ADH, she/he is not in the table yet, and we must create it. Here we also
    assume that the admin is authenticated before this function is called.

    """
    try:
        q = s.query(Adherent)
        q = q.join(AdminSQL)
        q = q.filter(Adherent.login == username)
        q = q.filter(Adherent.admin is not None)
        return q.one()

    except NoResultFound:
        if current_app.config['TESTING']:
            new_admin = AdminSQL(
                roles=""
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
        raise AdminNotFoundError()


def auth_regular_admin(f):
    """
    Authenticate a regular admin.
    """

    # @wraps(f) # Cannot wrap this function, because connexion needs to know we have the user and token_info...
    def wrapper(cls, ctx, *args, user, token_info, **kwargs):
        """
        Wrap http_api function.
        """
        LOG.warning('auth_regular_admin_called', extra=log_extra(ctx, token_info=token_info))
        if not current_app.config["TESTING"] and (user is None or token_info is None):
            LOG.warning('could_not_extract_user_and_token_info_kwargs', extra=log_extra(ctx))
            return NoContent, 401

        assert ctx.get(CTX_SQL_SESSION) is not None, 'You need SQL for authentication.'
        admin = _find_admin(ctx.get(CTX_SQL_SESSION), user)
        roles = admin.admin.roles
        if not current_app.config["TESTING"] and ADH6_USER not in roles:
            # User is not in the right group and we are not testing, do not allow.
            return NoContent, 401

        ctx = build_context(ctx=ctx, admin=Admin(login=admin.login))
        return f(cls, ctx, *args, **kwargs)  # Discard the user and token_info.

    return wrapper


def auth_super_admin(f):
    """
    Authenticate a super admin.
    """

    @wraps(f)
    def wrapper(cls, ctx, *args, **kwargs):
        admin = _find_admin(ctx.get(CTX_SQL_SESSION), TESTING_CLIENT)
        ctx = build_context(ctx=ctx, admin=Admin(login=admin.login))
        return f(cls, ctx, *args, **kwargs)

    # def wrapper(cls, ctx, *args, user, token_info, **kwargs):
    #     """
    #     Wrap http_api function.
    #     """
    #     if not ctx.get(CTX_TESTING) and ADH6_ADMIN not in token_info["groups"]:
    #         # User is not in the right group and we are not testing, do not allow.
    #         return NoContent, 401

    #     admin = _find_admin(ctx.get(CTX_SQL_SESSION), user)
    #     ctx = build_context(ctx=ctx, admin=Admin(login=admin.login))
    #     return f(cls, ctx, *args, **kwargs)  # Discard the user and token_info.

    return wrapper
