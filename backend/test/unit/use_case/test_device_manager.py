from unittest.mock import AsyncMock, MagicMock

from adh6.device.device_ip_manager import DeviceIpManager
from adh6.device.device_manager import DeviceManager
from adh6.device.interfaces import DeviceRepository
from adh6.entity import AbstractDevice
from adh6.entity.device_body import DeviceBody
from adh6.entity.member import Member
from adh6.entity.room import Room
from adh6.exceptions import InvalidMACAddress, MemberNotFoundError
from adh6.member.interfaces.member_repository import MemberRepository
from adh6.room.interfaces.room_repository import RoomRepository
from pytest import fixture, mark, raises


@fixture
def device_manager(
    mock_device_ip_manager: DeviceIpManager,
    mock_device_repository: DeviceRepository,
    mock_member_repository: MemberRepository,
    mock_room_repository: RoomRepository,
):
    return DeviceManager(
        device_repository=mock_device_repository,
        device_ip_manager=mock_device_ip_manager,
        member_repository=mock_member_repository,
        room_repository=mock_room_repository,
    )


class TestUpdateOrCreate:
    async def test_create_happy_path(
        self,
        mock_device_ip_manager: DeviceIpManager,
        mock_device_repository: DeviceRepository,
        mock_member_repository: MemberRepository,
        mock_room_repository: RoomRepository,
        sample_member: Member,
        sample_room: Room,
        sample_device: AbstractDevice,
        device_manager: DeviceManager,
    ):
        # That the owner exists:
        mock_member_repository.get_by_id = AsyncMock(return_value=(sample_member))

        # That the device does not exist in the DB:
        mock_device_repository.get_by_mac = AsyncMock(return_value=(None))
        # That the device does not exist in the DB:
        mock_device_repository.search_by = AsyncMock(return_value=([], 0))
        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_room_repository.get_from_member = AsyncMock(return_value=sample_room)
        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_device_repository.create = AsyncMock(return_value=(sample_device))
        mock_device_ip_manager.allocate_ip_with_vlan_number = AsyncMock(return_value=None)

        body = DeviceBody(
            mac=sample_device.mac, member=sample_device.member, connection_type=sample_device.connection_type
        )
        # When...
        device = await device_manager.create(body)

        # Expect...
        assert device is not None
        # mock_device_repository.create.assert_called_once_with(sample_device)

    async def test_invalid_mac(self, mock_device_repository: MagicMock, device_manager: DeviceManager):
        # When...
        with raises(InvalidMACAddress):
            await device_manager.create(DeviceBody(mac="this is not a valid mac", connection_type="wired", member=1))

        # Expect...
        mock_device_repository.create.assert_not_called()

    async def test_bad_member(
        self, mock_member_repository: MemberRepository, mock_device_repository: MagicMock, device_manager: DeviceManager
    ):
        # Given...
        mock_member_repository.get_by_id = AsyncMock(return_value=(None))

        # When...
        with raises(MemberNotFoundError):
            await device_manager.create(DeviceBody(mac="00:00:00:00:00:00", connection_type="wired", member=4242))

        # Expect...
        mock_device_repository.create.assert_not_called()
        mock_device_repository.update.assert_not_called()


@fixture
def mock_device_ip_manager():
    return MagicMock(spec=DeviceIpManager)


@fixture
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)
