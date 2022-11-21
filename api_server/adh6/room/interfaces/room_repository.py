# coding=utf-8
from typing import List, Union
from adh6.entity import Room, AbstractRoom
from adh6.default.crud_repository import CRUDRepository
import abc


class RoomRepository(CRUDRepository[Room, AbstractRoom]):
    @abc.abstractmethod
    def get_from_member(self, member_id: int) -> Union[Room, None]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_members(self, room_id: int) -> List[int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def add_member(self, room_id: int, member_id: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def remove_member(self, member_id: int) -> None:
        pass  # pragma: no cover
