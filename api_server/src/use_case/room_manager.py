# coding=utf-8

from src.entity import AbstractRoom
from src.exceptions import RoomNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.room_repository import RoomRepository
from src.use_case.decorator.security import SecurityDefinition, defines_security, is_admin

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
