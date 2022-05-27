from unittest.mock import MagicMock

import pytest
from src.exceptions import NotFoundError

from src.use_case.interface.payment_method_repository import PaymentMethodRepository
from src.use_case.interface.product_repository import ProductRepository
from src.use_case.interface.transaction_repository import TransactionRepository
from src.use_case.product_manager import ProductManager


class TestBuy:
    def test_no_products(self, ctx, product_manager):
        with pytest.raises(NotFoundError):
            product_manager.buy(ctx, 0, 0, [])

    def test_payment_method_uknown(self, ctx, mock_payment_method_repository: PaymentMethodRepository, product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(None), side_effect=NotFoundError("0"))

        with pytest.raises(NotFoundError):
            product_manager.buy(ctx, 0, 0, [1])

        mock_payment_method_repository.get_by_id.assert_called_once_with(ctx, 0)

    # @TODO: product transaction handling should be done in the manager rather than in the repository
    """ 
    def test_add_transaction_for_unknown_product(self, ctx, sample_payment_method, mock_transaction_repository: TransactionRepository, mock_payment_method_repository: PaymentMethodRepository, product_manager: ProductManager):
        mock_payment_method_repository.get_by_id = MagicMock(return_value=(sample_payment_method))
        mock_transaction_repository.add_products_payment_record = MagicMock(return_value=(None), side_effect=NotFoundError(""))
        mock_payment_method_repository.get_by_id.assert_called_once_with(ctx, 0)
        mock_transaction_repository.add_products_payment_record.assert_called_once_with(ctx, 0, )

        with pytest.raises(NotFoundError):
            product_manager.buy(ctx, 0, 0, [1])
    """


@pytest.fixture
def product_manager(
        mock_product_repository: ProductRepository,
        mock_transaction_repository: TransactionRepository,
        mock_payment_method_repository: PaymentMethodRepository
    ):
    return ProductManager(mock_product_repository, mock_transaction_repository, mock_payment_method_repository)

@pytest.fixture
def mock_product_repository():
    return MagicMock(spec=ProductRepository)

@pytest.fixture
def mock_transaction_repository():
    return MagicMock(spec=TransactionRepository)

@pytest.fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)
