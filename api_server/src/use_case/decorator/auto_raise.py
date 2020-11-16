import traceback
from functools import wraps


def auto_raise(f):
    @wraps(f)
    def wrapper(cls, ctx, *args, **kwargs):
        try:
            return f(cls, ctx, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            raise
    return wrapper