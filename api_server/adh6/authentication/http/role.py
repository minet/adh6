from typing import Any, Dict, Union

from connexion import NoContent
from adh6.authentication.role_manager import RoleManager
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error


class RoleHandler:
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager

    @with_context
    def search(self, ctx, auth: str, id_: Union[str, None]=None):
        try:
            result, count = self.role_manager.search(ctx=ctx, auth=auth, identifier=id_)
            headers = {
                "X-Total-Count": str(count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            return list(map(lambda x: x.to_dict(), result)), 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def post(self, ctx, body: Dict[str, Any]):
        try:
            self.role_manager.create(ctx=ctx, auth=body["auth"], identifier=body["identifier"], roles=body["roles"])
            return NoContent, 201
        except Exception as e:
            print(e)
            return handle_error(ctx, e)

    @with_context
    @log_call
    def delete(self, ctx, id_: int):
        try:
            self.role_manager.delete(ctx=ctx, id=id_)
            return NoContent, 204
        except Exception as e:
            print(e)
            return handle_error(ctx, e)
