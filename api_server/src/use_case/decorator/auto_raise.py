from functools import wraps


def auto_raise(f):
    @wraps(f)
    def wrapper(cls, ctx, *args, **kwargs):
        try:
            return f(cls, ctx, *args, **kwargs)
        except:
            raise
    return wrapper