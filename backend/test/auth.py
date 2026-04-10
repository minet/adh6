from typing import Any

from adh6.authentication.enums import Roles
from fastapi import HTTPException, status


def oidc_info(token, required_scopes=None) -> dict[str, Any]:
    """Mock OIDC info for testing environment."""

    # Token-based mock logic matching test tokens
    if token == "TEST_TOKEN":  # TESTING_CLIENT_TOKEN - admin user
        mock_data = {
            "uid": 28,  # TESTING_CLIENT_ID
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
            "username": "TestingClient",
        }
    elif token == "TEST_TOKEN_SAMPLE":  # SAMPLE_CLIENT_TOKEN - regular user
        mock_data = {
            "uid": 31,  # SAMPLE_CLIENT_ID
            "scope": [Roles.USER.value],  # Only basic user permissions
            "groups": [],
            "username": "SampleMember",
        }
    else:
        # For unknown tokens, deny access by default
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unknown test token: {token}")

    # Check required scopes if provided
    if required_scopes:
        if not isinstance(required_scopes, list):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid OIDC token: required scopes must be a list"
            )
        if not all(req in mock_data["scope"] for req in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid OIDC token: missing required scopes {required_scopes}",
            )

    return mock_data
