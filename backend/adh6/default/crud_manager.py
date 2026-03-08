from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.exceptions import IntMustBePositive

from .crud_repository import CRUDRepository


class CRUDManager:
    def __init__(self, repository: CRUDRepository, not_found_exception):
        self.repository = repository
        self.not_found_exception = not_found_exception

    @log_call
    async def search(
        self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, **kwargs
    ) -> tuple[list, int]:
        if limit < 0:
            raise IntMustBePositive("limit")

        if offset < 0:
            raise IntMustBePositive("offset")

        return await self.repository.search_by(
            limit=limit, offset=offset, terms=terms, **kwargs
        )

    @log_call
    async def get_by_id(self, id: int):
        e = await self.repository.get_by_id(id)
        if not e:
            raise self.not_found_exception(id)
        return e

    @log_call
    async def update_or_create(self, obj, id: int | None = None):
        current_object = None
        if id is not None:
            current_object = await self.repository.get_by_id(id)

        if current_object is None:
            return await self.repository.create(obj), True
        else:
            obj.id = current_object.id
            return await self.repository.update(obj, override=True), False

    @log_call
    async def partially_update(self, obj, id: int, override=False):
        obj.id = id
        return await self.repository.update(obj, override=override), False

    @log_call
    async def delete(self, id: int):
        e = await self.repository.get_by_id(object_id=id)
        if not e:
            raise self.not_found_exception(id)
        return await self.repository.delete(id)
