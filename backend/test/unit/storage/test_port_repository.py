from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import AbstractPort, Port
from adh6.network.storage.models import Port as SQLPort, Switch as SQLSwitch
from adh6.network.storage.port_repository import PortSQLRepository
from adh6.room.storage.models import Chambre as SQLChambre


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
def port_repo(mock_session):
    return PortSQLRepository(session=mock_session)


def create_mock_sql_port(id=1):
    port = MagicMock(spec=SQLPort)
    port.id = id
    port.numero = "1"
    port.oid = "1.1"
    port.switch_id = 1
    port.chambre_id = 1

    room = MagicMock(spec=SQLChambre)
    room.id = 1
    room.numero = 101  # Should be int
    room.description = "Test Room"
    room.vlan = MagicMock()
    room.vlan.numero = 41

    port.room = room
    return port


class TestPortSQLRepository:
    async def test_get_by_id(self, port_repo, mock_session):
        # Given
        sql_port = create_mock_sql_port()
        mock_session.scalar.return_value = sql_port

        # When
        result = await port_repo.get_by_id(1)

        # Then
        assert result.id == 1
        assert result.port_number == "1"

    async def test_search_by(self, port_repo, mock_session):
        # Given
        sql_port = create_mock_sql_port()
        mock_execute_result = MagicMock()
        mock_execute_result.all.return_value = [sql_port]
        mock_execute_result.scalars.return_value.all.return_value = [sql_port]
        mock_session.execute.return_value = mock_execute_result

        # When
        results, count = await port_repo.search_by(terms="1")

        # Then
        assert count == 1
        assert len(results) == 1

    async def test_create(self, port_repo, mock_session):
        # Given
        sw = SQLSwitch(id=1)
        room = SQLChambre(id=1)
        mock_session.scalar.side_effect = [room, sw]

        p = Port(id=None, portNumber="2", oid="1.2", room=1, switchObj=1)

        # When
        _ = await port_repo.create(p)

        # Then
        mock_session.add.assert_called()
        mock_session.flush.assert_called()

    async def test_update(self, port_repo, mock_session):
        # Given
        sql_port = create_mock_sql_port()
        mock_session.scalar.return_value = sql_port

        update_info = AbstractPort(id=1, portNumber="New")

        # When
        _ = await port_repo.update(update_info)

        # Then
        assert sql_port.numero == "New"
        mock_session.flush.assert_called()

    async def test_delete(self, port_repo, mock_session):
        # Given
        sql_port = MagicMock(spec=SQLPort)
        mock_session.scalar.return_value = sql_port

        # When
        await port_repo.delete(1)

        # Then
        mock_session.delete.assert_called_once_with(sql_port)

    async def test_get_rcom(self, port_repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 123
        mock_session.execute.return_value = mock_result

        # When
        await port_repo.get_rcom(1)

        # Then
        mock_session.execute.assert_called_once()
