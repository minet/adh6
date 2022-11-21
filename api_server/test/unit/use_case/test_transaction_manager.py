from unittest.mock import MagicMock

from pytest import fixture, raises
import pytest

from adh6.entity import AbstractTransaction
from adh6.entity.transaction import Transaction
from adh6.exceptions import NotFoundError, TransactionNotFoundError, IntMustBePositive, UserInputError, ValidationError
from adh6.treasury.cashbox_manager import CashboxManager
from adh6.treasury.interfaces.cashbox_repository import CashboxRepository
from adh6.treasury.interfaces.transaction_repository import TransactionRepository
from adh6.treasury.transaction_manager import TransactionManager


class TestGetByID:
    def test_happy_path(self,
                        mock_transaction_repository,
                        sample_transaction,
                        transaction_manager: TransactionManager):
        mock_transaction_repository.get_by_id = MagicMock(return_value=(sample_transaction))
        result = transaction_manager.get_by_id(id=sample_transaction.id)

        assert sample_transaction == result
        mock_transaction_repository.get_by_id.assert_called_once()

    def test_transaction_not_found(self,
                                   faker,
                                   mock_transaction_repository: TransactionRepository,
                                   transaction_manager: TransactionManager):
        mock_transaction_repository.get_by_id = MagicMock(return_value=(None), side_effect=TransactionNotFoundError(""))

        with raises(TransactionNotFoundError):
            transaction_manager.get_by_id(id=faker.random_int)


class TestSearch:
    def test_happy_path(self,
                        mock_transaction_repository,
                        sample_transaction: Transaction,
                        transaction_manager: TransactionManager):
        mock_transaction_repository.search_by = MagicMock(return_value=([sample_transaction], 1))
        result, count = transaction_manager.search(limit=42, offset=2, terms='abc')

        assert [sample_transaction] == result
        assert 1 == count
        mock_transaction_repository.search_by.assert_called_once_with(limit=42, offset=2, terms='abc')

    def test_offset_negative(self,
                             transaction_manager: TransactionManager):
        with raises(IntMustBePositive):
            transaction_manager.search(offset=-1)

    def test_limit_negative(self,
                            transaction_manager: TransactionManager):
        with raises(IntMustBePositive):
            transaction_manager.search(limit=-1)


class TestCreateOrUpdate:
    def test_happy_path_update(self,
                               mock_transaction_repository: TransactionRepository,
                               transaction_manager: TransactionManager,
                               sample_transaction: Transaction):
        req = AbstractTransaction(
            src=sample_transaction.src,
            dst=sample_transaction.dst,
            name=sample_transaction.name,
            value=sample_transaction.value,
            payment_method=sample_transaction.payment_method,
            attachments=sample_transaction.attachments
        )
        mock_transaction_repository.create = MagicMock(return_value=(sample_transaction))
        mock_transaction_repository.get_by_id = MagicMock(return_value=(sample_transaction))
        mock_transaction_repository.update = MagicMock(return_value=(sample_transaction))

        _, c = transaction_manager.update_or_create(req, sample_transaction.id)

        assert c is False
        mock_transaction_repository.create.assert_not_called()
        mock_transaction_repository.get_by_id.assert_called_once()
        mock_transaction_repository.update.assert_called_once()

    def test_happy_path_create(self,
                               mock_transaction_repository: TransactionRepository,
                               transaction_manager: TransactionManager,
                               sample_transaction: Transaction):
        req = AbstractTransaction(
            src='1',
            dst='2',
            name='test',
            value=1,
            payment_method='1',
            attachments=None
        )
        mock_transaction_repository.create = MagicMock(return_value=(sample_transaction))

        _, c = transaction_manager.update_or_create(req)

        assert c is True
        mock_transaction_repository.create.assert_called_once_with(req)

    def test_happy_path_create_only_admin(self,
                               mock_transaction_repository: TransactionRepository,
                               transaction_manager: TransactionManager,
                               sample_transaction_pending: Transaction):
        req = AbstractTransaction(
            src=sample_transaction_pending.src,
            dst=sample_transaction_pending.dst,
            name=sample_transaction_pending.name,
            value=sample_transaction_pending.value,
            payment_method=sample_transaction_pending.payment_method,
            attachments=sample_transaction_pending.attachments
        )
        mock_transaction_repository.create = MagicMock(return_value=(sample_transaction_pending))

        r, c = transaction_manager.update_or_create(req)

        assert r.pending_validation
        assert c is True
        mock_transaction_repository.create.assert_called_once_with(req)

    def test_happy_path_create_add_cashbox(self,
                               mock_transaction_repository: TransactionRepository,
                                           mock_cashbox_repository: CashboxRepository,
                               transaction_manager: TransactionManager,
                               sample_transaction: Transaction):
        sample_transaction.cashbox = "to"
        req = AbstractTransaction(
            src=sample_transaction.src,
            dst=sample_transaction.dst,
            name=sample_transaction.name,
            value=sample_transaction.value,
            payment_method=sample_transaction.payment_method,
            attachments=sample_transaction.attachments
        )
        mock_transaction_repository.create = MagicMock(return_value=(sample_transaction))
        mock_cashbox_repository.update = MagicMock(return_value=(None))

        _, c = transaction_manager.update_or_create(req)

        assert c is True
        mock_transaction_repository.create.assert_called_once_with(req)
        mock_cashbox_repository.update.assert_called_once_with(value_modifier=sample_transaction.value, transaction=sample_transaction)

    def test_happy_path_create_remove_cashbox(self,
                                              mock_transaction_repository: TransactionRepository,
                                              mock_cashbox_repository: CashboxRepository,
                                              transaction_manager: TransactionManager,
                                              sample_transaction: Transaction):
        sample_transaction.cashbox = "from"
        req = AbstractTransaction(
            src=sample_transaction.src,
            dst=sample_transaction.dst,
            name=sample_transaction.name,
            value=sample_transaction.value,
            payment_method=sample_transaction.payment_method,
            attachments=sample_transaction.attachments
        )
        mock_transaction_repository.create = MagicMock(return_value=(sample_transaction))
        mock_cashbox_repository.update = MagicMock(return_value=(None))

        _, c = transaction_manager.update_or_create(req)

        assert c is True
        assert sample_transaction.value is not None
        mock_transaction_repository.create.assert_called_once_with(req)
        mock_cashbox_repository.update.assert_called_once_with(value_modifier=-sample_transaction.value, transaction=sample_transaction)

    def test_same_account(self,
                          transaction_manager: TransactionManager):
        req = AbstractTransaction(
            src='1',
            dst='1',
            name='test',
            value=1,
            payment_method='1',
            attachments=None

        )
        with raises(ValidationError):
            transaction_manager.update_or_create(req)

    def test_no_value(self, transaction_manager: TransactionManager):
        req = AbstractTransaction(
            src='1',
            dst='2',
            name='test',
            value=None,
            payment_method='1',
            attachments=None

        )
        with raises(ValidationError):
            transaction_manager.update_or_create(req)

    def test_negative_value(self, transaction_manager: TransactionManager):
        req = AbstractTransaction(
            src='1',
            dst='2',
            name='test',
            value=-1,
            payment_method='1',
            attachments=None

        )
        with raises(ValidationError):
            transaction_manager.update_or_create(req)

    def test_happy_path(self, transaction_manager: TransactionManager):
        req = AbstractTransaction(
            src='1',
            dst='2',
            name='test',
            value=-1,
            payment_method='1',
            attachments=None

        )
        with raises(ValidationError):
            transaction_manager.update_or_create(req)


class TestPartiallyUpdate:
    def test_happy_path(self, transaction_manager: TransactionManager):
        req = AbstractTransaction(
            name='test',
            attachments=None

        )
        with pytest.raises(NotImplementedError):
            transaction_manager.partially_update(req)

    def test_update_readonly_field(self, transaction_manager: TransactionManager):
        req = AbstractTransaction(
            author=1,
        )
        with pytest.raises(ValidationError):
            transaction_manager.partially_update(req)


class TestValidate:
    def test_happy_path(self,
                        mock_transaction_repository,
                        sample_transaction_pending: Transaction,
                        transaction_manager: TransactionManager):
        # When...
        mock_transaction_repository.get_by_id = MagicMock(return_value=(sample_transaction_pending))
        transaction_manager.validate(**{"id": sample_transaction_pending.id})

        # Expect...
        mock_transaction_repository.validate.assert_called_once_with(sample_transaction_pending.id)

    def test_cannot_validate_nonpending(self,
                        mock_transaction_repository: TransactionRepository,
                        sample_transaction: Transaction,
                        transaction_manager: TransactionManager):
        # When...
        mock_transaction_repository.get_by_id = MagicMock(return_value=(sample_transaction))
        with raises(UserInputError):
            transaction_manager.validate(**{"id": sample_transaction.id})


class TestDelete:
    def test_happy_path(self,
                        mock_transaction_repository,
                        sample_transaction_pending: Transaction,
                        transaction_manager: TransactionManager):
        # When...
        mock_transaction_repository.get_by_id = MagicMock(return_value=(sample_transaction_pending))
        transaction_manager.delete(**{"id": sample_transaction_pending.id})

        # Expect...
        mock_transaction_repository.delete.assert_called_once_with(sample_transaction_pending.id)

    def test_cannot_delete_nonpending(self,
                        mock_transaction_repository,
                        sample_transaction: Transaction,
                        transaction_manager: TransactionManager):
        # When...
        mock_transaction_repository.get_by_id = MagicMock(return_value=(sample_transaction))
        with raises(UserInputError):
            transaction_manager.delete(**{"id": sample_transaction.id})


    def test_object_not_found(self,
                        mock_transaction_repository,
                        transaction_manager: TransactionManager):
        # Given
        mock_transaction_repository.get_by_id = MagicMock(return_value=(None), side_effect=NotFoundError(""))

        with raises(NotFoundError):
            transaction_manager.delete(**{"id": 0})


@fixture
def transaction_manager(mock_transaction_repository, mock_cashbox_repository):
    return TransactionManager(
        transaction_repository=mock_transaction_repository,
        cashbox_repository=mock_cashbox_repository
    )


@fixture
def mock_cashbox_manager(mock_cashbox_repository: CashboxRepository):
    return CashboxManager(cashbox_repository=mock_cashbox_repository)


@fixture
def mock_transaction_repository():
    return MagicMock(spec=TransactionRepository)


@fixture
def mock_cashbox_repository():
    return MagicMock(spec=CashboxRepository)
