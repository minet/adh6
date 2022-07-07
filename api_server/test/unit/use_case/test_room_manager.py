from unittest.mock import MagicMock

from pytest import fixture, raises

from adh6.entity import AbstractRoom
from adh6.entity.room import Room
from adh6.exceptions import VLANNotFoundError
from adh6.room.interfaces.room_repository import RoomRepository
from adh6.room.room_manager import RoomManager


class TestUpdateOrCreate:
    @fixture
    def mutation_request(self):
        return AbstractRoom(
            room_number='1234',
            description='desc',
            vlan='vlan',
        )

    def test_create_vlan_not_found(self,
                                   ctx,
                                   mock_room_repository: RoomRepository,
                                   mutation_request: AbstractRoom,
                                   sample_room: Room,
                                   room_manager: RoomManager):
        mock_room_repository.search_by = MagicMock(return_value=([], 0))
        mock_room_repository.create = MagicMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            room_manager.update_or_create(ctx, mutation_request)

    def test_update_vlan_not_found(self,
                                   ctx,
                                   mock_room_repository: RoomRepository,
                                   sample_room: Room,
                                   mutation_request: AbstractRoom,
                                   room_manager: RoomManager):
        mock_room_repository.search_by = MagicMock(return_value=([sample_room], 1))
        mock_room_repository.update = MagicMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            room_manager.update_or_create(ctx, mutation_request, **{"id": sample_room.id})


@fixture
def room_manager(mock_room_repository):
    return RoomManager(
        room_repository=mock_room_repository
    )


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)
