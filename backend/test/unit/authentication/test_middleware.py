from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adh6.authentication.enums import Roles
from adh6.authentication.middleware import _validate_api_key, get_token_info
from adh6.authentication.storage.models import ApiKey as ApiKeyModel
from fastapi import HTTPException, Request, status


@pytest.fixture
def mock_session():
    return MagicMock()


class TestGetTokenInfo:
    async def test_bearer_token_testing(self, mock_session, monkeypatch):
        # Given
        monkeypatch.setenv("TESTING", "1")
        request = MagicMock(spec=Request)
        request.headers = {"Authorization": "Bearer TEST_TOKEN"}

        # When
        result = await get_token_info(request, mock_session)

        # Then
        assert result["uid"] == 28
        assert Roles.USER.value in result["scope"]

    async def test_api_key_invalid(self, mock_session):
        # Given
        request = MagicMock(spec=Request)
        request.headers = {"X-API-KEY": "wrong-key"}
        mock_session.scalar = AsyncMock(return_value=None)

        # When / Then
        with pytest.raises(HTTPException) as excinfo:
            await get_token_info(request, mock_session)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_missing_credentials(self, mock_session):
        # Given
        request = MagicMock(spec=Request)
        request.headers = {}

        # When / Then
        with pytest.raises(HTTPException) as excinfo:
            await get_token_info(request, mock_session)
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestValidateApiKey:
    async def test_valid_api_key(self, mock_session):
        # Given
        key = "valid-key"
        api_key_obj = MagicMock(spec=ApiKeyModel)
        api_key_obj.id = 1
        mock_session.scalar = AsyncMock(return_value=api_key_obj)

        # Mock RoleRepository.find
        with patch("adh6.authentication.middleware.RoleRepository") as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_role = MagicMock()
            mock_role.role = "admin:read"
            mock_repo.find = AsyncMock(return_value=([mock_role], 1))

            # When
            result = await _validate_api_key(key, mock_session)

            # Then
            assert "admin:read" in result["scope"]
            assert result["auth_method"] == "api_key"
