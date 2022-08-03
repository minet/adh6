# coding=utf-8
"""
Log function call decorator.
"""
import re
from functools import wraps

import adh6.entity
from adh6.util.context import log_extra
from adh6.util.log import LOG


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
        log_args = []
        for key, value in kwargs.items():
            if hasattr(adh6.entity, type(value).__name__):
                log_kwargs[key] = value.to_dict()
            else:
                log_kwargs[key] = value

        for arg in args:
            if hasattr(adh6.entity, type(arg).__name__):
                log_args.append(arg.to_dict())
            else:
                log_args.append(arg)

        log_kwargs["__args"] = log_args
        LOG.info(class_name + "_" + f.__name__ + "_called",
                    extra=log_extra(ctx, **log_kwargs))
        return f(cls, ctx, *args, **kwargs)

    return wrapper
