from typing import Dict

from connexion import NoContent
from adh6.authentication.role_manager import RoleManager
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.default.util.serializer import serialize_response


class RoleHandler:
    def __init__(self, role_manager: RoleManager):
        self.role_manager = role_manager

    @with_context
    def search(self, ctx, filter_):
        try:
            result, count = self.role_manager.search(ctx=ctx, filter_=filter_)
            headers = {
                "X-Total-Count": str(count),
                'access-control-expose-headers': 'X-Total-Count'
            }
            return serialize_response(result), 200, headers
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    def post(self, ctx, body: Dict[str, str]):
        try:
            self.role_manager.create(ctx=ctx, identifier=body["login"], role=body["role"])
            return NoContent, 201
        except Exception as e:
            return handle_error(ctx, e)
