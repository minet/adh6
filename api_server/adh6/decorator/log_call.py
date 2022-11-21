# coding=utf-8
"""
Log function call decorator.
"""
from functools import wraps
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


def log_call(f):
    """
    Logs the function call with its parameters and context
    """
    @wraps(f)
    def wrapper(cls, *args, **kwargs):
        """
        Wrap http_api function.
        """
        import logging
        print(kwargs)
        logging.debug(f"{type(cls).__name__}_{f.__name__}_called | {args} | {kwargs}")
        with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
            return f(cls, *args, **kwargs)
    return wrapper
