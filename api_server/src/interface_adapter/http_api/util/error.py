# coding=utf-8
from src.exceptions import NetworkManagerReadError, ValidationError, UnauthorizedError, UnauthenticatedError, NotFoundError
from src.util.context import log_extra
from src.util.log import LOG


def bad_request(err: ValueError):
    return f'Bad request: {repr(err)}.'


def _error(code, message):
    return {
        'code': code,
        'message': message
    }


def handle_error(ctx, e: Exception):
    if isinstance(e, ValidationError) or isinstance(e, NetworkManagerReadError):
        return _error(400, str(e)), 400
    elif isinstance(e, NotFoundError):
        return _error(404, str(e)), 404
    elif isinstance(e, UnauthenticatedError):
        return _error(401, str(e)), 401
    elif isinstance(e, UnauthorizedError):
        return _error(403, str(e)), 403
    else:
        LOG.error('Fatal exception: ' + str(e), extra=log_extra(ctx))
        return _error(500, "The server encountered an unexpected error"), 500
