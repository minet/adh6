# coding=utf-8
from src.entity import Room, AbstractRoom
from src.use_case.interface.crud_repository import CRUDRepository


class RoomRepository(CRUDRepository[Room, AbstractRoom]):
    pass  # pragma: no cover
