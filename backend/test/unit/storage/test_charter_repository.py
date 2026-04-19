from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.member.storage.charter_repository import CharterSQLRepository


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def charter_repo(mock_session):
    return CharterSQLRepository(session=mock_session)


class TestCharterSQLRepository:
    async def test_get_minet(self, charter_repo, mock_session):
        # Given
        dt = datetime.now()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = dt
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await charter_repo.get(1, 123)

        # Then
        assert result == dt
        mock_session.execute.assert_called_once()

    async def test_get_hosting(self, charter_repo, mock_session):
        # Given
        dt = datetime.now()
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = dt
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await charter_repo.get(2, 123)

        # Then
        assert result == dt

    async def test_get_members(self, charter_repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [1, 2, 3]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        members, count = await charter_repo.get_members(1)

        # Then
        assert count == 3
        assert members == [1, 2, 3]

    async def test_update(self, charter_repo, mock_session):
        # Given
        mock_session.execute = AsyncMock()

        # When
        await charter_repo.update(1, 123)

        # Then
        mock_session.execute.assert_called_once()
