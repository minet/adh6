# coding=utf-8
import typing as t
from adh6.authentication import Roles
from adh6.constants import CTX_ADMIN, CTX_ROLES
from adh6.default.decorator.log_call import log_call
from adh6.default.decorator.with_context import with_context
from adh6.default.util.error import handle_error
from adh6.default.util.serializer import serialize_response
from adh6.entity import Room, AbstractRoom
from adh6.default.http_handler import DefaultHandler
from adh6.exceptions import UnauthorizedError
from adh6.room.room_manager import RoomManager


class RoomHandler(DefaultHandler):
    def __init__(self, room_manager: RoomManager):
        super().__init__(Room, AbstractRoom, room_manager)
        self.room_manager = room_manager

    @with_context
    @log_call
    def get(self, ctx, id_: int, only: t.Optional[t.List[str]]=None):
        try:
            members = self.room_manager.list_members(ctx, id_)
            print(members)
            if ctx.get(CTX_ADMIN) not in members and Roles.ADMIN_WRITE.value not in ctx.get(CTX_ROLES, []):
                raise UnauthorizedError("Unauthorize to access this resource")

            room = self.room_manager.get_by_id(ctx, id_)
            def remove(entity: t.Any) -> t.Any:
                if isinstance(entity, dict) and only is not None:
                    entity_cp = entity.copy()
                    for k in entity_cp.keys():
                        if k not in only + ["id", "__typename"]:
                            del entity[k]
                return entity
            return remove(serialize_response(room)), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def member_search(self, ctx, id_: int):
        try:
            return self.room_manager.list_members(ctx, id_), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def member_add_patch(self, ctx, id_: int, body):
        try:
            print(body)
            return self.room_manager.add_member(ctx, id_, body), 200
        except Exception as e:
            return handle_error(ctx, e)

    @with_context
    @log_call
    def member_del_patch(self, ctx, id_: int, body):
        try:
            print(body)
            return self.room_manager.remove_member(ctx, id_, body), 200
        except Exception as e:
            return handle_error(ctx, e)
