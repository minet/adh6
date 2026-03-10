from typing import Any

from adh6.decorator import log_call, with_context

from ..role_manager import RoleManager


class RoleHandler:
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager

    @with_context
    async def search(self, auth: str, id_: str | None = None):
        result, count = await self.role_manager.search(auth=auth, identifier=id_)
        headers = {"X-Total-Count": str(count), "access-control-expose-headers": "X-Total-Count"}
        return [x.to_dict() for x in result], 200, headers

    @with_context
    @log_call
    async def post(self, body: dict[str, Any]):
        await self.role_manager.create(auth=body["auth"], identifier=body["identifier"], roles=body["roles"])
        return None, 201

    @with_context
    @log_call
    async def delete(self, id_: int):
        await self.role_manager.delete(id=id_)
        return None, 204
