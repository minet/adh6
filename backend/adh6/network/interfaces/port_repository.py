from adh6.default.crud_repository import CRUDRepository
from adh6.entity import AbstractPort, Port


class PortRepository(CRUDRepository[Port, AbstractPort]):
    async def assign_room(self, port_id: int, room_id: int | None, expected_room: int | None) -> Port:
        raise NotImplementedError
