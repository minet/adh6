import typing as t

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity.base_model_ import Model
from adh6.exceptions import IntMustBePositive
from adh6.decorator import log_call
from .crud_repository import CRUDRepository


class CRUDManager:
    def __init__(self, repository: CRUDRepository, not_found_exception):
        self.repository = repository
        self.not_found_exception = not_found_exception

    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, **kwargs) -> t.Tuple[list, int]:
        if limit < 0:
            raise IntMustBePositive('limit')

        if offset < 0:
            raise IntMustBePositive('offset')

        return self.repository.search_by(
            limit=limit,
            offset=offset,
            terms=terms,
            **kwargs
        )

    @log_call
    def get_by_id(self, id: int) -> Model:
        e = self.repository.get_by_id(id)
        if not e:
            raise self.not_found_exception(id)
        return e

    @log_call
    def update_or_create(self, obj, id: t.Optional[int] = None):
        current_object = None
        if id is not None:
            current_object = self.get_by_id(id)

        if current_object is None:
            return self.repository.create(obj), True
        else:
            obj.id = current_object.id
            return self.repository.update(obj, override=True), False

    @log_call
    def partially_update(self, obj, id: int, override=False):
        obj.id = id
        return self.repository.update(obj, override=override), False

    @log_call
    def delete(self, id: int):
        _ = self.get_by_id(object_id=id)
        return self.repository.delete(id)
