"""Authentication middleware for FastAPI application."""

import os
from hashlib import sha3_512
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from jwcrypto.jwt import (
    JWTExpired,
    JWTInvalidClaimFormat,
    JWTInvalidClaimValue,
    JWTMissingClaim,
    JWTMissingKey,
    JWTNotYetValid,
)
from keycloak import KeycloakOpenID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage import RoleRepository
from adh6.authentication.storage.models import ApiKey as ApiKeyModel
from adh6.context import set_user
from adh6.database import get_session

JWTInvalid = (
    JWTExpired,
    JWTInvalidClaimFormat,
    JWTInvalidClaimValue,
    JWTMissingClaim,
    JWTMissingKey,
    JWTNotYetValid,
)

# Global Keycloak client instance
_keycloak_client: KeycloakOpenID | None = None


def _get_keycloak_client() -> KeycloakOpenID:
    """Get or initialize the Keycloak OpenID client."""
    global _keycloak_client
    if _keycloak_client is None:
        required_env_vars = [
            "KEYCLOAK_URL",
            "KEYCLOAK_REALM",
            "KEYCLOAK_CLIENT_ID",
            "KEYCLOAK_CLIENT_SECRET",
        ]
        missing_vars = [var for var in required_env_vars if var not in os.environ]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        _keycloak_client = KeycloakOpenID(
            server_url=os.environ["KEYCLOAK_URL"],
            client_id=os.environ["KEYCLOAK_CLIENT_ID"],
            realm_name=os.environ["KEYCLOAK_REALM"],
            client_secret_key=os.environ["KEYCLOAK_CLIENT_SECRET"],
        )
    return _keycloak_client


async def _validate_token_with_keycloak(token: str, session: AsyncSession) -> dict[str, Any]:
    """
    Validate token with Keycloak and extract user information.

    Returns a dict with: uid, scope, groups, username
    Raises HTTPException on validation errors.
    """
    if os.environ.get("TESTING") == "1":
        if token == "TEST_TOKEN":  # noqa: S105
            return {
                "uid": 28,
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
        if token == "TEST_TOKEN_SAMPLE":  # noqa: S105
            return {
                "uid": 31,
                "scope": [Roles.USER.value],
                "groups": [],
                "username": "SampleMember",
            }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid test token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    keycloak = _get_keycloak_client()
    role_repository = RoleRepository(session)

    # Decode and validate the token
    try:
        token_data = keycloak.decode_token(token)
    except JWTInvalid as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid OIDC token ({type(e).__name__.replace('JWT', '')}): {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OIDC token: no data found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not isinstance(token_data, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OIDC token: the data is not properly formatted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    uid = token_data.get("adh6_id")
    if not uid:
        username = token_data.get("preferred_username")
        if username:
            try:
                uid = await role_repository.user_id_from_username(login=username)
            except Exception:
                # User might not exist in database yet
                uid = None

    # Groups returned by keycloak start with /
    groups = [group.lstrip("/") for group in token_data.get("groups", []) if group is not None]

    # Find roles based on groups (OIDC method) and username (USER method)
    roles = []
    if groups:
        result, _ = await role_repository.find(
            method=AuthenticationMethod.OIDC,
            identifiers=groups,
        )
        roles.extend([i.role for i in result])

    if token_data.get("preferred_username"):
        username = token_data.get("preferred_username")
        if username:
            result, _ = await role_repository.find(
                method=AuthenticationMethod.USER,
                identifiers=[username],
            )
            roles.extend([i.role for i in result])

    scope = [Roles.USER.value, *roles]

    return {
        "uid": uid,
        "scope": scope,
        "groups": groups,
        "username": token_data.get("preferred_username"),
        "auth_method": "oidc",
    }


async def get_token_from_request(request: Request) -> str:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_header[7:]  # Remove "Bearer " prefix


async def get_token_info(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    """Get token info from Bearer token or API key headers."""
    auth_header = request.headers.get("Authorization", "")
    api_key_header = request.headers.get("X-API-KEY", "")

    try:
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            token_info = await _validate_token_with_keycloak(token, session)
        elif api_key_header:
            token_info = await _validate_api_key(api_key_header, session)
        else:
            raise HTTPException(  # noqa: TRY301 # This is expected in a token validation function
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_info:
            return token_info

        raise HTTPException(  # noqa: TRY301 # This is expected in a token validation function
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _validate_api_key(key: str, session: AsyncSession) -> dict[str, Any]:
    hashed = sha3_512(key.encode("utf-8")).hexdigest()
    api_key = await session.scalar(select(ApiKeyModel).where(ApiKeyModel.value == hashed))
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    role_repository = RoleRepository(session)
    role_mappings, _count = await role_repository.find(
        method=AuthenticationMethod.API_KEY,
        identifiers=[str(api_key.id)],
    )
    roles = [mapping.role for mapping in role_mappings]

    uid: int | None = None
    try:
        uid = await role_repository.user_id_from_username(api_key.user_login)
    except Exception:
        uid = None

    return {
        "uid": uid,
        "scope": [Roles.USER.value, *roles],
        "groups": [],
        "username": api_key.user_login,
        "auth_method": "api_key",
    }


async def auth_middleware(request: Request, call_next):
    """Middleware to extract and validate authentication token."""
    # Try to extract and validate token for protected endpoints
    if request.url.path.startswith("/api"):
        auth_header = request.headers.get("Authorization", "")
        api_key_header = request.headers.get("X-API-KEY", "")

        if auth_header.startswith("Bearer ") or api_key_header:
            try:
                async for session in get_session():
                    if auth_header.startswith("Bearer "):
                        token_info = await _validate_token_with_keycloak(auth_header[7:], session)
                    else:
                        token_info = await _validate_api_key(api_key_header, session)

                    if token_info:
                        request.state.token_info = token_info
                        set_user(token_info.get("uid"))
                    break
            except HTTPException as exc:
                response_kwargs: dict[str, Any] = {
                    "status_code": exc.status_code,
                    "content": {"detail": exc.detail},
                }
                if exc.headers:
                    response_kwargs["headers"] = exc.headers
                return JSONResponse(**response_kwargs)
            except Exception:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication failed"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

    response = await call_next(request)
    return response
