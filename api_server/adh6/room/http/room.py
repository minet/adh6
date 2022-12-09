# coding=utf-8
import typing as t

from connexion import NoContent
from adh6.constants import DEFAULT_OFFSET, DEFAULT_LIMIT
from adh6.authentication import Roles
from adh6.decorator import log_call, with_context
from adh6.entity import Room, AbstractRoom
from adh6.default import DefaultHandler
from adh6.exceptions import UnauthorizedError
from adh6.context import get_roles, get_login

from ..room_manager import RoomManager


class RoomHandler(DefaultHandler):
    def __init__(self, room_manager: RoomManager):
        super().__init__(Room, AbstractRoom, room_manager)
        self.room_manager = room_manager

    @with_context
    @log_call
    def search(self, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None, filter_: t.Optional[t.Any] = None):
        filter_ = self.abstract_entity_class.from_dict(filter_) if filter_ else None
        result, total_count = self.room_manager.search(limit=limit, offset=offset, terms=terms, filter_=filter_)
        headers = {
            "X-Total-Count": str(total_count),
            'access-control-expose-headers': 'X-Total-Count'
        }
        return list(map(lambda x: x.room_number, result)), 200, headers

    @with_context
    @log_call
    def get(self, room_number: int, only: t.Optional[t.List[str]]=None):
        room = self.room_manager.get_by_number(room_number)
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
    def put(self, room_number: int, body):
        r = self.room_manager.get_by_number(room_number)
        return super().put(body, r.id)

    @with_context
    @log_call
    def delete(self, room_number: int):
        r = self.room_manager.get_by_number(room_number)
        self.room_manager.delete(r.id)
        return NoContent, 204

    @with_context
    @log_call
    def member_search(self, room_number: int):
        return self.room_manager.list_members(room_number), 200

    @with_context
    @log_call
    def member_post(self, room_number: int, body):
        self.room_manager.add_member(room_number, body.get("login", ""))
        return NoContent, 204

    @with_context
    @log_call
    def member_delete(self, login: str):
        self.room_manager.remove_member(login=login)
        return NoContent, 204

    @with_context
    @log_call
    def member_get(self, login: int):
        if get_login() != login and Roles.ADMIN_WRITE.value not in get_roles():
            raise UnauthorizedError("Unauthorize to access this resource")
        return self.room_manager.room_from_member(login=login).room_number, 200
