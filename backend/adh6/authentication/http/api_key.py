from typing import Any

from adh6.decorator import with_context

from ..api_keys_manager import ApiKeyManager


class ApiKeyHandler:
    def __init__(self, api_key_manager: ApiKeyManager):
        self.api_key_manager = api_key_manager

    @with_context
    async def search(self, limit, offset, login: str | None = None):
        result, count = await self.api_key_manager.search(limit=limit, offset=offset, login=login)
        headers = {"X-Total-Count": str(count), "access-control-expose-headers": "X-Total-Count"}
        return [r.to_dict() for r in result], 200, headers

    @with_context
    async def post(self, body: dict[str, Any]):
        return await self.api_key_manager.create(login=body.get("login", ""), roles=body.get("roles", [])), 200

    @with_context
    async def delete(self, id_: int):
        await self.api_key_manager.delete(id=id_)
        return None, 204
