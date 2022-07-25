import functools
import typing as t

from adh6.authentication import Roles, Method

from adh6.constants import CTX_ADMIN, CTX_ROLES
from adh6.default.util.error import handle_error
from adh6.exceptions import UnauthorizedError


def _default_security_function(ctx: t.Dict[str, t.Any], x: t.Dict[str, t.Any], arg_name: str, method: Method) -> bool:
    return (method == Method.READ and Roles.ADMIN_READ.value in ctx.get(CTX_ROLES, [])) \
        or (method == Method.WRITE and Roles.ADMIN_WRITE.value in ctx.get(CTX_ROLES, [])) \
        or (x.get(arg_name, {}).get("member", -1) == ctx.get(CTX_ADMIN)) \
        or (x.get("id_", -1) == ctx.get(CTX_ADMIN))

def with_security(method: Method = Method.WRITE, arg_name: str = "body", func: t.Callable[[t.Dict[str, t.Any], t.Dict[str, t.Any], str, Method], bool] = _default_security_function):
    def inner(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                if "ctx" not in kwargs:
                    raise UnauthorizedError("cannot check the user")

                if not func(kwargs.get("ctx", {}), kwargs, arg_name, method):
                    raise UnauthorizedError("cannot access this resource") 
            except Exception as e:
                return handle_error(kwargs.get("ctx"), e)
            return f(*args, **kwargs)
        return wrapper
    return inner

