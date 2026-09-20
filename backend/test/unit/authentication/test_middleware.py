from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adh6.authentication.enums import Roles
from adh6.authentication.middleware import _validate_api_key, _validate_token_with_keycloak, authenticate
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


def _request(headers: dict[str, str], path: str = "/api/member/", method: str = "GET") -> Request:
    raw_headers = [(name.lower().encode(), value.encode()) for name, value in headers.items()]
    return Request({"type": "http", "method": method, "path": path, "query_string": b"", "headers": raw_headers})


class TestAuthenticate:
    async def test_request_without_credentials_is_anonymous(self, mock_session):
        request = _request({})

        await authenticate(request, mock_session)

        assert not hasattr(request.state, "token_info")

    async def test_non_api_paths_are_ignored(self, mock_session, verifier):
        request = _request({"Authorization": "Bearer abc"}, path="/ping")

        await authenticate(request, mock_session)

        verifier.verify.assert_not_awaited()
        assert not hasattr(request.state, "token_info")

    async def test_bearer_token_is_resolved_with_the_request_session(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"adh6_id": 1}
        request = _request({"Authorization": "Bearer abc"})

        with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
            repo_class.return_value = role_repository
            await authenticate(request, mock_session)

        repo_class.assert_called_once_with(mock_session)
        assert request.state.token_info["uid"] == 1

    async def test_api_key_is_resolved_with_the_request_session(self, mock_session):
        request = _request({"X-API-KEY": "key"})
        token_info = {"uid": 2, "api_key_id": 7}

        with patch("adh6.authentication.middleware._validate_api_key", AsyncMock(return_value=token_info)) as validate:
            await authenticate(request, mock_session)

        validate.assert_awaited_once_with("key", mock_session)
        assert request.state.token_info == token_info

    async def test_session_cookie_is_resolved_like_a_bearer_token(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"adh6_id": 3}
        request = _request({"Cookie": "adh6_access=cookie-token"})

        with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
            repo_class.return_value = role_repository
            await authenticate(request, mock_session)

        verifier.verify.assert_awaited_once_with("cookie-token")
        assert request.state.token_info["uid"] == 3

    async def test_bearer_and_api_key_win_over_the_session_cookie(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"adh6_id": 1}
        request = _request({"Authorization": "Bearer abc", "Cookie": "adh6_access=cookie-token"})

        with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
            repo_class.return_value = role_repository
            await authenticate(request, mock_session)

        verifier.verify.assert_awaited_once_with("abc")

    async def test_a_change_made_with_the_cookie_alone_is_refused(self, mock_session, verifier):
        request = _request({"Cookie": "adh6_access=cookie-token"}, method="DELETE")

        with pytest.raises(HTTPException) as excinfo:
            await authenticate(request, mock_session)

        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
        verifier.verify.assert_not_awaited()

    @pytest.mark.parametrize(
        "extra",
        [{"Sec-Fetch-Site": "cross-site"}, {"Sec-Fetch-Site": "same-site"}, {"Origin": "https://evil.example"}],
    )
    async def test_a_change_from_another_site_is_refused_even_with_the_header(self, mock_session, verifier, extra):
        headers = {"Cookie": "adh6_access=t", "X-Requested-With": "XMLHttpRequest", "Host": "adh6.minet.net", **extra}

        with pytest.raises(HTTPException) as excinfo:
            await authenticate(_request(headers, method="POST"), mock_session)

        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "extra",
        [
            {},
            {"Sec-Fetch-Site": "same-origin"},
            {"Origin": "https://adh6.minet.net"},
            {"Origin": "https://adh6.minet.net:8443"},
        ],
    )
    async def test_a_change_made_by_the_app_is_accepted(self, mock_session, verifier, role_repository, extra):
        verifier.verify.return_value = {"adh6_id": 3}
        headers = {"Cookie": "adh6_access=t", "X-Requested-With": "XMLHttpRequest", "Host": "adh6.minet.net", **extra}

        with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
            repo_class.return_value = role_repository
            await authenticate(_request(headers, method="POST"), mock_session)

        assert verifier.verify.await_count == 1

    async def test_bearer_and_api_key_changes_need_no_csrf_header(self, mock_session, verifier, role_repository):
        verifier.verify.return_value = {"adh6_id": 1}
        with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
            repo_class.return_value = role_repository
            await authenticate(_request({"Authorization": "Bearer abc"}, method="POST"), mock_session)
        assert verifier.verify.await_count == 1

        with patch("adh6.authentication.middleware._validate_api_key", AsyncMock(return_value={"uid": 2})):
            await authenticate(_request({"X-API-KEY": "key"}, method="POST"), mock_session)

    async def test_login_routes_ignore_an_old_session_cookie(self, mock_session, verifier):
        request = _request({"Cookie": "adh6_access=expired"}, path="/api/auth/login")

        await authenticate(request, mock_session)

        verifier.verify.assert_not_awaited()

    async def test_rejected_credentials_propagate(self, mock_session, verifier):
        verifier.verify.side_effect = InvalidOIDCToken("bad")

        with pytest.raises(HTTPException) as excinfo:
            await authenticate(_request({"Authorization": "Bearer abc"}), mock_session)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unexpected_error_is_500_without_details(self, mock_session, verifier):
        verifier.verify.side_effect = RuntimeError("secret")

        with pytest.raises(HTTPException) as excinfo:
            await authenticate(_request({"Authorization": "Bearer abc"}), mock_session)

        assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "secret" not in str(excinfo.value.detail)


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
