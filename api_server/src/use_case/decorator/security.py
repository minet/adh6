import sys
from functools import wraps

import connexion
from flask import current_app

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION
from src.entity import Admin
from src.entity.roles import Roles
from src.exceptions import UnauthenticatedError, MemberNotFoundError, AdminNotFoundError, UnauthorizedError
from src.interface_adapter.http_api.auth import TESTING_CLIENT
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Admin as AdminSQL, Adherent
from src.util.context import log_extra, build_context
from src.util.log import LOG


def _find_admin(session: Session, username):
    """
    Get the specified admin, if it does not exist, create it.

    The SQL table 'Utilisateurs' is not the source of truth for all the admins. That means that it is populated just so
    we can use admin_id for the entries. This table is not used for access control at all!

    This means when a new admin connects to ADH, she/he is not in the table yet, and we must create it. Here we also
    assume that the admin is authenticated before this function is called.

    """

    try:
        query = session.query(Adherent)
        query = query.filter((Adherent.login == username) | (Adherent.ldap_login == username))
        adherent = query.one_or_none()

        if adherent is not None:
            #roles = [Roles.USER.value] if adherent.admin is None else adherent.admin.roles.split(",")
            roles = connexion.context["token_info"]["groups"]
            if adherent.is_naina and "adh6_admin" not in roles:
                roles += ["adh6_admin"]
            if Roles.USER.value not in roles:
                roles.append(Roles.USER.value)
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
            session.add(new_admin)
            session.add(new_adherent)

            return _find_admin(session, username)
        raise MemberNotFoundError()


class SecurityDefinition(dict):
    def __init__(self, item=None, collection=None):
        dict.__init__(self, item=item, collection=collection)
        self.item = item
        self.collection = collection


def defines_security(security_definition):
    def decorator(Cls):
        setattr(Cls, "_" + "security_definition", security_definition)
        return Cls
    return decorator


def merge_obj_to_dict(d, obj):
    for attr_name in dir(obj):
        attr = obj.__getattribute__(attr_name)
        if not hasattr(attr, "__self__") and attr is not None and not hasattr(object, attr_name):
            d[obj.__class__.__name__ + "." + attr_name] = obj.__getattribute__(attr_name)
    return d


def uses_security(action, is_collection=False):
    def decorator(f):
        @wraps(f)
        def wrapper(cls, ctx, *args, **kwargs):
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

            if not hasattr(cls, '_security_definition') and not current_app.config["TESTING"]:
                raise UnauthorizedError("You do not have enough permissions to access this")
            elif not current_app.config["TESTING"]:
                security_definition = getattr(cls, '_security_definition')

                obj = kwargs["filter_"] if "filter_" in kwargs else None
                arguments = {}
                arguments = merge_obj_to_dict(arguments, obj)
                arguments = merge_obj_to_dict(arguments, Admin(login=user, member=adherent.id, roles=admin_roles))
                arguments['Roles'] = admin_roles

                authorized = False

                if is_collection:
                    authorized = security_definition.collection[action](arguments)
                else:
                    authorized = security_definition.item[action](arguments)

                if not authorized:
                    raise UnauthorizedError("You do not have enough permissions to access this")

            ctx = build_context(ctx=ctx, admin=adherent, roles=admin_roles)
            return f(cls, ctx, *args, **kwargs)

        return wrapper

    return decorator
