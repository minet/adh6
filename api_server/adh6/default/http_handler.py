# coding=utf-8
from typing import Any, List, Optional, Type
from connexion import NoContent
from flask_sqlalchemy.model import camel_to_snake_case
from adh6.authentication import Method
from adh6.authentication.security import with_security

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.crud_manager import CRUDManager
from adh6.default.util.error import handle_error
from adh6.entity.base_model_ import Model


class DefaultHandler:
    def __init__(self, entity_class: Type[Model], abstract_entity_class: Type[Model], main_manager: CRUDManager):
        self.entity_class = entity_class
        self.abstract_entity_class = abstract_entity_class
        self.main_manager = main_manager

    @with_context
    @with_security(method=Method.READ, arg_name="filter_")
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[Any] = None, only: Optional[List[str]]=None):
        try:
            only = list(map(camel_to_snake_case, only)) if only else None
            def remove(entity: Any) -> Any:
                print(entity)
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id"]:
                            del entity[k]
                print(entity)
                return entity
            filter_ = self.abstract_entity_class.from_dict(filter_) if filter_ else None
            result, total_count = self.main_manager.search(ctx, limit=limit, offset=offset, terms=terms, filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            return list(map(remove, map(lambda x: x.to_dict(), result))), 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def get(self, ctx, id_: int, only: Optional[List[str]]=None):
        try:
            only = list(map(camel_to_snake_case, only)) if only else None
            def remove(entity: Any) -> Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id"]:
                            del entity[k]
                return entity
            return remove(self.main_manager.get_by_id(ctx, id=id_).to_dict()), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @with_security()
    @log_call
    def post(self, ctx, body):
        return self._update(ctx=ctx, function=self.main_manager.update_or_create, klass=self.entity_class, body=body)

    @with_context
    @with_security()
    @log_call
    def put(self, ctx, body, id_: int):
        return self._update(ctx=ctx, function=self.main_manager.update_or_create, klass=self.entity_class, body=body, id=id_)

    @with_context
    @with_security()
    def patch(self, ctx, body, id_: int):
        return self._update(ctx=ctx, function=self.main_manager.partially_update, klass=self.abstract_entity_class, body=body, id=id_)

    @with_context
    @log_call
    def delete(self, ctx, id_: int):
        try:
            self.main_manager.delete(ctx, id=id_)
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)

    def _update(self, ctx, function, klass: Type[Model], body, id: Optional[int] = None):
        try:
            body['id'] = 0  # Set a dummy id to pass the initial validation
            to_update = klass.from_dict(body) 
            the_object, created = function(ctx, to_update, id=id)
            return the_object.to_dict(), 201 if created else 204
        except Exception as e:
            return handle_error(ctx, e)
