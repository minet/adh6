# coding=utf-8

from src.entity import AbstractRoom
from src.entity.roles import Roles
from src.exceptions import RoomNotFoundError
from src.use_case.crud_manager import CRUDManager
from src.use_case.decorator.security import defines_security, SecurityDefinition
from src.use_case.interface.room_repository import RoomRepository


@defines_security(SecurityDefinition(
    item={
        "read": Roles.ADH6_ADMIN,
    },
    collection={
        "read": Roles.ADH6_ADMIN
    }
))
class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self,
                 room_repository: RoomRepository,
                 ):
        super().__init__('room', room_repository, AbstractRoom, RoomNotFoundError)
        self.room_repository = room_repository
