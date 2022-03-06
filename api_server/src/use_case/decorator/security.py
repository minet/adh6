import os
from functools import wraps

import connexion

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION
from src.entity import Admin
from src.entity.roles import Roles
from src.exceptions import UnauthenticatedError, MemberNotFoundError, UnauthorizedError
from src.interface_adapter.sql.member_repository import _map_member_sql_to_entity
from src.interface_adapter.sql.model.models import Adherent
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

    query = session.query(Adherent)
    query = query.filter((Adherent.login == username) | (Adherent.ldap_login == username))
    adherent = query.one_or_none()

    if adherent is not None:
        roles = connexion.context["token_info"]["groups"]
        if adherent.is_naina and "adh6_admin" not in roles:
            roles += ["adh6_admin"]
        if Roles.USER.value not in roles:
            roles.append(Roles.USER.value)
        return _map_member_sql_to_entity(adherent), roles
    else:
        raise MemberNotFoundError(username)


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
            if os.getenv("UNIT_TESTING"):
                return f(cls, ctx, *args, **kwargs)
            user = connexion.context["user"] if "user" in connexion.context else None
            token_info = connexion.context["token_info"] if "token_info" in connexion.context else None

            if token_info is None:
                raise UnauthenticatedError("Not token informations")
            LOG.warning('auth_required_called', extra=log_extra(ctx, token_info=token_info))

            arguments = {}
            authorized = False
            if (token_info is None or (user is None or ("user" in token_info and token_info["user"] is None))):
                LOG.warning('could_not_extract_user_and_token_info_kwargs', extra=log_extra(ctx))
                raise UnauthenticatedError("You are not authenticated correctly")

            assert ctx.get(CTX_SQL_SESSION) is not None, 'You need SQL for authentication.'
            admin, admin_roles = _find_admin(ctx.get(CTX_SQL_SESSION), user)
            LOG.warning('found_roles', extra=log_extra(ctx, roles=admin_roles))

            obj = kwargs["filter_"] if "filter_" in kwargs else None
            arguments = merge_obj_to_dict(arguments, obj)
            arguments = merge_obj_to_dict(arguments, Admin(login=user, member=admin.id, roles=admin_roles))
            arguments['Roles'] = admin_roles

            if not hasattr(cls, '_security_definition'):
                raise UnauthorizedError("You do not have enough permissions to access this")
            security_definition = getattr(cls, '_security_definition')

            if action not in security_definition.collection and action not in security_definition.item:
                raise UnauthorizedError("The authentication has not been authorize on the server, please contact the administrator") 

            if is_collection:
                authorized = action in security_definition.collection and security_definition.collection[action](arguments)
            else:
                authorized = action in security_definition.item and security_definition.item[action](arguments)

            if not authorized:
                raise UnauthorizedError("You do not have enough permissions to access this")

            ctx = build_context(ctx=ctx, admin=admin, roles=admin_roles)
            return f(cls, ctx, *args, **kwargs)

        return wrapper

    return decorator
