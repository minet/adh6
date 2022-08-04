# coding=utf-8
"""
With context decator.
"""
import traceback
import uuid
from connexion import NoContent
import connexion
from flask import current_app, request
from functools import wraps

from adh6.exceptions import UnauthenticatedError

from adh6.storage import db
from adh6.misc.context import build_context, log_extra
from adh6.misc.log import LOG


def with_context(f, session_handler = None):
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
        s = session_handler.session() if session_handler else db.session()

        if "token_info" not in connexion.context:
            LOG.warning('could_not_extract_token_info_kwargs')
            raise UnauthenticatedError("Not token informations")

        token_info = connexion.context["token_info"]
        testing = current_app.config["TESTING"]
        ctx = build_context(
            session=s,
            testing=testing,
            request_id=str(uuid.uuid4()),  # Generates an unique ID on this request so we can track it.
            url=request.url,
            admin=token_info.get("uid", ""),
            roles=token_info.get("scope", [])
        )
        kwargs["ctx"] = ctx
        try:
            result = f(*args, **kwargs)

            print(result)

            # It makes things clearer and less error-prone.
            if not isinstance(result, tuple) or len(result) <= 1:
                raise ValueError("Please always pass the result AND the HTTP code.")

            status_code = result[1]
            msg = result[0]
            if result[0] == NoContent:
                msg = None
            if status_code and (200 <= status_code <= 299 or status_code == 302):
                s.commit()
            else:
                LOG.info("rollback_sql_transaction_non_200_http_code",
                         extra=log_extra(ctx, code=status_code, message=msg))
                s.rollback()
            return result

        except Exception as e:
            LOG.error("rollback_sql_transaction_exception_caught",
                      extra=log_extra(ctx, exception=str(e), traceback=traceback.format_exc()))
            s.rollback()
            raise

        finally:
            # When running unit tests, we don't close the session so tests can actually perform some work on that
            # session.
            if not testing:
                s.close()

    return wrapper
