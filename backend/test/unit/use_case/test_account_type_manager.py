from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.exceptions import AccountTypeNotFoundError
from adh6.treasury.account_type_manager import AccountTypeManager
from adh6.treasury.interfaces.account_type_repository import AccountTypeRepository


@pytest.fixture
def mock_account_type_repository():
    return MagicMock(spec=AccountTypeRepository)


@pytest.fixture
def account_type_manager(mock_account_type_repository):
    return AccountTypeManager(account_type_repository=mock_account_type_repository)


class TestCRUD:
    async def test_get_by_id(self, account_type_manager, mock_account_type_repository):
        # Given
        mock_account_type_repository.get_by_id = AsyncMock(return_value={"id": 1, "name": "Test"})

        # When
        result = await account_type_manager.get_by_id(1)

        # Then
        assert result == {"id": 1, "name": "Test"}
        mock_account_type_repository.get_by_id.assert_called_once_with(1)

    async def test_get_by_id_not_found(self, account_type_manager, mock_account_type_repository):
        # Given
        mock_account_type_repository.get_by_id = AsyncMock(return_value=None)

        # When / Then
        with pytest.raises(AccountTypeNotFoundError):
            await account_type_manager.get_by_id(999)

    async def test_delete(self, account_type_manager, mock_account_type_repository):
        # Given
        mock_account_type_repository.delete = AsyncMock(return_value=True)

        # When
        await account_type_manager.delete(1)

        # Then
        mock_account_type_repository.delete.assert_called_once_with(1)
