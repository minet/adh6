# coding=utf-8
"""
Log function call decorator.
"""
import re
from functools import wraps

import src.entity
from src.interface_adapter.http_api.util.serializer import serialize_response
from src.util.context import log_extra
from src.util.log import LOG


def log_call(f):
    """
    Logs the function call with its parameters and context
    """

    @wraps(f)
    def wrapper(cls, ctx, *args, **kwargs):
        """
        Wrap http_api function.
        """
        class_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', type(cls).__name__)
        class_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()

        log_kwargs = {}
        for key, value in kwargs.items():
            if hasattr(src.entity, type(value).__name__):
                log_kwargs[key] = serialize_response(value)
            else:
                log_kwargs[key] = value

        LOG.debug("http_" + class_name + "_" + f.__name__ + "_called",
                  extra=log_extra(ctx, **log_kwargs))
        return f(cls, ctx, *args, **kwargs)

    return wrapper
