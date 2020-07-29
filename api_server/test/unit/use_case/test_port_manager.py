from unittest.mock import MagicMock

from pytest import fixture, raises

from src.entity.port import Port
from src.exceptions import SwitchNotFoundError, RoomNotFoundError
from src.use_case.interface.port_repository import PortRepository
from src.use_case.port_manager import PortManager


class TestCreate:

    def test_unknown_room(self,
                          ctx,
                          mock_port_repository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.create = MagicMock(side_effect=RoomNotFoundError)

        # When...
        with raises(RoomNotFoundError):
            port_manager.update_or_create(ctx, sample_port)

        # Expect..
        mock_port_repository.create.assert_called_once()

    def test_unknown_switch(self,
                            ctx,
                            mock_port_repository: PortRepository,
                            sample_port: Port,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.create = MagicMock(side_effect=SwitchNotFoundError)

        # When...
        with raises(SwitchNotFoundError):
            port_manager.update_or_create(ctx, sample_port)

        # Expect..
        mock_port_repository.create.assert_called_once()


class TestUpdate:

    def test_unknown_room(self,
                          ctx,
                          mock_port_repository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.update = MagicMock(side_effect=RoomNotFoundError)
        mock_port_repository.search_by = MagicMock(return_value=([sample_port], 1))

        # When...
        with raises(RoomNotFoundError):
                port_manager.update_or_create(ctx, sample_port, port_id=1)

        # Expect..
        mock_port_repository.update.assert_called_once()

    def test_unknown_switch(self,
                            ctx,
                            mock_port_repository,
                            sample_port: Port,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.update = MagicMock(side_effect=SwitchNotFoundError)
        mock_port_repository.search_by = MagicMock(return_value=([sample_port], 1))

        # When...
        with raises(SwitchNotFoundError):
            port_manager.update_or_create(ctx, sample_port, port_id=1)

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
