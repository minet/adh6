"""
Log function call decorator.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TypeVar, cast

from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., object])


def log_call(f: F) -> F:
    """
    Logs the function call with its parameters and context
    """

    if asyncio.iscoroutinefunction(f):

        @wraps(f)
        async def async_wrapper(cls: object, *args: object, **kwargs: object) -> object:
            """
            Wrap http_api function.
            """
            logger.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)
            with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
                async_function = cast(Callable[..., Awaitable[object]], f)
                return await async_function(cls, *args, **kwargs)

        return cast(F, async_wrapper)

    @wraps(f)
    def sync_wrapper(cls: object, *args: object, **kwargs: object) -> object:
        """
        Wrap http_api function.
        """
        logger.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)
        with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
            return f(cls, *args, **kwargs)

    return cast(F, sync_wrapper)
