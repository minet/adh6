# coding=utf-8 import datetime import datetime import datetime
from unittest.mock import MagicMock

from pytest import fixture, raises, mark

from adh6.entity import AbstractDevice, DeviceBody, Member, Room
from adh6.exceptions import InvalidMACAddress, MemberNotFoundError
from adh6.device import DeviceManager, DeviceIpManager
from adh6.device.interfaces import DeviceRepository
from adh6.member import MemberManager
from adh6.room import RoomManager


@fixture
def device_manager(
        mock_device_ip_manager: DeviceIpManager,
        mock_device_repository: DeviceRepository,
        mock_member_manager: MemberManager,
        mock_room_manager: RoomManager
):
    return DeviceManager(
        device_repository=mock_device_repository,
        device_ip_manager=mock_device_ip_manager,
        member_manager=mock_member_manager,
        room_manager=mock_room_manager
    )


class TestUpdateOrCreate:
    def test_create_happy_path(self,
                               mock_device_repository: DeviceRepository,
                               mock_member_manager: MemberManager,
                               mock_room_manager: RoomManager,
                               sample_member: Member,
                               sample_room: Room,
                               sample_device: AbstractDevice,
                               device_manager: DeviceManager):
        # That the owner exists:
        mock_member_manager.get_by_id = MagicMock(return_value=(sample_member))

        # That the device does not exist in the DB:
        mock_device_repository.get_by_mac = MagicMock(return_value=(None))
        # That the device does not exist in the DB:
        mock_device_repository.search_by = MagicMock(return_value=([], 0))
        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_room_manager.search_by = MagicMock(return_value=([sample_room], 1))
        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_device_repository.create = MagicMock(return_value=(sample_device))

        body = DeviceBody(mac=sample_device.mac, member=sample_device.member, connection_type=sample_device.connection_type)
        # When...
        device = device_manager.create(body)

        # Expect...
        assert device is not None
        #mock_device_repository.create.assert_called_once_with(sample_device)

    def test_invalid_mac(self,
                         mock_device_repository: DeviceRepository,
                         device_manager: DeviceManager):

        # When...
        with raises(InvalidMACAddress):
            device_manager.create(DeviceBody(mac='this is not a valid mac'))

        # Expect...
        mock_device_repository.create.assert_not_called()

    @mark.skip(reason="Should we implement the relations logic in the managers ?")
    def test_bad_member(self,
                        mock_member_manager: MemberManager,
                        mock_device_repository: DeviceRepository,
                        device_manager: DeviceManager):
        # Given...
        mock_member_manager.get_by_id = MagicMock(return_value=(None))

        # When...
        with raises(MemberNotFoundError):
            device_manager.create(DeviceBody(mac="00:00:00:00:00:00", member=4242))

        # Expect...
        mock_device_repository.create.assert_not_called()
        mock_device_repository.update.assert_not_called()


@fixture
def mock_device_ip_manager():
    return MagicMock(spec=DeviceIpManager)


@fixture
def mock_member_manager():
    return MagicMock(spec=MemberManager)


@fixture
def mock_room_manager():
    return MagicMock(spec=RoomManager)


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)
