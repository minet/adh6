from typing import Any

from pydantic import BaseModel

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call, with_context
from adh6.default.crud_manager import CRUDManager


class DefaultHandler:
    def __init__(
        self, entity_class: type[BaseModel], abstract_entity_class: type[BaseModel], main_manager: CRUDManager
    ):
        self.entity_class = entity_class
        self.abstract_entity_class = abstract_entity_class
        self.main_manager = main_manager

    @with_context
    @log_call
    async def search(
        self,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET,
        terms=None,
        filter_: Any | None = None,
        only: list[str] | None = None,
    ):
        def remove(entity: Any) -> Any:
            if isinstance(entity, dict) and only is not None:
                entity_cp = entity.copy()
                for k in entity_cp:
                    if k not in [*only, "id"]:
                        del entity[k]
            return entity

        filter_ = self.abstract_entity_class.from_dict(filter_) if filter_ else None  # type: ignore[attr-defined]
        result, total_count = await self.main_manager.search(limit=limit, offset=offset, terms=terms, filter_=filter_)
        headers = {"X-Total-Count": str(total_count), "access-control-expose-headers": "X-Total-Count"}
        return list(map(remove, (x.to_dict() for x in result))), 200, headers  # type: ignore[attr-defined]

    @with_context
    @log_call
    async def get(self, id_: int, only: list[str] | None = None):
        def remove(entity: Any) -> Any:
            if isinstance(entity, dict) and only is not None:
                entity_cp = entity.copy()
                for k in entity_cp:
                    if k not in [*only, "id"]:
                        del entity[k]
            return entity

        obj = await self.main_manager.get_by_id(id=id_)
        return remove(obj.to_dict()), 200  # type: ignore[attr-defined]

    @with_context
    @log_call
    async def post(self, body):
        return await self._update(function=self.main_manager.update_or_create, klass=self.entity_class, body=body)

    @with_context
    @log_call
    async def put(self, body, id_: int):
        return await self._update(
            function=self.main_manager.update_or_create, klass=self.entity_class, body=body, id=id_
        )

    @with_context
    async def patch(self, body, id_: int):
        return await self._update(
            function=self.main_manager.partially_update, klass=self.abstract_entity_class, body=body, id=id_
        )

    @with_context
    @log_call
    async def delete(self, id_: int):
        await self.main_manager.delete(id=id_)
        return None, 204  # 204 No Content

    async def _update(self, function, klass: type[BaseModel], body, id: int | None = None):
        body["id"] = 0  # Set a dummy id to pass the initial validation
        to_update = klass.from_dict(body)  # type: ignore[attr-defined]
        the_object, created = await function(to_update, id=id)
        return the_object.to_dict(), 201 if created else 204  # type: ignore[attr-defined]
