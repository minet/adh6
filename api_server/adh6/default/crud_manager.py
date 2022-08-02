from typing import Optional, Tuple
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.exceptions import IntMustBePositive
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.auto_raise import auto_raise
from adh6.default.crud_repository import CRUDRepository


class CRUDManager:

    def __init__(self, repository: CRUDRepository, abstract_entity, not_found_exception):
        self.repository = repository
        self.abstract_entity = abstract_entity
        self.not_found_exception = not_found_exception

    @log_call
    @auto_raise
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, **kwargs) -> Tuple[list, int]:
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        return self.repository.search_by(
            ctx, 
            limit=limit,
            offset=offset,
            terms=terms,
            **kwargs
        )

    @log_call
    @auto_raise
    def get_by_id(self, ctx, id: int):
        return self.repository.get_by_id(ctx, id)

    @log_call
    @auto_raise
    def update_or_create(self, ctx, obj, id: Optional[int] = None):
        current_object = None
        if id is not None:
            current_object = self.repository.get_by_id(ctx, id)

        if current_object is None:
            return self.repository.create(ctx, obj), True
        else:
            obj.id = current_object.id
            return self.repository.update(ctx, obj, override=True), False

    @log_call
    @auto_raise
    def partially_update(self, ctx, obj, id: int, override=False):
        obj.id = id
        return self.repository.update(ctx, obj, override=override), False

    @log_call
    @auto_raise
    def delete(self, ctx, id: int):
        e = self.repository.get_by_id(ctx=ctx, object_id=id)
        if not e:
            raise self.not_found_exception(id)
        return self.repository.delete(ctx, id)
