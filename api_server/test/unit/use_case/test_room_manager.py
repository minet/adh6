from unittest.mock import MagicMock

from pytest import fixture, raises

from adh6.entity import AbstractRoom
from adh6.entity.room import Room
from adh6.exceptions import VLANNotFoundError
from adh6.member import MemberManager
from adh6.room.interfaces import RoomRepository
from adh6.room import RoomManager
from adh6.device import DeviceIpManager


class TestUpdateOrCreate:
    @fixture
    def mutation_request(self):
        return AbstractRoom(
            room_number='1234',
            description='desc',
            vlan='vlan',
        )

    def test_create_vlan_not_found(self,
                                   mock_room_repository: RoomRepository,
                                   mutation_request: AbstractRoom,
                                   room_manager: RoomManager):
        mock_room_repository.search_by = MagicMock(return_value=([], 0))
        mock_room_repository.create = MagicMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            room_manager.update_or_create(mutation_request)

    def test_update_vlan_not_found(self,
                                   mock_room_repository: RoomRepository,
                                   sample_room: Room,
                                   mutation_request: AbstractRoom,
                                   room_manager: RoomManager):
        mock_room_repository.get_by_id = MagicMock(return_value=(sample_room))
        mock_room_repository.update = MagicMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            room_manager.update_or_create(mutation_request, **{"id": sample_room.id})


@fixture
def room_manager(mock_room_repository, mock_member_manager, mock_device_ip_manager):
    return RoomManager(
        room_repository=mock_room_repository,
        member_manager=mock_member_manager,
        device_ip_manager=mock_device_ip_manager
    )


@fixture
def mock_member_manager():
    return MagicMock(spec=MemberManager)


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)


@fixture
def mock_device_ip_manager():
    return MagicMock(spec=DeviceIpManager)
