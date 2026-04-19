from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.default.crud_manager import CRUDManager
from adh6.default.crud_repository import CRUDRepository


@pytest.fixture
def mock_repository():
    return MagicMock(spec=CRUDRepository)


@pytest.fixture
def crud_manager(mock_repository):
    return CRUDManager(repository=mock_repository, not_found_exception=Exception)


class TestDelete:
    async def test_happy_path(self, crud_manager, mock_repository):
        # Given
        mock_repository.get_by_id = AsyncMock(return_value={"id": 1})
        mock_repository.delete = AsyncMock()

        # When
        await crud_manager.delete(1)

        # Then
        mock_repository.get_by_id.assert_called_once_with(object_id=1)
        mock_repository.delete.assert_called_once_with(1)

    async def test_not_found(self, crud_manager, mock_repository):
        # Given
        mock_repository.get_by_id = AsyncMock(return_value=None)

        # When / Then
        with pytest.raises(Exception):
            await crud_manager.delete(999)
