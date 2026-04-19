from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.member.storage.mailinglist_repository import MailinglistSQLReposiroty


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def mailinglist_repo(mock_session):
    return MailinglistSQLReposiroty(session=mock_session)


class TestMailinglistSQLRepository:
    async def test_get_from_member(self, mailinglist_repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await mailinglist_repo.get_from_member(123)

        # Then
        assert result == 1
        mock_session.execute.assert_called_once()

    async def test_update_from_member(self, mailinglist_repo, mock_session):
        # Given
        mock_session.execute = AsyncMock()

        # When
        await mailinglist_repo.update_from_member(123, 2)

        # Then
        mock_session.execute.assert_called_once()

    async def test_list_members(self, mailinglist_repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [1, 2]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await mailinglist_repo.list_members(1)

        # Then
        assert result == [1, 2]
        mock_session.execute.assert_called_once()
