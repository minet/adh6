# coding=utf-8
import typing as t
from connexion import NoContent

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call, with_context
from adh6.default.crud_manager import CRUDManager
from adh6.entity.base_model_ import Model


class DefaultHandler:
    def __init__(self, entity_class: t.Type[Model], abstract_entity_class: t.Type[Model], main_manager: CRUDManager):
        self.entity_class = entity_class
        self.abstract_entity_class = abstract_entity_class
        self.main_manager = main_manager

    @with_context
    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: t.Optional[t.Any] = None, only: t.Optional[t.List[str]]=None):
        def remove(entity: t.Any) -> t.Any:
            if isinstance(entity, dict) and only is not None:
                entity_cp = entity.copy()
                for k in entity_cp.keys():
                    if k not in only + ["id"]:
                        del entity[k]
            return entity
        filter_ = self.abstract_entity_class.from_dict(filter_) if filter_ else None
        result, total_count = self.main_manager.search(limit=limit, offset=offset, terms=terms, filter_=filter_)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return list(map(remove, map(lambda x: x.to_dict(), result))), 200, headers

    @with_context
    @log_call
    def get(self, id_: int, only: t.Optional[t.List[str]]=None):
        def remove(entity: t.Any) -> t.Any:
            if isinstance(entity, dict) and only is not None:
                entity_cp = entity.copy()
                for k in entity_cp.keys():
                    if k not in only + ["id"]:
                        del entity[k]
            return entity
        return remove(self.main_manager.get_by_id(id=id_).to_dict()), 200

    @with_context
    @log_call
    def post(self, body):
        return self._update(function=self.main_manager.update_or_create, klass=self.entity_class, body=body)

    @with_context
    @log_call
    def put(self, body, id_: int):
        return self._update(function=self.main_manager.update_or_create, klass=self.entity_class, body=body, id=id_)

    @with_context
    def patch(self, body, id_: int):
        return self._update(function=self.main_manager.partially_update, klass=self.abstract_entity_class, body=body, id=id_)

    @with_context
    @log_call
    def delete(self, id_: int):
        self.main_manager.delete(id=id_)
        return NoContent, 204  # 204 No Content

    def _update(self, function, klass: t.Type[Model], body, id: t.Optional[int] = None):
        body['id'] = 0  # Set a dummy id to pass the initial validation
        to_update = klass.from_dict(body) 
        the_object, created = function(to_update, id=id)
        return the_object.to_dict(), 201 if created else 204
