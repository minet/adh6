from typing import Any, Dict, Union

from connexion import NoContent
from adh6.decorator import log_call, with_context

from ..role_manager import RoleManager


class RoleHandler:
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager

    @with_context
    def search(self, auth: str, id_: Union[str, None]=None):
        result, count = self.role_manager.search(auth=auth, identifier=id_)
        headers = {
            "X-Total-Count": str(count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return list(map(lambda x: x.to_dict(), result)), 200, headers

    @with_context
    @log_call
    def post(self, body: Dict[str, Any]):
        self.role_manager.create(auth=body["auth"], identifier=body["identifier"], roles=body["roles"])
        return NoContent, 201

    @with_context
    @log_call
    def delete(self, id_: int):
        self.role_manager.delete(id=id_)
        return NoContent, 204
