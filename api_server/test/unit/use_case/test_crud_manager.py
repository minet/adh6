from unittest.mock import MagicMock

from pytest import raises, mark
from pytest_cases import fixture_ref, parametrize_plus, fixture_plus, unpack_fixture

from src.entity import AbstractDevice, AbstractAccount, AbstractSwitch, AbstractPort, AbstractRoom, AccountType
from src.entity.abstract_payment_method import AbstractPaymentMethod
from src.entity.abstract_product import AbstractProduct
from src.exceptions import IntMustBePositive, UserInputError
from src.use_case.account_manager import AccountManager
from src.use_case.account_type_manager import AccountTypeManager
from src.use_case.device_manager import DeviceManager
from src.use_case.interface.account_repository import AccountRepository
from src.use_case.interface.account_type_repository import AccountTypeRepository
from src.use_case.interface.device_repository import DeviceRepository
from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.use_case.interface.port_repository import PortRepository
from src.use_case.interface.product_repository import ProductRepository
from src.use_case.interface.room_repository import RoomRepository
from src.use_case.interface.switch_repository import SwitchRepository
from src.use_case.payment_method_manager import PaymentMethodManager
from src.use_case.port_manager import PortManager
from src.use_case.product_manager import ProductManager
from src.use_case.room_manager import RoomManager
from src.use_case.switch_manager import SwitchManager
from test.unit.use_case.conftest import sample_account1, sample_device, sample_switch, sample_port, sample_room, \
    sample_product, sample_payment_method, sample_account_type


@fixture_plus
@parametrize_plus("repository_class, manager_class, abstract_class, mock_object",
                  [
                      (SwitchRepository, SwitchManager, AbstractSwitch, fixture_ref(sample_switch)),
                      (PortRepository, PortManager, AbstractPort, fixture_ref(sample_port)),
                      (RoomRepository, RoomManager, AbstractRoom, fixture_ref(sample_room)),
                      (AccountRepository, AccountManager, AbstractAccount, fixture_ref(sample_account1)),
                      (ProductRepository, ProductManager, AbstractProduct, fixture_ref(sample_product)),
                      (
                              PaymentMethodRepository, PaymentMethodManager, AbstractPaymentMethod,
                              fixture_ref(sample_payment_method)),
                      (AccountTypeRepository, AccountTypeManager, AccountType, fixture_ref(sample_account_type)),

                  ],
                  ids=[
                      "switch", "port", "room", "account", "product", "payment_method", "account_type"
                  ])
def manager(repository_class, manager_class, abstract_class, mock_object):
    mock_repo = MagicMock(spec=repository_class)
    return mock_repo, manager_class(mock_repo), abstract_class, mock_object


mock_repo, mock_manager, abstract_object, mock_object = unpack_fixture(
    "mock_repo, mock_manager, abstract_object, mock_object", manager)


class TestGetByID:
    def test_happy_path(self,
                        ctx,
                        mock_repo, mock_object, mock_manager):
        mock_repo.search_by = MagicMock(return_value=([mock_object], 1))
        result = mock_manager.get_by_id(ctx, **{mock_manager.name + "_id": mock_object.id})

        assert mock_object == result
        mock_repo.search_by.assert_called_once()

    def test_object_not_found(self,
                              ctx,
                              mock_repo,
                              mock_manager,
                              mock_object):
        mock_repo.search_by = MagicMock(return_value=([], 0))

        with raises(UserInputError):
            mock_manager.get_by_id(ctx, **{mock_manager.name + "_id": mock_object.id})


class TestSearch:

    def test_happy_path(self,
                        ctx,
                        faker,
                        mock_repo, mock_object, mock_manager, abstract_object):
        # Given...
        terms = 'blah blah blah'
        mock_repo.search_by = MagicMock(return_value=([mock_object], 1))

        # When...
        result, count = mock_manager.search(ctx, limit=10, offset=1, filter_=abstract_object(id=mock_object.id),
                                            terms=terms)

        # Expect...
        assert [mock_object] == result
        assert 1 == count
        mock_repo.search_by.assert_called_once_with(ctx, limit=10, offset=1, filter_=abstract_object(id=mock_object.id),
                                                    terms=terms)

    def test_invalid_offset(self,
                            ctx,
                            faker,
                            mock_manager):
        # When...
        with raises(IntMustBePositive):
            mock_manager.search(ctx, limit=1, offset=-1, filter_=None, terms='blabla')

    def test_invalid_limit(self,
                           ctx,
                           faker,
                           mock_manager):
        # When...
        with raises(IntMustBePositive):
            mock_manager.search(ctx, limit=-1, offset=1, filter_=None, terms='blabla')


class TestUpdateOrCreate:

    def test_happy_path_create(self,
                               ctx,
                               faker,
                               mock_repo, mock_object, mock_manager, abstract_object):
        # Given...
        mock_repo.create = MagicMock(return_value=mock_object)

        # When...
        object, result = mock_manager.update_or_create(ctx, mock_object)

        # Expect...
        assert mock_object == object
        assert result is True
        mock_repo.create.assert_called_once_with(ctx, mock_object)

    def test_happy_path_update(self,
                               ctx,
                               faker,
                               mock_repo, mock_object, mock_manager):
        # Given...
        mock_repo.update = MagicMock(return_value=mock_object)
        mock_repo.search_by = MagicMock(return_value=([mock_object], 1))
        mock_id = mock_object.id

        # When...
        object, result = mock_manager.update_or_create(ctx, mock_object, **{mock_manager.name + "_id": mock_id})

        # Expect...
        assert mock_object == object
        assert result is False
        mock_repo.update.assert_called_once_with(ctx, mock_object, override=True)

    def test_happy_path_update_non_existing(self,
                               ctx,
                               faker,
                               mock_repo, mock_object, mock_manager):
        # Given...
        mock_repo.search_by = MagicMock(return_value=([], 0))
        mock_id = mock_object.id

        # When...
        with raises(UserInputError):
            mock_manager.update_or_create(ctx, mock_object, **{mock_manager.name + "_id": mock_id})

        # Expect...
        mock_repo.update.assert_not_called()
        mock_repo.create.assert_not_called()


class TestPartiallyUpdate:

    def test_happy_path(self,
                        ctx,
                        faker,
                        mock_repo, mock_object, mock_manager):
        # Given...
        mock_repo.update = MagicMock(return_value=mock_object)
        mock_repo.search_by = MagicMock(return_value=([mock_object], 1))
        mock_id = mock_object.id

        # When...
        object, result = mock_manager.partially_update(ctx, mock_object, **{mock_manager.name + "_id": mock_id})

        # Expect...
        assert mock_object == object
        assert result == False
        mock_repo.update.assert_called_once_with(ctx, mock_object, override=False)


class TestDelete:
    def test_happy_path(self,
                        ctx,
                        faker,
                        mock_repo,
                        mock_manager):
        # When...
        id = faker.random_int
        mock_manager.delete(ctx, **{mock_manager.name + "_id": id})

        # Expect...
        mock_repo.delete.assert_called_once_with(ctx, id)

    def test_object_not_found(self,
                              ctx,
                              faker,
                              mock_repo,
                              mock_manager):
        # Given
        mock_repo.delete = MagicMock(side_effect=UserInputError)
        id = faker.random_int

        # When...
        with raises(UserInputError):
            mock_manager.delete(ctx, **{mock_manager.name + "_id": id})

        # Expect...
        mock_repo.delete.assert_called_once_with(ctx, id)
