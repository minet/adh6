# coding=utf-8
from typing import Any, List, Optional
from connexion import NoContent
from adh6.authentication import Method
from adh6.authentication.security import with_security

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.crud_manager import CRUDManager
from adh6.default.util.error import handle_error
from adh6.default.util.serializer import deserialize_request, serialize_response


class DefaultHandler:
    def __init__(self, entity_class, abstract_entity_class, main_manager: CRUDManager):
        self.entity_class = entity_class
        self.abstract_entity_class = abstract_entity_class
        self.main_manager = main_manager

    @with_context
    @with_security(method=Method.READ, arg_name="filter_")
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: Optional[Any] = None, only: Optional[List[str]]=None):
        try:
            def remove(entity: Any) -> Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id", "__typename"]:
                            del entity[k]
                return entity
            filter_ = deserialize_request(filter_, self.abstract_entity_class) if filter_ else None
            result, total_count = self.main_manager.search(ctx, limit=limit, offset=offset, terms=terms, filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(remove, map(serialize_response, result)))
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def get(self, ctx, id_: int, only: Optional[List[str]]=None):
        try:
            def remove(entity: Any) -> Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id", "__typename"]:
                            del entity[k]
                return entity
            return remove(serialize_response(self.main_manager.get_by_id(ctx, id=id_))), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @with_security()
    @log_call
    def post(self, ctx, body):
        return _update(ctx, self.main_manager.update_or_create, self.entity_class, body=body)

    @with_context
    @with_security()
    @log_call
    def put(self, ctx, body, id_: int):
        return _update(ctx, self.main_manager.update_or_create, self.entity_class, body=body, id=id_)

    @with_context
    @with_security()
    def patch(self, ctx, body, id_: int):
        return _update(ctx, self.main_manager.partially_update, self.abstract_entity_class, body=body, id=id_)

    @with_context
    @log_call
    def delete(self, ctx, id_: int):
        try:
            self.main_manager.delete(ctx, id=id_)
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)

def _update(ctx, function, klass, body, id: Optional[int] = None):
    try:
        body['id'] = 0  # Set a dummy id to pass the initial validation
        to_update = deserialize_request(body, klass)
        the_object, created = function(ctx, to_update, id=id)
        return serialize_response(the_object), 201 if created else 204
    except Exception as e:
        return handle_error(ctx, e)
