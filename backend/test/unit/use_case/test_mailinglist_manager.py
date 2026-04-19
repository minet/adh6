from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import Member
from adh6.exceptions import ValidationError
from adh6.member.interfaces import MailinglistRepository, MemberRepository
from adh6.member.mailinglist_manager import MailinglistManager


@pytest.fixture
def mock_mailinglist_repo():
    return MagicMock(spec=MailinglistRepository)


@pytest.fixture
def mock_member_repo():
    return MagicMock(spec=MemberRepository)


@pytest.fixture
def mailinglist_manager(mock_mailinglist_repo, mock_member_repo):
    return MailinglistManager(mock_member_repo, mock_mailinglist_repo)


class TestMailinglistManager:
    async def test_get_member_mailinglist_happy_path(
        self, mailinglist_manager, mock_member_repo, mock_mailinglist_repo
    ):
        # Given
        mock_member_repo.get_by_id = AsyncMock(return_value=MagicMock(spec=Member))
        mock_mailinglist_repo.get_from_member = AsyncMock(return_value=1)

        # When
        result = await mailinglist_manager.get_member_mailinglist(123)

        # Then
        assert result == 1

    async def test_update_member_mailinglist_happy_path(
        self, mailinglist_manager, mock_member_repo, mock_mailinglist_repo
    ):
        # Given
        mock_member_repo.get_by_id = AsyncMock(return_value=MagicMock(spec=Member))

        # When
        await mailinglist_manager.update_member_mailinglist(123, 100)

        # Then
        mock_mailinglist_repo.update_from_member.assert_called_once_with(123, 100)

    async def test_update_member_mailinglist_invalid_value(self, mailinglist_manager):
        with pytest.raises(ValidationError):
            await mailinglist_manager.update_member_mailinglist(123, 300)

    async def test_get_members(self, mailinglist_manager, mock_mailinglist_repo):
        # Given
        mock_mailinglist_repo.list_members = AsyncMock(return_value=[1, 2, 3])

        # When
        result = await mailinglist_manager.get_members(10)

        # Then
        assert result == [1, 2, 3]
