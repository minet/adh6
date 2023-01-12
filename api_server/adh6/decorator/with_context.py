# coding=utf-8
"""
With context decator.
"""
from functools import wraps

from adh6.error import handle_error


def with_context(f):
    """
    Add context variable to the first argument of the http_api function.
    The wrapper will also take care of the lifecycle of the session choosen for the backend storage for instance the
    SQL session for SQLAlchemy.
    If the function wrapped return something that is not a 2XX error code, the session will be automatically rollbacked.
    Otherwise it will commit.
    The session object needs to implement at least 2 functions commit and rollback and the session_handler needs to
    implement session function which create the session object
    """

    @wraps(f)
    def wrapper(*args,**kwargs):
        """
        Wrap http_api function.
        """
        from adh6.storage import session
        try:
            result = f(*args, **kwargs)
            # It makes things clearer and less error-prone.
            if not isinstance(result, tuple) or len(result) <= 1:
                raise ValueError("Please always pass the result AND the HTTP code.")

            status_code = result[1]
            if status_code and (200 <= status_code <= 299 or status_code == 302):
                session.commit()
            else:
                raise Exception()
        except Exception as e:
            session.rollback()
            import traceback
            traceback.print_exc()
            return handle_error(e)
        return result

    return wrapper
