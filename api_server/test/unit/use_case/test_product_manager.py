from unittest.mock import MagicMock

import pytest
from adh6.entity import Account, PaymentMethod, Product
from adh6.exceptions import AccountNotFoundError, NotFoundError, PaymentMethodNotFoundError, ProductNotFoundError
from adh6.treasury import AccountManager
from adh6.treasury.interfaces import PaymentMethodRepository, ProductRepository, TransactionRepository
from adh6.treasury.product_manager import ProductManager


class TestBuy:
    def test_happy_path(self,
                        sample_account1: Account, 
                        sample_account2: Account,
                        sample_product: Product,
                        sample_payment_method: PaymentMethod, 
                        mock_payment_method_repository: PaymentMethodRepository, 
                        mock_account_manager: AccountManager,
                        mock_product_repository: ProductRepository,
                        mock_transaction_repository: TransactionRepository,
                        product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_account_manager.get_by_member = MagicMock(return_value=(sample_account1))
        mock_product_repository.get_by_id = MagicMock(return_value=(sample_product))
        mock_transaction_repository.create = MagicMock()

        product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_manager.get_by_member.assert_called()
        mock_product_repository.get_by_id.assert_called_once_with(1)
        mock_transaction_repository.create.assert_called_once()

    def test_no_products(self, product_manager):
        with pytest.raises(NotFoundError):
            product_manager.buy(0, 0, [])

    def test_payment_method_not_found(self, mock_payment_method_repository: PaymentMethodRepository, product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(None), side_effect=PaymentMethodNotFoundError("0"))

        with pytest.raises(PaymentMethodNotFoundError):
            product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)

    def test_dst_technical_account_not_found(self, sample_payment_method, mock_payment_method_repository: PaymentMethodRepository, mock_account_manager: AccountManager, product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_account_manager.get_by_name = MagicMock(return_value=(None), side_effect=AccountNotFoundError("0"))

        with pytest.raises(AccountNotFoundError):
            product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_manager.get_by_name.assert_called_once()

    def test_src_account_not_found(self, sample_account1, sample_payment_method, mock_payment_method_repository: PaymentMethodRepository, mock_account_manager: AccountManager, product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_account_manager.get_by_name = MagicMock(return_value=(sample_account1))
        mock_account_manager.get_by_member = MagicMock(return_value=(None), side_effect=AccountNotFoundError("0"))

        with pytest.raises(AccountNotFoundError):
            product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_manager.get_by_name.assert_called_once()
        mock_account_manager.get_by_member.assert_called_once_with(0)

    def test_product_not_found(self,
                               sample_account1: Account, 
                               sample_account2: Account, 
                               sample_payment_method: PaymentMethod, 
                               mock_payment_method_repository: PaymentMethodRepository, 
                               mock_account_manager: AccountManager,
                               mock_product_repository: ProductRepository,
                               product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_account_manager.get_by_member = MagicMock(return_value=(sample_account1))
        mock_product_repository.get_by_id = MagicMock(side_effect=ProductNotFoundError(""))

        with pytest.raises(ProductNotFoundError):
            product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_manager.get_by_member.assert_called()
        mock_product_repository.get_by_id.assert_called_once_with(1)


@pytest.fixture
def product_manager(
        mock_product_repository: ProductRepository,
        mock_transaction_repository: TransactionRepository,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_account_manager: AccountManager
    ):
    return ProductManager(mock_product_repository, mock_transaction_repository, mock_payment_method_repository, mock_account_manager)

@pytest.fixture
def mock_product_repository():
    return MagicMock(spec=ProductRepository)

@pytest.fixture
def mock_transaction_repository():
    return MagicMock(spec=TransactionRepository)

@pytest.fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)

@pytest.fixture
def mock_account_manager():
    return MagicMock(spec=AccountManager)
