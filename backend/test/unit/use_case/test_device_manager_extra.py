"""Extended tests for DeviceManager to increase coverage."""

from unittest.mock import AsyncMock, MagicMock

from adh6.device.device_ip_manager import DeviceIpManager
from adh6.device.device_manager import DeviceManager
from adh6.device.interfaces import DeviceRepository
from adh6.entity import Device
from adh6.entity.device_body import DeviceBody
from adh6.entity.member import Member
from adh6.entity.room import Room
from adh6.exceptions import DeviceAlreadyExists, DeviceNotFoundError, DevicesLimitReached, RoomNotFoundError
from adh6.member.interfaces.member_repository import MemberRepository
from adh6.room.interfaces.room_repository import RoomRepository
from pytest import fixture, raises


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)


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
def device_manager(mock_device_repository, mock_device_ip_manager, mock_member_repository, mock_room_repository):
    return DeviceManager(
        device_repository=mock_device_repository,
        device_ip_manager=mock_device_ip_manager,
        member_repository=mock_member_repository,
        room_repository=mock_room_repository,
    )


@fixture
def sample_member(faker) -> Member:
    return Member(
        id=faker.random_digit_not_null(),
        username=faker.user_name(),
        email=faker.email(),
        firstName=faker.first_name(),
        lastName=faker.last_name(),
    )


@fixture
def sample_room(faker) -> Room:
    return Room(id=faker.random_digit_not_null(), roomNumber=100, vlan=41, description="Test room")


@fixture
def sample_device(faker, sample_member) -> Device:
    return Device(
        id=faker.random_digit_not_null(),
        mac=faker.mac_address().replace(":", "-").upper(),
        member=sample_member.id,
        connectionType="wired",
        ipv4Address=faker.ipv4_public(),
        ipv6Address=faker.ipv6(),
    )


class TestPutMab:
    async def test_device_not_found(
        self,
        mock_device_repository: DeviceRepository,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=None)

        with raises(DeviceNotFoundError):
            await device_manager.put_mab(id=999)

    async def test_happy_path(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=sample_device)
        mock_device_repository.get_mab = AsyncMock(return_value=False)
        mock_device_repository.put_mab = AsyncMock(return_value=True)

        assert sample_device.id is not None
        result = await device_manager.put_mab(id=sample_device.id)

        assert result is True
        mock_device_repository.put_mab.assert_called_once_with(sample_device.id, True)


class TestGetMab:
    async def test_device_not_found(
        self,
        mock_device_repository: DeviceRepository,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=None)

        with raises(DeviceNotFoundError):
            await device_manager.get_mab(id=999)

    async def test_happy_path(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=sample_device)
        mock_device_repository.get_mab = AsyncMock(return_value=True)

        assert sample_device.id is not None
        result = await device_manager.get_mab(id=sample_device.id)

        assert result is True


class TestGetMacVendor:
    async def test_device_not_found(
        self,
        mock_device_repository: DeviceRepository,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=None)

        with raises(DeviceNotFoundError):
            await device_manager.get_mac_vendor(id=999)

    async def test_no_mac(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        device_no_mac = Device.model_construct(**{**sample_device.model_dump(), "mac": None})
        mock_device_repository.get_by_id = AsyncMock(return_value=device_no_mac)

        assert sample_device.id is not None
        result = await device_manager.get_mac_vendor(id=sample_device.id)
        assert result == "-"

    async def test_unknown_vendor(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        sample_device.mac = "AA-BB-CC-DD-EE-FF"
        mock_device_repository.get_by_id = AsyncMock(return_value=sample_device)

        assert sample_device.id is not None
        result = await device_manager.get_mac_vendor(id=sample_device.id)
        assert result == "-"


class TestCreate:
    async def test_room_not_found(
        self,
        mock_device_repository: DeviceRepository,
        mock_member_repository: MemberRepository,
        mock_room_repository: RoomRepository,
        sample_member: Member,
        device_manager: DeviceManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_room_repository.get_from_member = AsyncMock(return_value=None)

        with raises(RoomNotFoundError):
            await device_manager.create(
                DeviceBody(mac="00-11-22-33-44-55", connectionType="wired", member=sample_member.id)
            )

    async def test_device_already_exists(
        self,
        mock_device_repository: DeviceRepository,
        mock_member_repository: MemberRepository,
        mock_room_repository: RoomRepository,
        sample_member: Member,
        sample_room: Room,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_room_repository.get_from_member = AsyncMock(return_value=sample_room)
        mock_device_repository.get_by_mac = AsyncMock(return_value=sample_device)
        mock_device_repository.search_by = AsyncMock(return_value=([], 0))

        with raises(DeviceAlreadyExists):
            await device_manager.create(
                DeviceBody(mac="00-11-22-33-44-55", connectionType="wired", member=sample_member.id)
            )

    async def test_devices_limit_reached(
        self,
        mock_device_repository: DeviceRepository,
        mock_member_repository: MemberRepository,
        mock_room_repository: RoomRepository,
        sample_member: Member,
        sample_room: Room,
        device_manager: DeviceManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_room_repository.get_from_member = AsyncMock(return_value=sample_room)
        mock_device_repository.get_by_mac = AsyncMock(return_value=None)
        mock_device_repository.search_by = AsyncMock(return_value=([], 25))  # > 20 devices

        with raises(DevicesLimitReached):
            await device_manager.create(
                DeviceBody(mac="00-11-22-33-44-55", connectionType="wired", member=sample_member.id)
            )

    async def test_no_connection_type(
        self,
        mock_device_repository: DeviceRepository,
        mock_member_repository: MemberRepository,
        mock_room_repository: RoomRepository,
        sample_member: Member,
        sample_room: Room,
        device_manager: DeviceManager,
    ):
        mock_member_repository.get_by_id = AsyncMock(return_value=sample_member)
        mock_room_repository.get_from_member = AsyncMock(return_value=sample_room)

        with raises(ValueError):
            await device_manager.create(
                DeviceBody.model_construct(mac="00-11-22-33-44-55", connection_type="", member=sample_member.id)
            )


class TestGetOwner:
    async def test_device_not_found(
        self,
        mock_device_repository: DeviceRepository,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=None)

        with raises(DeviceNotFoundError):
            await device_manager.get_owner(device_id=999)

    async def test_happy_path(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        sample_member: Member,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=sample_device)
        mock_device_repository.owner = AsyncMock(return_value=sample_member.id)

        assert sample_device.id is not None
        result = await device_manager.get_owner(device_id=sample_device.id)
        assert result == sample_member.id


class TestRename:
    async def test_device_not_found(
        self,
        mock_device_repository: DeviceRepository,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=None)

        with raises(DeviceNotFoundError):
            await device_manager.rename(device_id=999, name="new_name")

    async def test_happy_path(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=sample_device)
        mock_device_repository.set_name = AsyncMock(return_value=None)

        assert sample_device.id is not None
        await device_manager.rename(device_id=sample_device.id, name="new_name")
        mock_device_repository.set_name.assert_called_once_with(sample_device.id, "new_name")


class TestGenerateWifiPassword:
    async def test_device_not_found(
        self,
        mock_device_repository: DeviceRepository,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=None)

        with raises(DeviceNotFoundError):
            await device_manager.generate_wifi_password(device_id=999)

    async def test_happy_path(
        self,
        mock_device_repository: DeviceRepository,
        sample_device: Device,
        device_manager: DeviceManager,
    ):
        mock_device_repository.get_by_id = AsyncMock(return_value=sample_device)
        mock_device_repository.set_wifi_password = AsyncMock(return_value=None)

        assert sample_device.id is not None
        result = await device_manager.generate_wifi_password(device_id=sample_device.id)
        assert len(result) == 12
        mock_device_repository.set_wifi_password.assert_called_once()
