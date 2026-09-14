from typing import Any

from adh6.authentication.enums import Roles
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from test import (
    SAMPLE_CLIENT,
    SAMPLE_CLIENT_ID,
    SAMPLE_CLIENT_TOKEN,
    TESTING_CLIENT,
    TESTING_CLIENT_ID,
    TESTING_CLIENT_TOKEN,
)

_TEST_TOKENS: dict[str, dict[str, Any]] = {
    TESTING_CLIENT_TOKEN: {
        "uid": TESTING_CLIENT_ID,
        "scope": [
            Roles.USER.value,
            Roles.ADMIN_READ.value,
            Roles.ADMIN_WRITE.value,
            Roles.ADMIN_PROD.value,
            Roles.NETWORK_WRITE.value,
            Roles.NETWORK_READ.value,
            Roles.TRESO_READ.value,
            Roles.TRESO_WRITE.value,
        ],
        "groups": ["admin", "network_admin", "treso"],
        "username": TESTING_CLIENT,
        "auth_method": "oidc",
    },
    SAMPLE_CLIENT_TOKEN: {
        "uid": SAMPLE_CLIENT_ID,
        "scope": [Roles.USER.value],
        "groups": [],
        "username": SAMPLE_CLIENT,
        "auth_method": "oidc",
    },
}


async def validate_test_token(token: str, session: AsyncSession) -> dict[str, Any]:
    """Stand-in for the Keycloak token validation, installed by test.integration.context."""
    if token not in _TEST_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid test token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return dict(_TEST_TOKENS[token])
