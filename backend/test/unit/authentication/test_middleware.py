from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adh6.authentication.enums import Roles
from adh6.authentication.middleware import _validate_api_key, _validate_token_with_keycloak, auth_middleware
from adh6.authentication.oidc.token_verifier import InvalidOIDCToken, OidcProviderUnavailable
from adh6.authentication.storage.models import ApiKey as ApiKeyModel
from adh6.exceptions import MemberNotFoundError
from fastapi import HTTPException, Request, status


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def verifier():
    with patch("adh6.authentication.middleware.get_oidc_token_verifier") as get_verifier:
        verifier = MagicMock()
        verifier.verify = AsyncMock()
        get_verifier.return_value = verifier
        yield verifier


@pytest.fixture
def role_repository():
    with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
        repo = AsyncMock()
        repo.find_for_oidc_identity.return_value = []
        repo_class.return_value = repo
        yield repo


class TestValidateTokenWithKeycloak:
    async def test_roles_come_from_groups_and_username(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"adh6_id": 123, "preferred_username": "testuser", "groups": ["/admin", "treso"]}
        role_repository.find_for_oidc_identity.return_value = [SimpleNamespace(role=Roles.ADMIN_READ.value)]

        result = await _validate_token_with_keycloak("token", mock_session)

        assert result["uid"] == 123
        assert result["username"] == "testuser"
        assert result["groups"] == ["admin", "treso"]
        assert result["scope"] == [Roles.USER.value, Roles.ADMIN_READ.value]
        role_repository.find_for_oidc_identity.assert_awaited_once_with(groups=["admin", "treso"], username="testuser")
        role_repository.user_id_from_username.assert_not_awaited()

    async def test_uid_is_resolved_from_username_without_adh6_id(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"preferred_username": "testuser"}
        role_repository.user_id_from_username.return_value = 456

        result = await _validate_token_with_keycloak("token", mock_session)

        assert result["uid"] == 456
        assert result["groups"] == []

    async def test_unknown_member_is_authenticated_without_uid(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"preferred_username": "newcomer"}
        role_repository.user_id_from_username.side_effect = MemberNotFoundError("newcomer")

        result = await _validate_token_with_keycloak("token", mock_session)

        assert result["uid"] is None

    async def test_database_errors_are_not_swallowed(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"preferred_username": "testuser"}
        role_repository.user_id_from_username.side_effect = ConnectionError("database down")

        with pytest.raises(ConnectionError):
            await _validate_token_with_keycloak("token", mock_session)

    async def test_malformed_groups_are_ignored(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"adh6_id": 1, "groups": "/admin"}

        result = await _validate_token_with_keycloak("token", mock_session)

        assert result["groups"] == []

    async def test_invalid_token_is_401_without_details(self, mock_session, verifier, role_repository):
        verifier.verify.side_effect = InvalidOIDCToken("signature mismatch for key xyz")

        with pytest.raises(HTTPException) as excinfo:
            await _validate_token_with_keycloak("token", mock_session)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Invalid OIDC token"

    async def test_unavailable_provider_is_503(self, mock_session, verifier, role_repository):
        verifier.verify.side_effect = OidcProviderUnavailable("timeout")

        with pytest.raises(HTTPException) as excinfo:
            await _validate_token_with_keycloak("token", mock_session)

        assert excinfo.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestAuthMiddleware:
    @staticmethod
    def _request(headers: dict[str, str], path: str = "/api/member/") -> Request:
        raw_headers = [(name.lower().encode(), value.encode()) for name, value in headers.items()]
        return Request({"type": "http", "method": "GET", "path": path, "query_string": b"", "headers": raw_headers})

    async def test_request_without_credentials_passes_through(self):
        request = self._request({})
        call_next = AsyncMock(return_value="response")

        assert await auth_middleware(request, call_next) == "response"
        assert not hasattr(request.state, "token_info")

    async def test_unexpected_error_is_500_without_details(self):
        request = self._request({"Authorization": "Bearer token"})
        call_next = AsyncMock()

        with patch("adh6.authentication.middleware.async_session_factory", side_effect=RuntimeError("secret")):
            response = await auth_middleware(request, call_next)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert b"secret" not in response.body
        call_next.assert_not_awaited()


class TestValidateApiKey:
    async def test_invalid_api_key(self, mock_session):
        mock_session.scalar = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as excinfo:
            await _validate_api_key("wrong-key", mock_session)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_valid_api_key(self, mock_session):
        api_key_obj = MagicMock(spec=ApiKeyModel)
        api_key_obj.id = 1
        api_key_obj.user_login = "testuser"
        mock_session.scalar = AsyncMock(return_value=api_key_obj)

        with patch("adh6.authentication.middleware.RoleRepository") as mock_repo_class:
            mock_repo = mock_repo_class.return_value
            mock_repo.find = AsyncMock(return_value=([SimpleNamespace(role="admin:read")], 1))
            mock_repo.user_id_from_username = AsyncMock(side_effect=MemberNotFoundError("testuser"))

            result = await _validate_api_key("valid-key", mock_session)

        assert "admin:read" in result["scope"]
        assert result["auth_method"] == "api_key"
        assert result["uid"] is None
