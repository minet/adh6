from unittest.mock import MagicMock

from pytest import fixture, raises

from adh6.entity.port import Port
from adh6.exceptions import SwitchNotFoundError, RoomNotFoundError
from adh6.network.interfaces.port_repository import PortRepository
from adh6.network.port_manager import PortManager


class TestCreate:

    def test_unknown_room(self,
                          mock_port_repository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.create = MagicMock(side_effect=RoomNotFoundError)

        # When...
        with raises(RoomNotFoundError):
            port_manager.update_or_create(sample_port)

        # Expect..
        mock_port_repository.create.assert_called_once()

    def test_unknown_switch(self,
                            mock_port_repository: PortRepository,
                            sample_port: Port,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.create = MagicMock(side_effect=SwitchNotFoundError)

        # When...
        with raises(SwitchNotFoundError):
            port_manager.update_or_create(sample_port)

        # Expect..
        mock_port_repository.create.assert_called_once()


class TestUpdate:

    def test_unknown_room(self,
                          mock_port_repository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.update = MagicMock(side_effect=RoomNotFoundError)
        mock_port_repository.search_by = MagicMock(return_value=([sample_port], 1))

        # When...
        with raises(RoomNotFoundError):
                port_manager.update_or_create(sample_port, id=1)

        # Expect..
        mock_port_repository.update.assert_called_once()

    def test_unknown_switch(self,
                            mock_port_repository,
                            sample_port: Port,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.update = MagicMock(side_effect=SwitchNotFoundError)
        mock_port_repository.search_by = MagicMock(return_value=([sample_port], 1))

        # When...
        with raises(SwitchNotFoundError):
            port_manager.update_or_create(sample_port, id=1)

        # Expect..
        mock_port_repository.update.assert_called_once()


@fixture
def port_manager(
        mock_port_repository,
):
    return PortManager(
        port_repository=mock_port_repository
    )


@fixture
def mock_port_repository():
    return MagicMock(spec=PortRepository)
