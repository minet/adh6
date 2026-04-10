import abc

from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractRoom, Room


class RoomRepository(CRUDRepository[Room, AbstractRoom]):
    @abc.abstractmethod
    async def get_from_member(self, member_id: int) -> Room | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def get_members(self, room_id: int) -> list[int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def add_member(self, room_id: int, member_id: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def remove_member(self, member_id: int) -> None:
        pass  # pragma: no cover
