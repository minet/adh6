from dataclasses import asdict
from unittest.mock import MagicMock

from pytest import fixture, raises, mark

from src.entity import AbstractRoom
from src.entity.room import Room
from src.exceptions import RoomNotFoundError, VLANNotFoundError, RoomNumberMismatchError, MissingRequiredField, \
    IntMustBePositive
from src.use_case.interface.room_repository import RoomRepository
from src.use_case.room_manager import RoomManager


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

    @mark.skip(reason="VLAN management isn't implemented yet")
    def test_update_vlan_not_found(self,
                                   ctx,
                                   mock_room_repository: RoomRepository,
                                   sample_room: Room,
                                   mutation_request: AbstractRoom,
                                   room_manager: RoomManager):
        mock_room_repository.search_by = MagicMock(return_value=([sample_room], 1))
        mock_room_repository.create = MagicMock(side_effect=VLANNotFoundError)
        with raises(VLANNotFoundError):
            room_manager.update_or_create(ctx, mutation_request, **{"room_id": sample_room.id})


@fixture
def room_manager(mock_room_repository):
    return RoomManager(
        room_repository=mock_room_repository
    )


@fixture
def mock_room_repository():
    return MagicMock(spec=RoomRepository)
