from unittest.mock import MagicMock

from pytest import raises
import pytest
from pytest_cases import unpack_fixture
from pytest_lazyfixture import lazy_fixture

from adh6.entity import AbstractAccount, AbstractSwitch, AbstractPort, AbstractPaymentMethod
from adh6.exceptions import IntMustBePositive, NotFoundError
from adh6.default.crud_repository import CRUDRepository
from adh6.treasury.account_manager import AccountManager
from adh6.treasury.payment_method_manager import PaymentMethodManager
from adh6.treasury.interfaces.account_repository import AccountRepository
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.network.port_manager import PortManager
from adh6.network.switch_manager import SwitchManager
from adh6.network.interfaces.port_repository import PortRepository
from adh6.network.interfaces.switch_repository import SwitchRepository


@pytest.fixture(
    params=[
        (SwitchRepository, SwitchManager, AbstractSwitch, lazy_fixture('sample_switch')),
        (PortRepository, PortManager, AbstractPort, lazy_fixture('sample_port')),
        (AccountRepository, AccountManager, AbstractAccount, lazy_fixture('sample_account1')),
        (PaymentMethodRepository, PaymentMethodManager, AbstractPaymentMethod, lazy_fixture('sample_payment_method')),
    ]
)
def data_set(request):
    return request.param


@pytest.fixture(
    ids=[
        "switch", "port", "account", "payment_method"
    ]
)
def manager(data_set):
    mock_repo = MagicMock(spec=data_set[0])
    return mock_repo, data_set[1](mock_repo), data_set[2], data_set[3]


mock_repo, mock_manager, abstract_object, mock_object = unpack_fixture(
    "mock_repo, mock_manager, abstract_object, mock_object", manager)


class TestGetByID:
    def test_happy_path(self, mock_repo, mock_object, mock_manager):
        mock_repo.get_by_id = MagicMock(return_value=(mock_object))
        result = mock_manager.get_by_id(id=mock_object.id)

        assert mock_object == result
        mock_repo.get_by_id.assert_called_once_with(mock_object.id)

    def test_object_not_found(self, mock_repo, mock_manager, mock_object):
        mock_repo.get_by_id = MagicMock(return_value=(None), side_effect=NotFoundError(""))
        with raises(NotFoundError):
            mock_manager.get_by_id(id=mock_object.id)
        mock_repo.get_by_id.assert_called_once_with(mock_object.id)


class TestSearch:
    def test_happy_path(self, mock_repo, mock_object, mock_manager, abstract_object):
        # Given...
        terms = 'blah blah blah'
        mock_repo.search_by = MagicMock(return_value=([mock_object], 1))

        # When...
        result, count = mock_manager.search(limit=10, offset=1, filter_=abstract_object(id=mock_object.id), terms=terms)

        # Expect...
        assert [mock_object] == result
        assert 1 == count
        mock_repo.search_by.assert_called_once_with(limit=10, offset=1, filter_=abstract_object(id=mock_object.id), terms=terms)

    def test_invalid_offset(self, mock_manager):
        # When...
        with raises(IntMustBePositive):
            mock_manager.search(limit=1, offset=-1, filter_=None, terms='blabla')

    def test_invalid_limit(self, mock_manager):
        # When...
        with raises(IntMustBePositive):
            mock_manager.search(limit=-1, offset=1, filter_=None, terms='blabla')


class TestUpdateOrCreate:

    def test_happy_path_create(self, mock_repo, mock_object, mock_manager):
        # Given...
        mock_repo.create = MagicMock(return_value=mock_object)

        # When...
        object, result = mock_manager.update_or_create(mock_object)

        # Expect...
        assert mock_object == object
        assert result is True
        mock_repo.create.assert_called_once_with(mock_object)

    def test_happy_path_update(self, mock_repo, mock_object, mock_manager):
        # Given...
        mock_repo.update = MagicMock(return_value=mock_object)
        mock_repo.get_by_id = MagicMock(return_value=(mock_object))
        mock_id = mock_object.id

        # When...
        object, result = mock_manager.update_or_create(mock_object, **{"id": mock_id})

        # Expect...
        assert mock_object == object
        assert result is False
        mock_repo.update.assert_called_once_with(mock_object, override=True)

    def test_happy_path_update_non_existing(self, mock_repo: CRUDRepository, mock_object, mock_manager):
        mock_repo.get_by_id = MagicMock(return_value=(None), side_effect=NotFoundError(""))
        mock_id = mock_object.id

        with raises(NotFoundError):
            mock_manager.update_or_create(mock_object, **{"id": mock_id})

        mock_repo.get_by_id.assert_called_once_with(mock_id)
        mock_repo.update.assert_not_called()
        mock_repo.create.assert_not_called()


class TestPartiallyUpdate:
    def test_happy_path(self, mock_repo, mock_object, mock_manager):
        mock_repo.update = MagicMock(return_value=mock_object)
        mock_repo.search_by = MagicMock(return_value=([mock_object], 1))
        mock_id = mock_object.id
        object, result = mock_manager.partially_update(mock_object, **{"id": mock_id})

        assert mock_object == object
        assert result == False
        mock_repo.update.assert_called_once_with(mock_object, override=False)


class TestDelete:
    def test_happy_path(self, faker, mock_repo, mock_manager):
        id = faker.random_int()
        mock_repo.get_by_id = MagicMock(return_value=(mock_object))
        mock_manager.delete(id=id)
        mock_repo.delete.assert_called_once_with(id)

    def test_object_not_found(self, faker, mock_repo, mock_manager):
        mock_repo.get_by_id = MagicMock(return_value=(None), side_effect=NotFoundError(""))
        id = faker.random_int()
        with raises(NotFoundError):
            mock_manager.delete(id=id)
