# coding=utf-8
from types import MappingProxyType

from adh6.constants import CTX_SQL_SESSION, CTX_ADMIN, CTX_TESTING, CTX_REQUEST_ID, CTX_REQUEST_URL, CTX_ROLES

def build_context(session=None, admin=None, testing=None, request_id=None, url=None, roles=None) -> MappingProxyType:
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
    return MappingProxyType(new_fields)


def log_extra(context: MappingProxyType, **extra_fields):
    infos = {
        'request_uuid': context.get(CTX_REQUEST_ID),
        'user': context.get(CTX_ADMIN),
        'testing': str(context.get(CTX_TESTING) or False),
        'url': context.get(CTX_REQUEST_URL),
        'roles': context.get(CTX_ROLES),
    }
    return {
        'extra': {**infos, **extra_fields},
    }
