# coding=utf-8

from adh6.entity import AbstractRoom
from adh6.exceptions import RoomNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.room.interfaces.room_repository import RoomRepository
from adh6.authentication.security import SecurityDefinition, defines_security, is_admin

@defines_security(SecurityDefinition(
    item={
        "read": is_admin(),
        "update": is_admin(),
        "delete": is_admin(),
    },
    collection={
        "read": is_admin(),
        "create" : is_admin(),
    }
))

class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self, room_repository: RoomRepository):
        super().__init__(room_repository, AbstractRoom, RoomNotFoundError)
        self.room_repository = room_repository
