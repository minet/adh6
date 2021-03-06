# coding=utf-8
from connexion import NoContent

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.exceptions import NotFoundError, ValidationError, UserInputError, UnauthorizedError, UnauthenticatedError
from src.interface_adapter.http_api.decorator.log_call import log_call
from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.http_api.util.error import handle_error, _error
from src.interface_adapter.http_api.util.serializer import deserialize_request, serialize_response
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.crud_manager import CRUDManager
from src.util.context import log_extra
from src.util.log import LOG


class DefaultHandler:
    def __init__(self, entity_class, abstract_entity_class, main_manager: CRUDManager):
        self.entity_class = entity_class
        self.abstract_entity_class = abstract_entity_class
        self.main_manager = main_manager

    @with_context
    @require_sql
    @log_call
    def search(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_=None):
        try:
            filter_ = deserialize_request(filter_, self.abstract_entity_class)
            result, total_count = self.main_manager.search(ctx, limit=limit, offset=offset, terms=terms,
                                                           filter_=filter_)
            headers = {
                "X-Total-Count": str(total_count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            result = list(map(serialize_response, result))
            return result, 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def get(self, ctx, **kwargs):
        try:
            return serialize_response(self.main_manager.get_by_id(ctx, **kwargs)), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def post(self, ctx, body):
        try:
            body['id'] = 0  # Set a dummy id to pass the initial validation
            to_create = deserialize_request(body, self.entity_class)
            object, created = self.main_manager.update_or_create(ctx, to_create)
            if created:
                return serialize_response(object), 201
            else:
                return _error(500, "The server encountered an unexpected error"), 500
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @require_sql
    @log_call
    def put(self, ctx, *args, **kwargs):
        return _update(ctx, self.main_manager.update_or_create, self.entity_class, *args, **kwargs)

    @with_context
    @require_sql
    @log_call
    def patch(self, ctx, *args, **kwargs):
        return _update(ctx, self.main_manager.partially_update, self.abstract_entity_class, *args, **kwargs)

    @with_context
    @require_sql
    @log_call
    def delete(self, ctx, *args, **kwargs):
        try:
            self.main_manager.delete(ctx, **kwargs)
            return NoContent, 204  # 204 No Content
        except Exception as e:
            return handle_error(ctx, e)


def _update(ctx, function, klass, *args, **kwargs):
    try:
        body = kwargs.pop('body', None)
        body['id'] = 0  # Set a dummy id to pass the initial validation
        to_update = deserialize_request(body, klass)
        the_object, created = function(ctx, to_update, *args, **kwargs)
        if the_object:
            return serialize_response(the_object), 201 if created else 204
        else:
            return _error(500, "The server encountered an unexpected error"), 500
    except Exception as e:
        return handle_error(ctx, e)
