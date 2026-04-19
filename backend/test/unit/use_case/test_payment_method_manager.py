from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.exceptions import PaymentMethodNotFoundError
from adh6.treasury.interfaces.payment_method_repository import PaymentMethodRepository
from adh6.treasury.payment_method_manager import PaymentMethodManager


@pytest.fixture
def mock_payment_method_repository():
    return MagicMock(spec=PaymentMethodRepository)


@pytest.fixture
def payment_method_manager(mock_payment_method_repository):
    return PaymentMethodManager(payment_method_repository=mock_payment_method_repository)


class TestCRUD:
    async def test_get_by_id(self, payment_method_manager, mock_payment_method_repository):
        # Given
        mock_payment_method_repository.get_by_id = AsyncMock(return_value={"id": 1, "name": "Cash"})

        # When
        result = await payment_method_manager.get_by_id(1)

        # Then
        assert result == {"id": 1, "name": "Cash"}
        mock_payment_method_repository.get_by_id.assert_called_once_with(1)

    async def test_get_by_id_not_found(self, payment_method_manager, mock_payment_method_repository):
        # Given
        mock_payment_method_repository.get_by_id = AsyncMock(return_value=None)

        # When / Then
        with pytest.raises(PaymentMethodNotFoundError):
            await payment_method_manager.get_by_id(999)
