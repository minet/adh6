from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import PaymentMethod, Product
from adh6.exceptions import NotFoundError, PaymentMethodNotFoundError, ProductNotFoundError
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.treasury.interfaces.product_repository import ProductRepository
from adh6.treasury.product_manager import ProductManager
from adh6.treasury.transaction_manager import TransactionManager


class TestBuy:
    async def test_happy_path(
        self,
        sample_product: Product,
        sample_payment_method: PaymentMethod,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_product_repository: ProductRepository,
        mock_transaction_manager: TransactionManager,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=(sample_payment_method))
        mock_product_repository.get_by_id = AsyncMock(return_value=(sample_product))
        mock_transaction_manager.update_or_create = AsyncMock()

        await product_manager.buy(0, 0, author_id=42, product_ids=[1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_product_repository.get_by_id.assert_called_once_with(1)
        mock_transaction_manager.update_or_create.assert_called_once()

    async def test_author_id_propagated_to_transaction(
        self,
        sample_product: Product,
        sample_payment_method: PaymentMethod,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_product_repository: ProductRepository,
        mock_transaction_manager: TransactionManager,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=sample_payment_method)
        mock_product_repository.get_by_id = AsyncMock(return_value=sample_product)
        mock_transaction_manager.update_or_create = AsyncMock()

        await product_manager.buy(0, 0, author_id=99, product_ids=[1])

        call_args = mock_transaction_manager.update_or_create.call_args
        abstract_transaction = call_args[0][0]
        assert abstract_transaction.author == 99, "author must not be None — transaction INSERT will fail"

    async def test_no_products(self, product_manager):
        with pytest.raises(NotFoundError):
            await product_manager.buy(0, 0, author_id=42, product_ids=[])

    async def test_payment_method_not_found(
        self, mock_payment_method_repository: PaymentMethodRepository, product_manager: ProductManager
    ):
        mock_payment_method_repository.get_by_id = MagicMock(
            return_value=(None), side_effect=PaymentMethodNotFoundError("0")
        )

        with pytest.raises(PaymentMethodNotFoundError):
            await product_manager.buy(0, 0, author_id=42, product_ids=[1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)

    async def test_product_not_found(
        self,
        sample_payment_method: PaymentMethod,
        mock_payment_method_repository: PaymentMethodRepository,
        mock_product_repository: ProductRepository,
        product_manager: ProductManager,
    ):
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=(sample_payment_method))
        mock_product_repository.get_by_id = AsyncMock(return_value=(None), side_effect=ProductNotFoundError(""))

        with pytest.raises(ProductNotFoundError):
            await product_manager.buy(0, 0, author_id=42, product_ids=[1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(0)
        mock_product_repository.get_by_id.assert_called_once_with(1)


@pytest.fixture
def product_manager(
    mock_product_repository: ProductRepository,
    mock_transaction_manager: TransactionManager,
    mock_payment_method_repository: PaymentMethodRepository,
):
    return ProductManager(mock_product_repository, mock_transaction_manager, mock_payment_method_repository)


@pytest.fixture
def mock_product_repository():
    return MagicMock(spec=ProductRepository)


@pytest.fixture
def mock_transaction_manager():
    return MagicMock(spec=TransactionManager)


@pytest.fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)
