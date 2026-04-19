from unittest.mock import AsyncMock, MagicMock

from adh6.entity.port import Port
from adh6.exceptions import RoomNotFoundError, SwitchNotFoundError
from adh6.network.interfaces.port_repository import PortRepository
from adh6.network.port_manager import PortManager
from pytest import fixture, raises


class TestBulkCreate:
    async def test_happy_path(self, mock_port_repository, port_manager):
        # Given
        bodies = [MagicMock(spec=Port), MagicMock(spec=Port)]
        mock_port_repository.create = AsyncMock()

        # When
        result = await port_manager.bulk_create(bodies)

        # Then
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["errors"]) == 0
        assert mock_port_repository.create.call_count == 2

    async def test_with_failures(self, mock_port_repository, port_manager):
        # Given
        body1 = MagicMock(spec=Port)
        body1.port_number = 1
        body1.oid = "1.1"
        body2 = MagicMock(spec=Port)
        body2.port_number = 2
        body2.oid = "1.2"
        bodies = [body1, body2]
        mock_port_repository.create = AsyncMock(side_effect=[None, Exception("Failed")])

        # When
        result = await port_manager.bulk_create(bodies)

        # Then
        assert result["success"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1
        assert "Port 2 (OID 1.2): Failed" in result["errors"][0]


class TestCreate:
    async def test_unknown_room(self, mock_port_repository, sample_port: Port, port_manager: PortManager):
        # Given...
        mock_port_repository.create = AsyncMock(side_effect=RoomNotFoundError)

        # When...
        with raises(RoomNotFoundError):
            await port_manager.update_or_create(sample_port)

        # Expect..
        mock_port_repository.create.assert_called_once()

    async def test_unknown_switch(
        self, mock_port_repository: PortRepository, sample_port: Port, port_manager: PortManager
    ):
        # Given...
        mock_port_repository.create = AsyncMock(side_effect=SwitchNotFoundError)

        # When...
        with raises(SwitchNotFoundError):
            await port_manager.update_or_create(sample_port)

        # Expect..
        mock_port_repository.create.assert_called_once()


class TestUpdate:
    async def test_unknown_room(self, mock_port_repository, sample_port: Port, port_manager: PortManager):
        # Given...
        mock_port_repository.update = AsyncMock(side_effect=RoomNotFoundError)
        mock_port_repository.get_by_id = AsyncMock(return_value=sample_port)

        # When...
        with raises(RoomNotFoundError):
            await port_manager.update_or_create(sample_port, id=1)

        # Expect..
        mock_port_repository.update.assert_called_once()

    async def test_unknown_switch(self, mock_port_repository, sample_port: Port, port_manager: PortManager):
        # Given...
        mock_port_repository.update = AsyncMock(side_effect=SwitchNotFoundError)
        mock_port_repository.get_by_id = AsyncMock(return_value=sample_port)

        # When...
        with raises(SwitchNotFoundError):
            await port_manager.update_or_create(sample_port, id=1)

        # Expect..
        mock_port_repository.update.assert_called_once()


@fixture
def port_manager(
    mock_port_repository,
):
    return PortManager(port_repository=mock_port_repository)


@fixture
def mock_port_repository():
    return MagicMock(spec=PortRepository)
