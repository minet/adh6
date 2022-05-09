from enum import Enum
import operator
import os
from functools import wraps
from typing import List, Optional

import connexion

from sqlalchemy.orm.session import Session

from src.constants import CTX_SQL_SESSION
from src.entity.util.logic import BinaryExpression, Expression, FalseExpression, TrueExpression
from src.exceptions import UnauthenticatedError, MemberNotFoundError, UnauthorizedError
from src.interface_adapter.sql.model.models import Adherent, ApiKey
from src.util.context import log_extra, build_context
from src.util.log import LOG

class User(object):
    def __init__(self, id: Optional[int] = None, login: Optional[str] = None, roles: List[str] = []) -> None:
        self._id = id
        self._login = login
        self._roles = roles

    """
    The id is None when connection throught an api key
    or is equal to the one of the user on the plateform
    """
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        self._id = id
   
    """
    Login of the user either connecting with an api key nor with a normal connexion
    """
    @property
    def login(self):
        return self._login
    @login.setter
    def login(self, login):
        self._login = login
    
    """
    Roles of the user in the plateform
    """
    @property
    def roles(self):
        return self._roles
    @roles.setter
    def roles(self, roles):
        self._roles = roles

class Roles(Enum):
    USER = "adh6_user"
    NETWORK = "network"
    ADMIN = "adh6_admin"
    SUPERADMIN = "adh6_superadmin"
    TRESO = "adh6_treso"
    VLAN_PROD = "cluster-prod"
    VLAN_DEV = "cluster-dev"
    VLAN_HOSTING = "cluster-hosting" 


def _find_user(session: Session, username) -> User:
    """
    If a user is found in the ApiKey or the Members return it. This function only 
    fuse all the informations regarding the user that do the request, it does not
    handle the authentication directly
    """

    adherent: Optional[Adherent] = session.query(Adherent).filter((Adherent.login == username) | (Adherent.ldap_login == username)).one_or_none()
    api_user: Optional[ApiKey] = session.query(ApiKey).filter(ApiKey.name == username).one_or_none()

    exists = adherent is not None or api_user is not None

    if not exists:
        raise MemberNotFoundError(username)

    user = User(login=username, roles=connexion.context["token_info"]["groups"])
    if adherent is not None:
        user.id = adherent.id
        if adherent.is_naina and "adh6_admin" not in user.roles:
            user.roles.append("adh6_admin")
    
    if Roles.USER.value not in user.roles:
        user.roles.append(Roles.USER.value)
    return user 


class SecurityDefinition(dict):
    def __init__(self, item={}, collection={}):
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
            token_info = connexion.context["token_info"] if "token_info" in connexion.context else None
            username = connexion.context["user"] if "user" in connexion.context else None
            if token_info is None:
                LOG.warning('could_not_extract_token_info_kwargs', extra=log_extra(ctx))
                raise UnauthenticatedError("Not token informations")
            if username is None:
                LOG.warning('could_not_extract_user_info_kwargs', extra=log_extra(ctx))
                raise UnauthenticatedError("You are not authenticated correctly")
            
            LOG.warning('auth_required_called', extra=log_extra(ctx, token_info=token_info))
            
            arguments = {}
            authorized = False
            assert ctx.get(CTX_SQL_SESSION) is not None, 'You need SQL for authentication.'
            logged_user = _find_user(ctx.get(CTX_SQL_SESSION), username)
            obj = kwargs["filter_"] if "filter_" in kwargs else None
            arguments = merge_obj_to_dict(arguments, obj)
            arguments["user"] = logged_user
            if not hasattr(cls, '_security_definition'):
                raise UnauthorizedError("You do not have enough permissions to access this")
            security_definition: SecurityDefinition = getattr(cls, '_security_definition')
            if action not in security_definition.collection and action not in security_definition.item:
                raise UnauthorizedError("The authentication has not been authorize on the server, please contact the administrator")
            if is_collection:
                authorized = action in security_definition.collection and security_definition.collection[action](arguments)
            else:
                authorized = action in security_definition.item and security_definition.item[action](arguments)
            if logged_user.roles is not None and Roles.SUPERADMIN.value in logged_user.roles:
                authorized = True

            if not authorized:
                raise UnauthorizedError("You do not have enough permissions to access this")

            ctx = build_context(ctx=ctx, admin=logged_user, roles=logged_user.roles)
            return f(cls, ctx, *args, **kwargs)

        return wrapper

    return decorator

class OwnsExpression(Expression):
    def __init__(self):
        super().__init__()

    def __call__(self, arguments):
        user: User = arguments['user']
        return user.id

def owns(*props: List[property]) -> Expression:
    expression = TrueExpression()
    for prop in props:
        expression &= BinaryExpression(prop, OwnsExpression(), operator=operator.eq)
    return expression

class HasRoleExpression(Expression):
    def __init__(self, enum_element: Roles):
        super().__init__()
        self.enum_element: Roles = enum_element

    def __call__(self, arguments):
        roles: List[str] = arguments['user'].roles
        return self.enum_element.value in roles

def has_any_role(roles: List[Roles]) -> Expression:
    expression = FalseExpression()
    for role in roles:
        expression |= HasRoleExpression(role)
    return expression

def is_admin() -> Expression:
    return HasRoleExpression(Roles.ADMIN)
