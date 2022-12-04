# coding=utf-8
import typing as t

from connexion import NoContent
from adh6.authentication import Roles
from adh6.decorator import log_call, with_context
from adh6.entity import Room, AbstractRoom
from adh6.default import DefaultHandler
from adh6.exceptions import UnauthorizedError
from adh6.context import get_user, get_roles

from ..room_manager import RoomManager


class RoomHandler(DefaultHandler):
    def __init__(self, room_manager: RoomManager):
        super().__init__(Room, AbstractRoom, room_manager)
        self.room_manager = room_manager

    @with_context
    @log_call
    def get(self, id_: int, only: t.Optional[t.List[str]]=None):
        room = self.room_manager.get_by_id(id_)
        def remove(entity: t.Any) -> t.Any:
            if isinstance(entity, dict) and only is not None:
                entity_cp = entity.copy()
                for k in entity_cp.keys():
                    if k not in only + ["id"]:
                        del entity[k]
            return entity
        return remove(room.to_dict()), 200

    @with_context
    @log_call
    def member_search(self, id_: int):
        return self.room_manager.list_members(id_), 200

    @with_context
    @log_call
    def member_post(self, id_: int, body):
        self.room_manager.add_member(id_, body.get("id", -1))
        return NoContent, 204

    @with_context
    @log_call
    def member_delete(self, id_: int, member_id: int):
        self.room_manager.remove_member(id_, member_id)
        return NoContent, 204

    @with_context
    @log_call
    def member_add_patch(self, id_: int, body):
        return self.member_post(id_=id_, body=body)

    @with_context
    @log_call
    def member_del_patch(self, id_: int, member_id: int):
        return self.member_delete(id_=id_, member_id=member_id)

    @with_context
    @log_call
    def member_get(self, id_: int):
        if get_user() != id_ and Roles.ADMIN_WRITE.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.room_manager.room_from_member(id_).id, 200
