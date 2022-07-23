from typing import Any, Dict, Union

from connexion import NoContent
from adh6.authentication.api_keys_manager import ApiKeyManager
from adh6.default.util.error import handle_error
from adh6.default.decorator.with_context import with_context
from adh6.default.util.serializer import serialize_response


class ApiKeyHandler:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.api_key_manager = api_key_manager

    @with_context
    def search(self, ctx, limit, offset, login: Union[str, None] = None):
        try:
            result, count = self.api_key_manager.search(ctx=ctx, limit=limit, offset=offset, login=login)
            headers = {
                "X-Total-Count": str(count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            return serialize_response(result), 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    def post(self, ctx, body: Dict[str, Any]):
        try:
            return self.api_key_manager.create(ctx=ctx, login=body.get('login', ''), roles=body.get('roles', [])), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    def delete(self, ctx, id_: int):
        try:
            self.api_key_manager.delete(ctx=ctx, id=id_)
            return NoContent, 204
        except Exception as e:
            return handle_error(ctx, e)

