from unittest.mock import AsyncMock, MagicMock

from adh6.entity import AbstractRoom
from adh6.entity.room import Room
from adh6.exceptions import VLANNotFoundError
from adh6.member.member_manager import MemberManager
from adh6.room.interfaces.room_repository import RoomRepository
from adh6.room.room_manager import RoomManager
from pytest import fixture, raises


class TestUpdateOrCreate:
    @fixture
    def mutation_request(self):
        return AbstractRoom(
            roomNumber=1234,
            description="desc",
            vlan=42,
        )

    async def test_create_vlan_not_found(
        self, mock_room_repository: RoomRepository, mutation_request: AbstractRoom, room_manager: RoomManager
    ):
        mock_room_repository.search_by = AsyncMock(return_value=([], 0))
        mock_room_repository.create = AsyncMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            await room_manager.update_or_create(mutation_request)

    async def test_update_vlan_not_found(
        self,
        mock_room_repository: RoomRepository,
        sample_room: Room,
        mutation_request: AbstractRoom,
        room_manager: RoomManager,
    ):
        mock_room_repository.get_by_id = AsyncMock(return_value=sample_room)
        mock_room_repository.update = AsyncMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            await room_manager.update_or_create(mutation_request, id=sample_room.id)


@fixture
def room_manager(mock_room_repository, mock_member_manager):
    return RoomManager(room_repository=mock_room_repository, member_manager=mock_member_manager)


@fixture
def mock_member_manager():
    return MagicMock(spec=MemberManager)


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)
