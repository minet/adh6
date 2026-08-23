from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.constants import MembershipStatus
from adh6.entity import AbstractMembership, Member
from adh6.exceptions import MemberNotFoundError, ValidationError
from adh6.member.charter_manager import CharterManager
from adh6.member.interfaces import CharterRepository, MemberRepository, MembershipRepository


@pytest.fixture
def mock_charter_repo():
    return MagicMock(spec=CharterRepository)


@pytest.fixture
def mock_member_repo():
    return MagicMock(spec=MemberRepository)


@pytest.fixture
def mock_membership_repo():
    return MagicMock(spec=MembershipRepository)


@pytest.fixture
def charter_manager(mock_charter_repo, mock_member_repo, mock_membership_repo):
    return CharterManager(mock_charter_repo, mock_member_repo, mock_membership_repo)


class TestCharterManager:
    async def test_get_happy_path(self, charter_manager, mock_member_repo, mock_charter_repo):
        # Given
        dt = datetime.now()
        mock_member_repo.get_by_id = AsyncMock(return_value=MagicMock(spec=Member))
        mock_charter_repo.get = AsyncMock(return_value=dt)

        # When
        result = await charter_manager.get(1, 123)

        # Then
        assert result == dt

    async def test_get_invalid_charter_id(self, charter_manager):
        with pytest.raises(ValidationError):
            await charter_manager.get(3, 123)

    async def test_get_member_not_found(self, charter_manager, mock_member_repo):
        mock_member_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(MemberNotFoundError):
            await charter_manager.get(1, 123)

    async def test_sign_happy_path(self, charter_manager, mock_member_repo, mock_membership_repo, mock_charter_repo):
        # Given
        mock_member_repo.get_by_id = AsyncMock(return_value=MagicMock(spec=Member))
        sub = MagicMock(spec=AbstractMembership)
        sub.status = MembershipStatus.PENDING_RULES.value
        sub.uuid = "some-uuid"
        mock_membership_repo.search = AsyncMock(return_value=([sub], 1))

        # When
        await charter_manager.sign(1, 123)

        # Then
        mock_charter_repo.update.assert_called_once_with(1, 123)
        mock_membership_repo.update.assert_called_once()

    async def test_sign_without_a_pending_membership_still_records_the_signature(
        self, charter_manager, mock_member_repo, mock_membership_repo, mock_charter_repo
    ):
        """Signing a charter must not require a membership to be waiting for it.

        This used to raise MembershipNotFoundError, which created a chicken-and-egg on renewals:
        the previous membership is COMPLETE, so no PENDING_RULES row exists, so the member could
        never sign, so the renewal could never advance.
        """
        # Given
        mock_member_repo.get_by_id = AsyncMock(return_value=MagicMock(spec=Member))
        mock_membership_repo.search = AsyncMock(return_value=([], 0))

        # When
        await charter_manager.sign(1, 123)

        # Then
        mock_charter_repo.update.assert_called_once_with(1, 123)
        mock_membership_repo.update.assert_not_called()

    async def test_get_members(self, charter_manager, mock_charter_repo):
        mock_charter_repo.get_members = AsyncMock(return_value=([1, 2], 2))
        members, count = await charter_manager.get_members(1)
        assert members == [1, 2]
        assert count == 2
