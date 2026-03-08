"""Tests for OIDC token information extraction in FastAPI middleware."""

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from jwcrypto.jwt import JWTExpired, JWTInvalidClaimFormat, JWTMissingClaim

from adh6.authentication.enums import Roles
from adh6.authentication.middleware import _validate_token_with_keycloak


@pytest.fixture
def mock_session():
    """Create a fake async DB session."""
    return MagicMock()


@pytest.fixture
def anyio_backend():
    """Run anyio tests only on asyncio, matching the app runtime."""
    return "asyncio"


@pytest.fixture
def mock_keycloak_client():
    """Mock keycloak client used by middleware."""
    with patch("adh6.authentication.middleware._get_keycloak_client") as mocked:
        client = MagicMock()
        mocked.return_value = client
        yield client


@pytest.fixture
def mock_role_repository():
    """Mock async role repository used during token processing."""
    with patch("adh6.authentication.middleware.RoleRepository") as repo_class:
        repo = AsyncMock()
        repo_class.return_value = repo
        yield repo


@pytest.fixture
def valid_token_data():
    """Sample valid token data with adh6_id."""
    return {
        "adh6_id": 123,
        "preferred_username": "testuser",
        "groups": ["/admin", "/network_admin", "/treso"],
        "sub": "user-uuid-123",
        "iat": 1234567890,
        "exp": 9999999999,
    }


@pytest.fixture
def valid_token_data_no_adh6_id():
    """Sample valid token data without adh6_id."""
    return {
        "preferred_username": "testuser",
        "groups": ["/admin", "/network_admin"],
        "sub": "user-uuid-123",
        "iat": 1234567890,
        "exp": 9999999999,
    }


@pytest.mark.anyio
async def test_valid_token_with_adh6_id(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
    valid_token_data,
):
    """A valid token returns expected uid, groups and scope."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = valid_token_data

    oidc_roles = [SimpleNamespace(role=Roles.ADMIN_READ)]
    user_roles = [SimpleNamespace(role=Roles.USER)]
    mock_role_repository.find.side_effect = [
        (oidc_roles, len(oidc_roles)),
        (user_roles, len(user_roles)),
    ]

    result = await _validate_token_with_keycloak("valid_token_123", mock_session)

    assert result is not None
    assert result["uid"] == 123
    assert result["username"] == "testuser"
    assert result["groups"] == ["admin", "network_admin", "treso"]
    assert Roles.USER.value in result["scope"]
    assert Roles.ADMIN_READ in result["scope"]
    assert Roles.USER in result["scope"]

    mock_keycloak_client.decode_token.assert_called_once_with("valid_token_123")
    assert mock_role_repository.find.call_count == 2


@pytest.mark.anyio
async def test_valid_token_without_adh6_id(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
    valid_token_data_no_adh6_id,
):
    """When adh6_id is missing, user_id is resolved from username."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = valid_token_data_no_adh6_id

    mock_role_repository.user_id_from_username.return_value = 456
    oidc_roles = [SimpleNamespace(role=Roles.ADMIN_WRITE)]
    user_roles = [SimpleNamespace(role=Roles.USER)]
    mock_role_repository.find.side_effect = [
        (oidc_roles, len(oidc_roles)),
        (user_roles, len(user_roles)),
    ]

    result = await _validate_token_with_keycloak("valid_token_456", mock_session)

    assert result is not None
    assert result["uid"] == 456
    assert result["username"] == "testuser"
    assert result["groups"] == ["admin", "network_admin"]
    assert Roles.USER.value in result["scope"]
    assert Roles.ADMIN_WRITE in result["scope"]

    mock_role_repository.user_id_from_username.assert_awaited_once_with(
        login="testuser"
    )


@pytest.mark.anyio
async def test_invalid_token_claim_format_raises_unauthorized(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Malformed tokens should raise HTTP 401."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.side_effect = JWTInvalidClaimFormat(
        "Invalid token format"
    )

    with pytest.raises(HTTPException) as exc_info:
        await _validate_token_with_keycloak(cast(Any, 123), mock_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid OIDC token" in exc_info.value.detail
    assert "InvalidClaimFormat" in exc_info.value.detail


@pytest.mark.anyio
async def test_expired_token_raises_unauthorized(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Expired tokens should raise HTTP 401."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.side_effect = JWTExpired("Token has expired")

    with pytest.raises(HTTPException) as exc_info:
        await _validate_token_with_keycloak("expired_token_123", mock_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid OIDC token" in exc_info.value.detail
    assert "Expired" in exc_info.value.detail


@pytest.mark.anyio
async def test_missing_claim_raises_unauthorized(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Tokens missing claims should raise HTTP 401."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.side_effect = JWTMissingClaim(
        "Missing required claim"
    )

    with pytest.raises(HTTPException) as exc_info:
        await _validate_token_with_keycloak("incomplete_token_123", mock_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid OIDC token" in exc_info.value.detail
    assert "MissingClaim" in exc_info.value.detail


@pytest.mark.anyio
async def test_empty_token_data_raises_unauthorized(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Empty token payload should raise HTTP 401."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await _validate_token_with_keycloak("empty_token", mock_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid OIDC token: no data found"


@pytest.mark.anyio
async def test_malformed_token_data_raises_unauthorized(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Non-dict token payload should raise HTTP 401."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = "not_a_dict"

    with pytest.raises(HTTPException) as exc_info:
        await _validate_token_with_keycloak("malformed_token", mock_session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        exc_info.value.detail
        == "Invalid OIDC token: the data is not properly formatted"
    )


@pytest.mark.anyio
async def test_token_without_username_or_id(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Token without uid/username still returns parsed groups and default scope."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = {
        "groups": ["/admin"],
        "sub": "user-uuid-123",
    }

    oidc_roles = [SimpleNamespace(role=Roles.ADMIN_READ)]
    mock_role_repository.find.side_effect = [
        (oidc_roles, len(oidc_roles)),
    ]

    result = await _validate_token_with_keycloak(
        "token_without_user_info", mock_session
    )

    assert result is not None
    assert result["uid"] is None
    assert result["username"] is None
    assert result["groups"] == ["admin"]
    assert Roles.USER.value in result["scope"]
    assert Roles.ADMIN_READ in result["scope"]


@pytest.mark.anyio
async def test_groups_stripping_leading_slash(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Leading slashes are stripped and None values are ignored."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = {
        "adh6_id": 123,
        "preferred_username": "testuser",
        "groups": ["/admin", "//double_slash", "no_slash", None],
    }

    mock_role_repository.find.return_value = ([], 0)

    result = await _validate_token_with_keycloak(
        "token_with_various_groups", mock_session
    )

    assert result is not None
    assert result["groups"] == ["admin", "double_slash", "no_slash"]


@pytest.mark.anyio
async def test_no_groups_in_token(
    monkeypatch,
    mock_session,
    mock_keycloak_client,
    mock_role_repository,
):
    """Token without groups should keep an empty groups list."""
    monkeypatch.delenv("TESTING", raising=False)
    mock_keycloak_client.decode_token.return_value = {
        "adh6_id": 123,
        "preferred_username": "testuser",
    }

    user_roles = [SimpleNamespace(role=Roles.USER)]
    mock_role_repository.find.side_effect = [
        (user_roles, len(user_roles)),
    ]

    result = await _validate_token_with_keycloak("token_without_groups", mock_session)

    assert result is not None
    assert result["groups"] == []
    assert Roles.USER.value in result["scope"]
