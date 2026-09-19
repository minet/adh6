"""
Log function call decorator.
"""

import asyncio
import logging
from functools import wraps

from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


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
            logger.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)
            with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
                return await f(cls, *args, **kwargs)

        return async_wrapper

    @wraps(f)
    def sync_wrapper(cls, *args, **kwargs):
        """
        Wrap http_api function.
        """
        logger.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)
        with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
            return f(cls, *args, **kwargs)

    return sync_wrapper
