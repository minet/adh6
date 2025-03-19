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

        # print(kwargs)
        logging.debug("%s_%s_called | %s | %s", type(cls).__name__, f.__name__, args, kwargs)  # noqa: LOG015  # TODO: use local logger
        with tracer.start_as_current_span(f"{type(cls).__name__}.{f.__name__}"):
            return f(cls, *args, **kwargs)

    return wrapper
