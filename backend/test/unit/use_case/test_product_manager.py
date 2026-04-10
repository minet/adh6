from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import Account, PaymentMethod, Product
from adh6.exceptions import AccountNotFoundError, NotFoundError, PaymentMethodNotFoundError, ProductNotFoundError
from adh6.treasury.interfaces.account_repository import AccountRepository
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.treasury.interfaces.product_repository import ProductRepository
from adh6.treasury.product_manager import ProductManager
from adh6.treasury.transaction_manager import TransactionManager


class TestBuy:
    async def test_happy_path(
        self,
        sample_account1: Account,
        sample_account2: Account,
        sample_product: Product,
        sample_payment_method: PaymentMethod,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_account_repository: AccountRepository,
        mock_product_repository: ProductRepository,
        mock_transaction_manager: TransactionManager,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=(sample_payment_method))
        mock_account_repository.search_by = AsyncMock(side_effect=[([sample_account1], 1), ([sample_account2], 1)])
        mock_product_repository.get_by_id = AsyncMock(return_value=(sample_product))
        mock_transaction_manager.update_or_create = AsyncMock()

        await product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_repository.search_by.assert_called()
        mock_product_repository.get_by_id.assert_called_once_with(1)
        mock_transaction_manager.update_or_create.assert_called_once()

    async def test_no_products(self, product_manager):
        with pytest.raises(NotFoundError):
            await product_manager.buy(0, 0, [])

    async def test_payment_method_not_found(
        self, mock_payment_method_repository: PaymentMethodRepository, product_manager: ProductManager
    ):
        mock_payment_method_repository.get_by_id = MagicMock(
            return_value=(None), side_effect=PaymentMethodNotFoundError("0")
        )

        with pytest.raises(PaymentMethodNotFoundError):
            await product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)

    async def test_dst_technical_account_not_found(
        self,
        sample_payment_method,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_account_repository: AccountRepository,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=(sample_payment_method))
        mock_account_repository.search_by = AsyncMock(return_value=([], 0))

        with pytest.raises(AccountNotFoundError):
            await product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_repository.search_by.assert_called_once()

    async def test_src_account_not_found(
        self,
        sample_account1,
        sample_payment_method,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_account_repository: AccountRepository,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=(sample_payment_method))
        mock_account_repository.search_by = AsyncMock(side_effect=[([sample_account1], 1), ([], 0)])

        with pytest.raises(AccountNotFoundError):
            await product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_repository.search_by.assert_called()

    async def test_product_not_found(
        self,
        sample_account1: Account,
        sample_account2: Account,
        sample_payment_method: PaymentMethod,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_account_repository: AccountRepository,
        mock_product_repository: ProductRepository,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=(sample_payment_method))
        mock_account_repository.search_by = AsyncMock(side_effect=[([sample_account1], 1), ([sample_account2], 1)])
        mock_product_repository.get_by_id = AsyncMock(return_value=(None), side_effect=ProductNotFoundError(""))

        with pytest.raises(ProductNotFoundError):
            await product_manager.buy(0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_account_repository.search_by.assert_called()
        mock_product_repository.get_by_id.assert_called_once_with(1)


@pytest.fixture
def product_manager(
    mock_product_repository: ProductRepository,
    mock_transaction_manager: TransactionManager,
    mock_payment_method_repository: PaymentMethodRepository,
    mock_account_repository: AccountRepository,
):
    return ProductManager(
        mock_product_repository, mock_transaction_manager, mock_payment_method_repository, mock_account_repository
    )


@pytest.fixture
def mock_product_repository():
    return MagicMock(spec=ProductRepository)


@pytest.fixture
def mock_transaction_manager():
    return MagicMock(spec=TransactionManager)


@pytest.fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)


@pytest.fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)
