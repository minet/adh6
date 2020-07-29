from unittest.mock import MagicMock

from pytest import fixture, raises

from src.entity import AbstractTransaction, PaymentMethod
from src.entity.transaction import Transaction
from src.exceptions import TransactionNotFoundError, IntMustBePositive, UserInputError
from src.use_case.interface.caisse_repository import CaisseRepository
from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.payment_method_manager import PaymentMethodManager
from src.use_case.transaction_manager import TransactionManager, CaisseManager


class TestGetByID:
    def test_happy_path(self,
                        ctx,
                        faker,
                        mock_transaction_repository,
                        sample_transaction,
                        transaction_manager: TransactionManager):
        print(sample_transaction)
        mock_transaction_repository.search_by = MagicMock(return_value=([sample_transaction], 1))
        result = transaction_manager.get_by_id(ctx, **{"transaction_id": sample_transaction.id})

        assert sample_transaction == result
        mock_transaction_repository.search_by.assert_called_once()

    def test_transaction_not_found(self,
                                   ctx,
                                   faker,
                                   mock_transaction_repository: TransactionRepository,
                                   transaction_manager: TransactionManager):
        mock_transaction_repository.search_by = MagicMock(return_value=([], 0))

        with raises(TransactionNotFoundError):
            transaction_manager.get_by_id(ctx, **{"transaction_id": faker.random_int})


class TestSearch:
    def test_happy_path(self,
                        ctx,
                        mock_transaction_repository,
                        sample_transaction: Transaction,
                        transaction_manager: TransactionManager):
        mock_transaction_repository.search_by = MagicMock(return_value=([sample_transaction], 1))
        result, count = transaction_manager.search(ctx, limit=42, offset=2, terms='abc')

        assert [sample_transaction] == result
        assert 1 == count
        mock_transaction_repository.search_by.assert_called_once_with(ctx, limit=42, offset=2, terms='abc',
                                                                      filter_=None)

    def test_offset_negative(self,
                             ctx,
                             transaction_manager: TransactionManager):
        with raises(IntMustBePositive):
            transaction_manager.search(ctx, offset=-1)

    def test_limit_negative(self,
                            ctx,
                            transaction_manager: TransactionManager):
        with raises(IntMustBePositive):
            transaction_manager.search(ctx, limit=-1)


class TestCreate:
    def test_happy_path(self,
                        ctx, mock_transaction_repository,
                        transaction_manager: TransactionManager):
        transaction_manager.payment_method_manager.search = MagicMock(
            return_value=([PaymentMethod(id=0, name="Liquide")], 0))

        req = AbstractTransaction(
            src='1',
            dst='2',
            name='test',
            value=1,
            payment_method='1',
            attachments=None
        )
        mock_transaction_repository.create_transaction = MagicMock()

        transaction_manager.update_or_create(ctx, req)

        mock_transaction_repository.create.assert_called_once_with(ctx, req)

    def test_same_account(self,
                          ctx,
                          transaction_manager: TransactionManager):
        req = AbstractTransaction(
            src='1',
            dst='1',
            name='test',
            value=1,
            payment_method='1',
            attachments=None

        )
        with raises(UserInputError):
            transaction_manager.update_or_create(ctx, req)


@fixture
def transaction_manager(mock_transaction_repository, ):
    return TransactionManager(
        transaction_repository=mock_transaction_repository,
        payment_method_manager=mock_payment_method_manager,
        caisse_manager=mock_caisse_manager
    )


@fixture
def mock_payment_method_manager(mock_payment_method_repository):
    return PaymentMethodManager(
        payment_method_repository=mock_payment_method_repository
    )


@fixture
def mock_caisse_manager(mock_caisse_repository):
    return CaisseManager()


@fixture
def mock_transaction_repository():
    return MagicMock(spec=TransactionRepository)


@fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)


@fixture
def mock_caisse_repository():
    return MagicMock(spec=CaisseRepository)
