from unittest.mock import MagicMock

from pytest import fixture, raises

from src.entity.product import Product
from src.exceptions import ProductNotFoundError, IntMustBePositive
from src.use_case.interface.product_repository import ProductRepository
from src.use_case.product_manager import ProductManager

TEST_PRODUCT_ID = 1200
TEST_PRODUCT_NAME = "loutre"


class TestGetByID:
    def test_happy_path(self,
                        ctx,
                        mock_product_repository: ProductRepository,
                        sample_product: Product,
                        product_manager: ProductManager):
        mock_product_repository.search_product_by = MagicMock(return_value=([sample_product], 1))
        result = product_manager.get_by_id(ctx, product_id=TEST_PRODUCT_ID)

        assert sample_product == result
        mock_product_repository.search_product_by.assert_called_once()

    def test_product_not_found(self,
                               ctx,
                               mock_product_repository: ProductRepository,
                               product_manager: ProductManager):
        mock_product_repository.search_product_by = MagicMock(return_value=([], 0))

        with raises(ProductNotFoundError):
            product_manager.get_by_id(ctx, product_id=TEST_PRODUCT_ID)


class TestSearch:
    def test_happy_path(self,
                        ctx,
                        mock_product_repository: ProductRepository,
                        sample_product: Product,
                        product_manager: ProductManager):
        mock_product_repository.search_product_by = MagicMock(return_value=([sample_product], 1))
        result, count = product_manager.search(ctx, limit=42, offset=2, product_id=None, terms='abc')

        assert [sample_product] == result
        assert 1 == count
        mock_product_repository.search_product_by.assert_called_once_with(ctx, limit=42, offset=2, product_id=None,
                                                                          terms='abc')

    def test_offset_negative(self,
                             ctx,
                             product_manager: ProductManager):
        with raises(IntMustBePositive):
            product_manager.search(ctx, limit=42, offset=-1, product_id=None, terms=None)

    def test_limit_negative(self,
                            ctx,
                            product_manager: ProductManager):
        with raises(IntMustBePositive):
            product_manager.search(ctx, limit=-1, offset=2, product_id=None, terms=None)


@fixture
def product_manager(mock_product_repository):
    return ProductManager(
        product_repository=mock_product_repository
    )


@fixture
def mock_product_repository():
    return MagicMock(spec=ProductRepository)


