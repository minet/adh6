# coding=utf-8 import datetime import datetime import datetime
from unittest.mock import MagicMock

from pytest import fixture, raises
from pytest_cases import parametrize_with_cases, fixture_ref, parametrize, parametrize_plus

from src.entity import AbstractDevice, AbstractAccount
from src.entity.device import Device
from src.entity.member import Member
from src.entity.room import Room
from src.exceptions import InvalidMACAddress, MissingRequiredField, InvalidIPv6, InvalidIPv4, MemberNotFoundError
from src.exceptions import NoMoreIPAvailableException, DeviceNotFoundError, IntMustBePositive
from src.use_case.account_manager import AccountManager
from src.use_case.device_manager import DeviceManager
from src.use_case.interface.account_repository import AccountRepository
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.ip_allocator import IPAllocator
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.room_repository import RoomRepository
from src.use_case.interface.vlan_repository import VLANRepository
from test.unit.use_case.conftest import sample_device, sample_account1


@fixture
def mock_device_repository():
    return MagicMock(spec=DeviceRepository)


@fixture
def device_manager(
        mock_device_repository: DeviceRepository,
):
    return DeviceManager(
        device_repository=mock_device_repository
    )


@fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)


@fixture
def account_manager(
        mock_account_repository: AccountRepository,
):
    return AccountManager(
        account_repository=mock_account_repository
    )

class TestUpdateOrCreate:
    def test_create_happy_path(self,
                               ctx,
                               faker,
                               mock_device_repository: MagicMock,
                               mock_member_repository: MagicMock,
                               mock_room_repository: MagicMock,
                               mock_ip_allocator: MagicMock,
                               sample_member: Member,
                               sample_room: Room,
                               sample_device: AbstractDevice,
                               device_manager: DeviceManager):
        ipv4 = '192.0.0.1'
        ipv6 = 'fe80::1'
        # Given...

        # That the owner exists:
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # That the device does not exist in the DB:
        mock_device_repository.search_by = MagicMock(return_value=([], 0))

        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_room_repository.search_by = MagicMock(return_value=([sample_room], 1))
        mock_ip_allocator.allocate_ip_v4 = MagicMock(return_value=ipv4)
        mock_ip_allocator.allocate_ip_v6 = MagicMock(return_value=ipv6)

        # When...
        device = device_manager.update_or_create(ctx, sample_device)

        # Expect...
        assert device is not None
        mock_device_repository.create.assert_called_once_with(ctx, sample_device)

    def test_invalid_ip_v6(self,
                           ctx,
                           faker,
                           mock_device_repository: MagicMock,
                           mock_member_repository: MagicMock,
                           mock_room_repository: MagicMock,
                           mock_ip_allocator: MagicMock,
                           sample_member: Member,
                           sample_room: Room,
                           sample_device: AbstractDevice,
                           device_manager: DeviceManager):
        ipv4 = '192.0.0.1'
        ipv6 = 'fe80::1'
        # Given...

        # That the owner exists:
        mock_member_repository.search_by = MagicMock(return_value=([sample_member], 1))

        # That the device does not exist in the DB:
        mock_device_repository.search_by = MagicMock(return_value=([], 0))

        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_room_repository.search_by = MagicMock(return_value=([sample_room], 1))
        mock_ip_allocator.allocate_ip_v4 = MagicMock(return_value=ipv4)
        mock_ip_allocator.allocate_ip_v6 = MagicMock(return_value=ipv6)

        # When...
        with raises(InvalidIPv6):
            device_manager.update_or_create(ctx, sample_device)

        # Expect...
        mock_device_repository.create_device.assert_not_called()

    def test_invalid_ip_v4(self,
                           ctx,
                           faker,
                           mock_device_repository: MagicMock,
                           mock_member_repository: MagicMock,
                           mock_room_repository: MagicMock,
                           mock_ip_allocator: MagicMock,
                           sample_member: Member,
                           sample_room: Room,
                           sample_device: AbstractDevice,
                           device_manager: DeviceManager):
        ipv4 = '192.0.0.1'
        ipv6 = 'fe80::1'
        # Given...

        # That the owner exists:
        mock_member_repository.search_member_by = MagicMock(return_value=([sample_member], 1))

        # That the device does not exist in the DB:
        mock_device_repository.search_device_by = MagicMock(return_value=([], 0))

        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_room_repository.search_room_by = MagicMock(return_value=([sample_room], 1))
        mock_ip_allocator.allocate_ip_v4 = MagicMock(return_value=ipv4)
        mock_ip_allocator.allocate_ip_v6 = MagicMock(return_value=ipv6)

        # When...
        with raises(InvalidIPv4):
            device_manager.update_or_create(ctx, sample_device)

        # Expect...
        mock_device_repository.create_device.assert_not_called()

    def test_invalid_mac(self,
                         ctx,
                         faker,
                         mock_device_repository: MagicMock,
                         mock_member_repository: MagicMock,
                         mock_room_repository: MagicMock,
                         mock_ip_allocator: MagicMock,
                         sample_member: Member,
                         sample_room: Room,
                         device_manager: DeviceManager):
        ipv4 = '192.0.0.1'
        ipv6 = 'fe80::1'
        # Given...

        # That the owner exists:
        mock_member_repository.search_member_by = MagicMock(return_value=([sample_member], 1))

        # That the device does not exist in the DB:
        mock_device_repository.search_device_by = MagicMock(return_value=([], 0))

        # That the owner has a room (needed to get the ip range to allocate the IP):
        mock_room_repository.search_room_by = MagicMock(return_value=([sample_room], 1))
        mock_ip_allocator.allocate_ip_v4 = MagicMock(return_value=ipv4)
        mock_ip_allocator.allocate_ip_v6 = MagicMock(return_value=ipv6)

        # When...
        with raises(InvalidMACAddress):
            device_manager.update_or_create(ctx, mac_address=TEST_MAC_ADDRESS1,
                                            req=MutationRequest(
                                                mac_address='invalid mac',
                                                owner_username=faker.user_name,
                                                connection_type='wired',
                                                ip_v4_address=None,
                                                ip_v6_address=None,
                                            ),
                                            )

        # Expect...
        mock_device_repository.create_device.assert_not_called()

    def test_update_happy_path(self,
                               ctx,
                               faker,
                               mock_device_repository: MagicMock,
                               mock_member_repository: MagicMock,
                               sample_member: Member,
                               sample_device: Device,
                               device_manager: DeviceManager):
        # Given...

        # That the owner exists:
        mock_member_repository.search_member_by = MagicMock(return_value=([sample_member], 1))

        # That the device exists in the DB:
        mock_device_repository.search_device_by = MagicMock(return_value=([sample_device], 1))

        # When...
        created = device_manager.update_or_create(ctx,
                                                  mac_address=sample_device.mac_address,
                                                  req=MutationRequest(
                                                      owner_username=faker.user_name,
                                                      connection_type='wireless',
                                                      mac_address=sample_device.mac_address,
                                                      ip_v4_address=None,
                                                      ip_v6_address=None,
                                                  ),
                                                  )

        # Expect...
        assert created is False
        mock_device_repository.update_device.assert_called_once_with(ctx, sample_device.mac_address,
                                                                     mac_address=sample_device.mac_address,
                                                                     owner_username=faker.user_name,
                                                                     connection_type='wireless',
                                                                     ip_v4_address=None,
                                                                     ip_v6_address=None)

    def test_create_no_room(self,
                            ctx,
                            faker,
                            mock_device_repository: MagicMock,
                            mock_member_repository: MagicMock,
                            mock_room_repository: MagicMock,
                            sample_member: Member,
                            device_manager: DeviceManager):
        # Given...

        # That the owner has no a room.
        mock_room_repository.search_room_by = MagicMock(return_value=([], 0))

        # That the owner exists:
        mock_member_repository.search_member_by = MagicMock(return_value=([sample_member], 1))

        # That the device does not exist in the DB:
        mock_device_repository.search_device_by = MagicMock(return_value=([], 0))

        # When...
        created = device_manager.update_or_create(ctx, mac_address=TEST_MAC_ADDRESS1,
                                                  req=MutationRequest(
                                                      owner_username=faker.user_name,
                                                      connection_type='wired',
                                                      mac_address=TEST_MAC_ADDRESS1,
                                                      ip_v4_address=None,
                                                      ip_v6_address=None,
                                                  ),
                                                  )

        # Expect...
        assert created is True
        mock_device_repository.create_device.assert_called_once_with(ctx, mac_address=TEST_MAC_ADDRESS1,
                                                                     owner_username=faker.user_name,
                                                                     connection_type='wired',
                                                                     ip_v4_address=None,
                                                                     ip_v6_address=None)

    def test_empty_owner_username(self,
                                  ctx,
                                  faker,
                                  mock_member_repository: MagicMock,
                                  mock_device_repository: MagicMock,
                                  device_manager: DeviceManager):
        # Given...
        mock_member_repository.search_member_by = MagicMock(return_value=([], 0))

        # When...Unnamed
        with raises(MissingRequiredField):
            device_manager.update_or_create(ctx, mac_address=TEST_MAC_ADDRESS1,
                                            req=MutationRequest(
                                                owner_username='',
                                                connection_type='wired',
                                                mac_address=TEST_MAC_ADDRESS1,
                                                ip_v4_address=None,
                                                ip_v6_address=None,
                                            ),
                                            )

        # Expect...
        mock_device_repository.create_device.assert_not_called()
        mock_device_repository.update_device.assert_not_called()

    def test_bad_username(self,
                          ctx,
                          faker,
                          mock_member_repository: MagicMock,
                          mock_device_repository: MagicMock,
                          device_manager: DeviceManager):
        # Given...
        mock_member_repository.search_member_by = MagicMock(return_value=([], 0))

        # When...
        with raises(MemberNotFoundError):
            device_manager.update_or_create(ctx, mac_address=TEST_MAC_ADDRESS1,
                                            req=MutationRequest(
                                                owner_username='hello__',
                                                connection_type='wired',
                                                mac_address=TEST_MAC_ADDRESS1,
                                                ip_v4_address=None,
                                                ip_v6_address=None,
                                            ),
                                            )

        # Expect...
        mock_device_repository.create_device.assert_not_called()
        mock_device_repository.update_device.assert_not_called()

    def test_invalid_device_type(self,
                                 ctx,
                                 faker,
                                 mock_member_repository: MagicMock,
                                 mock_device_repository: MagicMock,
                                 device_manager: DeviceManager):
        # Given...
        mock_member_repository.search_member_by = MagicMock(return_value=([], 0))

        # When...Unnamed
        with raises(ValueError):
            device_manager.update_or_create(ctx, mac_address=TEST_MAC_ADDRESS1,
                                            req=MutationRequest(
                                                owner_username='abcdefgh',
                                                connection_type='invalid',
                                                mac_address=TEST_MAC_ADDRESS1,
                                                ip_v4_address=None,
                                                ip_v6_address=None,
                                            ),
                                            )

        # Expect...
        mock_device_repository.create_device.assert_not_called()
        mock_device_repository.update_device.assert_not_called()

    def test_allocation_failed(self,
                               ctx,
                               faker,
                               mock_device_repository: MagicMock,
                               mock_member_repository: MagicMock,
                               mock_room_repository: MagicMock,
                               sample_member: Member,
                               sample_device: Device,
                               sample_room: Room,
                               mock_ip_allocator: MagicMock,
                               device_manager: DeviceManager):
        # Given...

        mock_ip_allocator.allocate_ip_v4 = MagicMock(side_effect=NoMoreIPAvailableException)

        # That the owner exists:
        mock_member_repository.search_member_by = MagicMock(return_value=([sample_member], 1))

        # That the device exists in the DB:
        mock_room_repository.search_room_by = MagicMock(return_value=([sample_room], 1))

        # That the device exists in the DB:
        mock_device_repository.search_device_by = MagicMock(return_value=([sample_device], 1))

        # When...
        with raises(NoMoreIPAvailableException):
            device_manager.update_or_create(ctx,
                                            mac_address=sample_device.mac_address,
                                            req=MutationRequest(
                                                owner_username=faker.user_name,
                                                connection_type='wired',
                                                mac_address=TEST_MAC_ADDRESS1,
                                                ip_v4_address=None,
                                                ip_v6_address=None,
                                            ),
                                            )


class TestGetByMacAddress:
    def test_happy_path(self,
                        ctx,
                        faker,
                        mock_device_repository: MagicMock,
                        sample_device,
                        device_manager: DeviceManager):
        mock_device_repository.search_device_by = MagicMock(return_value=([sample_device], 1))
        mac = faker.mac_address
        # When...
        device_manager.search(ctx, filter_=AbstractDevice(mac=mac))

        # Expect...
        mock_device_repository.search_device_by.assert_called_once_with(ctx, mac_address=mac)

    def test_device_not_found(self,
                              ctx,
                              faker,
                              mock_device_repository: MagicMock,
                              device_manager: DeviceManager):
        mock_device_repository.search_device_by = MagicMock(return_value=([], 0))
        mac = faker.mac_address
        # When...
        with raises(DeviceNotFoundError):
            device_manager.search(ctx, filter_=AbstractDevice(mac=mac))

        # Expect...
        mock_device_repository.search_device_by.assert_called_once_with(ctx, mac_address=mac)


@fixture
def mock_vlan_repository():
    return MagicMock(spec=VLANRepository)


@fixture
def mock_ip_allocator():
    return MagicMock(spec=IPAllocator)


@fixture
def mock_member_repository():
    return MagicMock(spec=MemberRepository)


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)
