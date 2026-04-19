"""
Log function call decorator.
"""

import asyncio
from functools import wraps

from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def log_call(f):
    """
    Logs the function call with its parameters and context
    """

    if asyncio.iscoroutinefunction(f):

        @wraps(f)
        async def async_wrapper(cls, *args, **kwargs):
            """
            Wrap http_api function.
            """
            import logging

            logging.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)  # noqa: LOG015  # TODO: use local logger
            with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
                return await f(cls, *args, **kwargs)

        return async_wrapper

    @wraps(f)
    def sync_wrapper(cls, *args, **kwargs):
        """
        Wrap http_api function.
        """
        import logging

        logging.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)  # noqa: LOG015  # TODO: use local logger
        with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
            return f(cls, *args, **kwargs)

    return sync_wrapper
