# coding=utf-8
from adh6.entity import Room, AbstractRoom
from adh6.default.crud_repository import CRUDRepository


class RoomRepository(CRUDRepository[Room, AbstractRoom]):
    pass  # pragma: no cover
