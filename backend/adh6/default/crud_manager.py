from collections.abc import Callable
from typing import Any

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.exceptions import IntMustBePositive

from .crud_repository import CRUDRepository


class CRUDManager:
    def __init__(
        self,
        repository: CRUDRepository[Any, Any, Any],
        not_found_exception: Callable[[object], Exception],
    ) -> None:
        self.repository = repository
        self.not_found_exception = not_found_exception

    @log_call
    async def search(
        self,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        terms: str | None = None,
        **kwargs: Any,
    ) -> tuple[list[Any], int]:
        if limit < 0:
            raise IntMustBePositive("limit")

        if offset < 0:
            raise IntMustBePositive("offset")

        return await self.repository.search_by(limit=limit, offset=offset, terms=terms, **kwargs)

    @log_call
    async def get_by_id(self, id: int) -> Any:
        e = await self.repository.get_by_id(id)
        if not e:
            raise self.not_found_exception(id)
        return e

    @log_call
    async def create(self, body: Any) -> Any:
        return await self.repository.create(body)

    @log_call
    async def update(self, id: int, body: Any, override: bool = True) -> Any:
        e = await self.repository.get_by_id(id)
        if not e:
            raise self.not_found_exception(id)
        body.id = id
        return await self.repository.update(body, override=override)

    @log_call
    async def update_or_create(self, obj: Any, id: int | None = None) -> tuple[Any, bool]:
        current_object = None
        if id is not None:
            current_object = await self.repository.get_by_id(id)

        if current_object is None:
            return await self.repository.create(obj), True
        obj.id = current_object.id
        return await self.repository.update(obj, override=True), False

    @log_call
    async def partially_update(self, obj: Any, id: int, override: bool = False) -> tuple[Any, bool]:
        obj.id = id
        return await self.repository.update(obj, override=override), False

    @log_call
    async def delete(self, id: int) -> Any:
        e = await self.repository.get_by_id(object_id=id)
        if not e:
            raise self.not_found_exception(id)
        return await self.repository.delete(id)
