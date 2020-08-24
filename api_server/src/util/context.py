# coding=utf-8
from types import MappingProxyType

from src.constants import CTX_SQL_SESSION, CTX_ADMIN, CTX_TESTING, CTX_REQUEST_ID, CTX_REQUEST_URL


def build_context(ctx: MappingProxyType = None, session=None, admin=None, testing=None, request_id=None, url=None):
    """

    :rtype:
    """
    new_fields = {
        CTX_SQL_SESSION: session,
        CTX_ADMIN: admin,
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
    admin_login = None
    if context.get(CTX_ADMIN):
        admin_login = context.get(CTX_ADMIN).username

    infos = {
        'request_uuid': context.get(CTX_REQUEST_ID),
        'user': admin_login,
        'testing': str(context.get(CTX_TESTING) or False),
        'url': context.get(CTX_REQUEST_URL)
    }
    return {
        'extra': {**infos, **extra_fields},
    }
