from adh6.decorator import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.exceptions import RoomNotFoundError
from adh6.member.member_manager import MemberManager

from .interfaces import RoomRepository


class RoomManager(CRUDManager):
    """
    Implements all the use cases related to room management.
    """

    def __init__(self, room_repository: RoomRepository, member_manager: MemberManager):
        super().__init__(room_repository, RoomNotFoundError)
        self.room_repository = room_repository
        self.member_manager = member_manager

    @log_call
    async def add_member(self, room_id: int, member_id: int) -> None:
        room = await self.room_repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundError(room_id)
        await self.member_manager.get_by_id(member_id)

        previous_room = await self.room_repository.get_from_member(member_id)
        if previous_room:
            await self.room_repository.remove_member(member_id)

        await self.room_repository.add_member(room_id, member_id)
        if not previous_room:
            await self.member_manager.update_subnet(member_id=member_id)
            await self.member_manager.ethernet_vlan_changed(member_id, room.vlan)
        elif previous_room.vlan != room.vlan:
            await self.member_manager.ethernet_vlan_changed(member_id, room.vlan)

    @log_call
    async def remove_member(self, room_id: int, member_id: int) -> None:
        await self.member_manager.get_by_id(member_id)
        room = await self.room_repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundError(room_id)

        await self.room_repository.remove_member(member_id)
        await self.member_manager.reset_member(member_id)

    @log_call
    async def list_members(self, room_id: int) -> list[int]:
        room = await self.room_repository.get_by_id(room_id)
        if not room:
            raise RoomNotFoundError(room_id)

        return await self.room_repository.get_members(room_id=room_id)

    @log_call
    async def room_from_member(self, member_id: int) -> int:
        room = await self.room_repository.get_from_member(member_id)
        if not room or room.id is None:
            raise RoomNotFoundError
        return room.id
