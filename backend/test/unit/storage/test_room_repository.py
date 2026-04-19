from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import Room
from adh6.room.storage.models import Chambre
from adh6.room.storage.room_repository import RoomSQLRepository
from adh6.subnet.storage.models import Vlan


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.scalar = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def room_repo(mock_session):
    return RoomSQLRepository(session=mock_session)


def create_mock_chambre(id=1):
    c = MagicMock(spec=Chambre)
    c.id = id
    c.numero = 101  # Should be int
    c.description = "Test Room"
    c.vlan_id = 41
    return c


class TestRoomSQLRepository:
    async def test_get_by_id(self, room_repo, mock_session):
        # Given
        c = create_mock_chambre()
        mock_session.scalar.return_value = c

        mock_vlan = MagicMock(spec=Vlan)
        mock_vlan.numero = 41
        mock_execute_result = MagicMock()
        mock_execute_result.first.return_value = (mock_vlan,)
        mock_session.execute.return_value = mock_execute_result

        # When
        result = await room_repo.get_by_id(1)

        # Then
        assert result.id == 1
        assert result.vlan == 41

    async def test_get_from_member(self, room_repo, mock_session):
        # Given
        c = create_mock_chambre()
        mock_session.scalar.return_value = c

        mock_vlan = MagicMock(spec=Vlan)
        mock_vlan.numero = 41
        mock_execute_result = MagicMock()
        mock_execute_result.first.return_value = (mock_vlan,)
        mock_session.execute.return_value = mock_execute_result

        # When
        result = await room_repo.get_from_member(123)

        # Then
        assert result is not None
        assert result.id == 1

    async def test_search_by(self, room_repo, mock_session):
        # Given
        c = create_mock_chambre()
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [c]
        mock_execute_result.scalars.return_value.all.return_value = [c]

        mock_vlan = MagicMock(spec=Vlan)
        mock_vlan.numero = 41
        mock_vlan_result = MagicMock()
        mock_vlan_result.first.return_value = (mock_vlan,)

        # We need results for count, fetch, and mapping (vlan lookup)
        mock_session.execute.side_effect = [mock_execute_result, mock_execute_result, mock_vlan_result]

        # When
        results, count = await room_repo.search_by(terms="Room")

        # Then
        assert count == 1
        assert len(results) == 1

    async def test_create(self, room_repo, mock_session):
        # Given
        mock_vlan = MagicMock(spec=Vlan)
        mock_vlan.id = 1
        mock_vlan.numero = 42
        mock_session.scalar.return_value = mock_vlan

        mock_vlan_row = MagicMock()
        mock_vlan_row.numero = 42
        mock_execute_result = MagicMock()
        mock_execute_result.first.return_value = (mock_vlan_row,)
        mock_session.execute.return_value = mock_execute_result

        r = Room(id=None, roomNumber=102, description="New", vlan=42)

        # When
        await room_repo.create(r)

        # Then
        mock_session.add.assert_called()
        mock_session.flush.assert_called()

    async def test_delete(self, room_repo, mock_session):
        # Given
        c = create_mock_chambre()
        mock_session.scalar.return_value = c

        # When
        await room_repo.delete(1)

        # Then
        mock_session.delete.assert_called_once_with(c)
