# coding=utf-8
from adh6.exceptions import AlreadyExistsError, NetworkManagerReadError, ValidationError, UnauthorizedError, NotFoundError
import logging

def handle_error(e: Exception):
    def _error(code, message):
        return {
            'code': code,
            'message': message
        }
    if isinstance(e, NotFoundError):
        return _error(404, str(e)), 404
    elif isinstance(e, UnauthorizedError):
        return _error(403, str(e)), 403
    elif isinstance(e, ValueError) or isinstance(e, ValidationError) or isinstance(e, NetworkManagerReadError) or isinstance(e, AlreadyExistsError):
        return _error(400, str(e)), 400
    else:
        logging.error('Fatal exception: ' + str(e))
        return _error(500, "The server encountered an unexpected error"), 500
