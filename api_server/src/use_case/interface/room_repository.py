# coding=utf-8

from typing import List

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import Room, AbstractRoom
from src.use_case.interface.crud_repository import CRUDRepository


class RoomRepository(CRUDRepository):
    def search_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, terms=None,
                  filter_: AbstractRoom = None) -> (List[Room], int):
        raise NotImplemented

    def create(self, ctx, object_to_create: Room) -> object:
        raise NotImplemented

    def update(self, ctx, object_to_update: AbstractRoom, override=False) -> object:
        raise NotImplemented

    def delete(self, ctx, object_id) -> None:
        raise NotImplemented
