# coding=utf-8
from adh6.exceptions import AlreadyExistsError, NetworkManagerReadError, ValidationError, UnauthorizedError, NotFoundError
from adh6.misc.context import log_extra
from adh6.misc.log import LOG


def _error(code, message):
    return {
        'code': code,
        'message': message
    }


def handle_error(ctx, e: Exception):
    if isinstance(e, NotFoundError):
        return _error(404, str(e)), 404
    elif isinstance(e, UnauthorizedError):
        return _error(403, str(e)), 403
    elif isinstance(e, ValueError) or isinstance(e, ValidationError) or isinstance(e, NetworkManagerReadError) or isinstance(e, AlreadyExistsError):
        return _error(400, str(e)), 400
    else:
        LOG.error('Fatal exception: ' + str(e), extra=log_extra(ctx))
        return _error(500, "The server encountered an unexpected error"), 500
