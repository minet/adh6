# coding=utf-8
from types import MappingProxyType
from typing import Optional

from adh6.constants import CTX_SQL_SESSION, CTX_ADMIN, CTX_TESTING, CTX_REQUEST_ID, CTX_REQUEST_URL, CTX_ROLES

def build_context(ctx: Optional[MappingProxyType]=None, session=None, admin=None, testing=None, request_id=None, url=None, roles=None):
    """
    :rtype:
    """
    new_fields = {
        CTX_SQL_SESSION: session,
        CTX_ADMIN: admin,
        CTX_ROLES: roles,
        CTX_TESTING: testing,
        CTX_REQUEST_ID: request_id,
        CTX_REQUEST_URL: url
    }
    if ctx is None:
        return MappingProxyType(new_fields)

    old_fields = {k: v for k, v in ctx.items() if v is not None}  # Remove None fields.

    merged = {**new_fields, **old_fields}  # Merge old and new context, with priority for the new one.

    return MappingProxyType(merged)


def log_extra(context: MappingProxyType, **extra_fields):
    user_login = None
    if (user := context.get(CTX_ADMIN)):
        user_login = user.login

    infos = {
        'request_uuid': context.get(CTX_REQUEST_ID),
        'user': user_login,
        'testing': str(context.get(CTX_TESTING) or False),
        'url': context.get(CTX_REQUEST_URL),
        'roles': context.get(CTX_ROLES),
    }
    return {
        'extra': {**infos, **extra_fields},
    }
