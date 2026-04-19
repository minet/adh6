from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.entity import Member
from adh6.member.http.profile import ProfileHandler
from adh6.member.member_manager import MemberManager


@pytest.fixture
def mock_member_manager():
    return MagicMock(spec=MemberManager)


@pytest.fixture
def profile_handler(mock_member_manager):
    return ProfileHandler(member_manager=mock_member_manager)


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    mock_db_module = MagicMock()
    mock_db_module.session.dirty = False
    mock_db_module.session.new = False
    mock_db_module.session.deleted = False
    monkeypatch.setattr("adh6.storage.db", mock_db_module)
    return mock_db_module


class TestProfile:
    async def test_happy_path(self, profile_handler, mock_member_manager, monkeypatch):
        member = MagicMock(spec=Member)
        member.id = 1
        member.to_dict.return_value = {"id": 1, "username": "testuser"}
        roles = ["user"]

        mock_member_manager.get_profile = AsyncMock(return_value=(member, roles))

        # Mock get_user from adh6.context
        monkeypatch.setattr("adh6.member.http.profile.get_user", lambda: 1)

        result, status_code = await profile_handler.profile()

        assert status_code == 200
        assert result["member"] == {"id": 1, "username": "testuser"}
        assert result["roles"] == ["user"]

    async def test_unauthorized(self, profile_handler, mock_member_manager, monkeypatch):
        member = MagicMock(spec=Member)
        member.id = 1
        roles = ["user"]

        mock_member_manager.get_profile = AsyncMock(return_value=(member, roles))

        # Mock get_user to a different ID
        monkeypatch.setattr("adh6.member.http.profile.get_user", lambda: 2)

        # UnauthorizedError should be caught by with_context and handled by handle_error
        result, status_code = await profile_handler.profile()
        assert status_code == 403
