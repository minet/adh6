# coding=utf-8

from adh6.entity import AbstractRoom
from adh6.exceptions import RoomNotFoundError
from adh6.default.crud_manager import CRUDManager
from adh6.room.interfaces.room_repository import RoomRepository


class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self, room_repository: RoomRepository):
        super().__init__(room_repository, AbstractRoom, RoomNotFoundError)
        self.room_repository = room_repository
