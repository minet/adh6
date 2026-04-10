"""Extended tests for RoomManager to increase coverage."""

from unittest.mock import AsyncMock, MagicMock

from adh6.entity.room import Room
from adh6.exceptions import RoomNotFoundError
from adh6.member.member_manager import MemberManager
from adh6.room.interfaces.room_repository import RoomRepository
from adh6.room.room_manager import RoomManager
from pytest import fixture, raises


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)


@fixture
def mock_member_manager():
    return MagicMock(spec=MemberManager)


@fixture
def room_manager(mock_room_repository, mock_member_manager):
    return RoomManager(room_repository=mock_room_repository, member_manager=mock_member_manager)


@fixture
def sample_room(faker) -> Room:
    return Room(
        id=faker.random_digit_not_null(),
        roomNumber=faker.random_int(min=100, max=9999),
        description="Test room",
        vlan=41,
    )


@fixture
def sample_room_different_vlan(faker) -> Room:
    return Room(
        id=faker.random_digit_not_null() + 100,
        roomNumber=faker.random_int(min=100, max=9999),
        description="Different VLAN room",
        vlan=42,
    )


class TestAddMember:
    async def test_room_not_found(
        self,
        mock_room_repository: RoomRepository,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_room_repository.get_by_id = AsyncMock(return_value=None)

        assert sample_room.id is not None
        with raises(RoomNotFoundError):
            await room_manager.add_member(room_id=sample_room.id, member_id=1)

    async def test_happy_path_no_previous_room(
        self,
        mock_room_repository: RoomRepository,
        mock_member_manager: MemberManager,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_room_repository.get_by_id = AsyncMock(return_value=sample_room)
        mock_member_manager.get_by_id = AsyncMock(return_value=MagicMock(id=1))
        mock_room_repository.get_from_member = AsyncMock(return_value=None)
        mock_room_repository.add_member = AsyncMock(return_value=None)
        mock_member_manager.update_subnet = AsyncMock(return_value=None)
        mock_member_manager.ethernet_vlan_changed = AsyncMock(return_value=None)

        assert sample_room.id is not None
        await room_manager.add_member(room_id=sample_room.id, member_id=1)

        mock_room_repository.add_member.assert_called_once_with(sample_room.id, 1)
        mock_member_manager.update_subnet.assert_called_once_with(member_id=1)
        mock_member_manager.ethernet_vlan_changed.assert_called_once_with(1, sample_room.vlan)

    async def test_happy_path_with_previous_room_same_vlan(
        self,
        mock_room_repository: RoomRepository,
        mock_member_manager: MemberManager,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        previous_room = Room(id=999, roomNumber=100, vlan=sample_room.vlan, description="Other room")
        mock_room_repository.get_by_id = AsyncMock(return_value=sample_room)
        mock_member_manager.get_by_id = AsyncMock(return_value=MagicMock(id=1))
        mock_room_repository.get_from_member = AsyncMock(return_value=previous_room)
        mock_room_repository.remove_member = AsyncMock(return_value=None)
        mock_room_repository.add_member = AsyncMock(return_value=None)
        mock_member_manager.ethernet_vlan_changed = AsyncMock(return_value=None)

        assert sample_room.id is not None
        await room_manager.add_member(room_id=sample_room.id, member_id=1)

        mock_room_repository.remove_member.assert_called_once_with(1)
        mock_room_repository.add_member.assert_called_once_with(sample_room.id, 1)
        # Same VLAN, so no ethernet_vlan_changed
        mock_member_manager.ethernet_vlan_changed.assert_not_called()

    async def test_happy_path_with_previous_room_different_vlan(
        self,
        mock_room_repository: RoomRepository,
        mock_member_manager: MemberManager,
        room_manager: RoomManager,
        sample_room: Room,
        sample_room_different_vlan: Room,
    ):
        mock_room_repository.get_by_id = AsyncMock(return_value=sample_room)
        mock_member_manager.get_by_id = AsyncMock(return_value=MagicMock(id=1))
        mock_room_repository.get_from_member = AsyncMock(return_value=sample_room_different_vlan)
        mock_room_repository.remove_member = AsyncMock(return_value=None)
        mock_room_repository.add_member = AsyncMock(return_value=None)
        mock_member_manager.ethernet_vlan_changed = AsyncMock(return_value=None)

        assert sample_room.id is not None
        await room_manager.add_member(room_id=sample_room.id, member_id=1)

        mock_room_repository.add_member.assert_called_once_with(sample_room.id, 1)
        mock_member_manager.ethernet_vlan_changed.assert_called_once_with(1, sample_room.vlan)


class TestRemoveMember:
    async def test_happy_path(
        self,
        mock_room_repository: RoomRepository,
        mock_member_manager: MemberManager,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_member_manager.get_by_id = AsyncMock(return_value=MagicMock(id=1))
        mock_room_repository.get_by_id = AsyncMock(return_value=sample_room)
        mock_room_repository.remove_member = AsyncMock(return_value=None)
        mock_member_manager.reset_member = AsyncMock(return_value=None)

        assert sample_room.id is not None
        await room_manager.remove_member(room_id=sample_room.id, member_id=1)

        mock_room_repository.remove_member.assert_called_once_with(1)
        mock_member_manager.reset_member.assert_called_once_with(1)

    async def test_room_not_found(
        self,
        mock_room_repository: RoomRepository,
        mock_member_manager: MemberManager,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_member_manager.get_by_id = AsyncMock(return_value=MagicMock(id=1))
        mock_room_repository.get_by_id = AsyncMock(return_value=None)

        assert sample_room.id is not None
        with raises(RoomNotFoundError):
            await room_manager.remove_member(room_id=sample_room.id, member_id=1)


class TestListMembers:
    async def test_happy_path(
        self,
        mock_room_repository: RoomRepository,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_room_repository.get_by_id = AsyncMock(return_value=sample_room)
        mock_room_repository.get_members = AsyncMock(return_value=[1, 2])

        assert sample_room.id is not None
        result = await room_manager.list_members(room_id=sample_room.id)
        assert result == [1, 2]

    async def test_room_not_found(
        self,
        mock_room_repository: RoomRepository,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_room_repository.get_by_id = AsyncMock(return_value=None)

        assert sample_room.id is not None
        with raises(RoomNotFoundError):
            await room_manager.list_members(room_id=sample_room.id)


class TestRoomFromMember:
    async def test_happy_path(
        self,
        mock_room_repository: RoomRepository,
        room_manager: RoomManager,
        sample_room: Room,
    ):
        mock_room_repository.get_from_member = AsyncMock(return_value=sample_room)

        result = await room_manager.room_from_member(member_id=1)
        assert result == sample_room.id

    async def test_no_room_found(
        self,
        mock_room_repository: RoomRepository,
        room_manager: RoomManager,
    ):
        mock_room_repository.get_from_member = AsyncMock(return_value=None)

        with raises(RoomNotFoundError):
            await room_manager.room_from_member(member_id=1)

    async def test_room_with_no_id(
        self,
        mock_room_repository: RoomRepository,
        room_manager: RoomManager,
    ):
        room_no_id = Room.model_construct(id=None, roomNumber=100, vlan=41, description="Test room")
        mock_room_repository.get_from_member = AsyncMock(return_value=room_no_id)

        with raises(RoomNotFoundError):
            await room_manager.room_from_member(member_id=1)
