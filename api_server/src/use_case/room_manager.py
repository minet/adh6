# coding=utf-8

from src.entity import AbstractRoom
from src.exceptions import RoomNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.interface.room_repository import RoomRepository


class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self,
                 room_repository: RoomRepository,
                 ):
        super().__init__('room', room_repository, AbstractRoom, RoomNotFoundError)
        self.room_repository = room_repository
