from unittest.mock import AsyncMock, MagicMock

from adh6.entity import AbstractPort
from adh6.entity.port import Port
from adh6.exceptions import RoomNotFoundError, SwitchNotFoundError
from adh6.network.interfaces.port_repository import PortRepository
from adh6.network.port_manager import PortManager
from pytest import fixture, raises


class TestBulkCreate:
    async def test_happy_path(self, mock_port_repository, port_manager):
        # Given
        bodies = [
            AbstractPort(switchObj=1, portNumber="1", oid="10101"),
            AbstractPort(switchObj=1, portNumber="2", oid="10102"),
        ]
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
        body1 = AbstractPort(switchObj=1, portNumber="1", oid="10101")
        body2 = AbstractPort(switchObj=1, portNumber="2", oid="10102")
        bodies = [body1, body2]
        mock_port_repository.create = AsyncMock(side_effect=[None, Exception("Failed")])

        # When
        result = await port_manager.bulk_create(bodies)

        # Then
        assert result["success"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1
        assert "Port 2 (OID 10102): Failed" in result["errors"][0]


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


class TestDiscoveryValidation:
    async def test_creates_with_the_name_and_index_from_snmp(self, mock_port_repository):
        network = MagicMock()
        network.discover_ports = AsyncMock(return_value=[{"portNumber": "Gi1/0/1", "oid": "10101"}])
        mock_port_repository.create = AsyncMock()
        manager = PortManager(mock_port_repository, network)
        await manager.create(AbstractPort(switchObj=1, oid="0010101", portNumber="wrong name"))
        saved = mock_port_repository.create.call_args.args[0]
        assert saved.oid == "10101"
        assert saved.port_number == "Gi1/0/1"

    async def test_rejects_unknown_numeric_index(self, mock_port_repository):
        from adh6.entity import AbstractPort
        from adh6.exceptions import ValidationError

        network = MagicMock()
        network.discover_ports = AsyncMock(return_value=[])
        manager = PortManager(mock_port_repository, network)
        with raises(ValidationError):
            await manager.create(AbstractPort(switchObj=1, oid="10101"))
        mock_port_repository.create.assert_not_called()

    async def test_bulk_discovers_once_per_switch_even_on_failure(self, mock_port_repository):
        from adh6.entity import AbstractPort
        from adh6.exceptions import NetworkManagerReadError

        network = MagicMock()
        network.discover_ports = AsyncMock(side_effect=NetworkManagerReadError("unreachable"))
        manager = PortManager(mock_port_repository, network)
        result = await manager.bulk_create(
            [AbstractPort(switchObj=1, oid="10101"), AbstractPort(switchObj=1, oid="10102")]
        )
        assert result["failed"] == 2
        assert result["success"] == 0
        network.discover_ports.assert_awaited_once_with(1)
        mock_port_repository.create.assert_not_called()
