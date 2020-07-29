from dataclasses import asdict
from unittest.mock import MagicMock

from pytest import fixture, raises, mark

from src.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity import AbstractPort
from src.entity.port import Port
from src.exceptions import SwitchNotFoundError, RoomNotFoundError, PortNotFoundError, IntMustBePositive
from src.use_case.interface.port_repository import PortRepository
from src.use_case.port_manager import PortManager


class TestSearch:
    def test_happy_path(self,
                        ctx,
                        mock_port_repository: PortRepository,
                        sample_port: Port,
                        port_manager: PortManager):
        mock_port_repository.search_port_by = MagicMock(return_value=([sample_port], 1))

        port = AbstractPort(
            id=1
        )
        result, count = port_manager.search(ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, _filter=port)

        assert [sample_port] == result
        assert 1 == count
        mock_port_repository.search_port_by.assert_called_once_with(ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET,
                                                                    _filter=port)

    def test_invalid_offset(self,
                            ctx,
                            port_manager: PortManager):
        with raises(IntMustBePositive):
            port_manager.search(ctx, offset=-1)

    def test_invalid_limit(self,
                           ctx,
                           port_manager: PortManager):
        with raises(IntMustBePositive):
            port_manager.search(ctx, limit=-1)


class TestCreate:

    def test_happy_path(self,
                        ctx,
                        mock_port_repository: PortRepository,
                        sample_port: Port,
                        port_manager: PortManager):
        # Given...
        mock_port_repository.create_port = MagicMock()

        # When...
        port_manager.update_or_create(ctx, sample_port)

        # Expect...
        mock_port_repository.create_port.assert_called_once_with(ctx, sample_port)

    @mark.parametrize('field,value', [
        ('port_number', ''),
        ('port_number', None),

        ('switch', ''),
        ('switch', None),
    ])
    def test_invalid_mutation_request(self,
                                      ctx,
                                      mock_port_repository: PortRepository,
                                      field: str,
                                      value,
                                      sample_port: Port,
                                      port_manager: PortManager):
        # Given...
        mock_port_repository.create_port = MagicMock()

        req = Port(**{**asdict(sample_port), **{field: value}})

        # When...
        with raises(ValueError):
            port_manager.update_or_create(ctx, req)

        # Expect...
        mock_port_repository.create_port.assert_not_called()

    def test_unknown_room(self,
                          ctx,
                          mock_port_repository: PortRepository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.create_port = MagicMock(side_effect=RoomNotFoundError)

        # When...
        with raises(RoomNotFoundError):
            port_manager.update_or_create(ctx, sample_port)

        # Expect..
        mock_port_repository.create_port.assert_called_once()

    def test_unknown_switch(self,
                            ctx,
                            mock_port_repository: PortRepository,
                            sample_port: Port,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.create_port = MagicMock(side_effect=SwitchNotFoundError)

        # When...
        with raises(SwitchNotFoundError):
            port_manager.update_or_create(ctx, sample_port)

        # Expect..
        mock_port_repository.create_port.assert_called_once()


class TestUpdate:

    def test_happy_path(self,
                        ctx,
                        mock_port_repository: PortRepository,
                        sample_port: Port,
                        port_manager: PortManager):
        # Given...
        mock_port_repository.update_port = MagicMock()

        # When...
        port_manager.update_or_create(ctx, '1', sample_port)

        # Expect...
        mock_port_repository.update_port.assert_called_once_with(ctx, sample_port, port_id=1)

    def test_unknown_room(self,
                          ctx,
                          mock_port_repository: PortRepository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.update_port = MagicMock(side_effect=RoomNotFoundError)

        # When...
        with raises(RoomNotFoundError):
            port_manager.update_or_create(ctx, sample_port, port_id=1)

        # Expect..
        mock_port_repository.update_port.assert_called_once()

    def test_unknown_port(self,
                          ctx,
                          mock_port_repository: PortRepository,
                          sample_port: Port,
                          port_manager: PortManager):
        # Given...
        mock_port_repository.update_port = MagicMock(side_effect=PortNotFoundError)

        # When...
        with raises(PortNotFoundError):
            port_manager.update_or_create(ctx, '1', sample_port)

        # Expect..
        mock_port_repository.update_port.assert_called_once()

    def test_unknown_switch(self,
                            ctx,
                            mock_port_repository: PortRepository,
                            sample_port: Port,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.update_port = MagicMock(side_effect=SwitchNotFoundError)

        # When...
        with raises(SwitchNotFoundError):
            port_manager.update_or_create(ctx, '1', sample_port)

        # Expect..
        mock_port_repository.update_port.assert_called_once()


class TestDelete:
    def test_happy_path(self,
                        ctx,
                        mock_port_repository: PortRepository,
                        port_manager: PortManager):
        # Given...
        mock_port_repository.delete_port = MagicMock()

        # When...
        port_manager.delete(ctx, 'portID')

        # Expect...
        mock_port_repository.delete_port.assert_called_once_with(ctx, 'portID')

    def test_port_not_found(self,
                            ctx,
                            mock_port_repository: PortRepository,
                            port_manager: PortManager):
        # Given...
        mock_port_repository.delete_port = MagicMock(side_effect=PortNotFoundError)

        # When...
        with raises(PortNotFoundError):
            port_manager.delete(ctx, 'portID')


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
