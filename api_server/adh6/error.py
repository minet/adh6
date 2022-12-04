# coding=utf-8
from adh6.exceptions import AlreadyExistsError, NetworkManagerReadError, ValidationError, UnauthorizedError, NotFoundError
import logging

def handle_error(e: Exception):
    def _error(message):
        return {
            'message': message
        }
    if isinstance(e, NotFoundError):
        return _error(str(e)), 404
    elif isinstance(e, UnauthorizedError):
        return _error(str(e)), 403
    elif isinstance(e, ValueError) or isinstance(e, ValidationError) or isinstance(e, NetworkManagerReadError) or isinstance(e, AlreadyExistsError):
        return _error(str(e)), 400
    else:
        logging.error('Fatal exception: ' + str(e))
        print(e)
        return _error("The server encountered an unexpected error"), 500
