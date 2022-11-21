from typing import Any, Dict, Union

from connexion import NoContent
from adh6.decorator import with_context

from ..api_keys_manager import ApiKeyManager


class ApiKeyHandler:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.api_key_manager = api_key_manager

    @with_context
    def search(self, limit, offset, login: Union[str, None] = None):
        result, count = self.api_key_manager.search(limit=limit, offset=offset, login=login)
        headers = {
            "X-Total-Count": str(count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return [r.to_dict() for r in result], 200, headers

    @with_context
    def post(self, body: Dict[str, Any]):
        return self.api_key_manager.create(login=body.get('login', ''), roles=body.get('roles', [])), 200

    @with_context
    def delete(self, id_: int):
        self.api_key_manager.delete(id=id_)
        return NoContent, 204

