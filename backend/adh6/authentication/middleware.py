"""Authentication dependency: resolves the caller of every /api request."""

import logging
from hashlib import sha3_512
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.oidc.token_verifier import (
    InvalidOIDCToken,
    OidcProviderUnavailable,
    get_oidc_token_verifier,
)
from adh6.authentication.storage import RoleRepository
from adh6.authentication.storage.models import ApiKey as ApiKeyModel
from adh6.context import set_api_key_id, set_user
from adh6.database import get_session
from adh6.exceptions import MemberNotFoundError

_log = logging.getLogger(__name__)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _validate_token_with_keycloak(token: str, session: AsyncSession) -> dict[str, Any]:
    """Verify a Keycloak access token and resolve the member and roles behind it."""
    try:
        claims = await get_oidc_token_verifier().verify(token)
    except InvalidOIDCToken as exc:
        # The reason stays in the logs: it helps an attacker more than a legitimate client.
        _log.info("Rejected OIDC token: %s", exc)
        raise _unauthorized("Invalid OIDC token") from exc
    except OidcProviderUnavailable as exc:
        _log.warning("OIDC provider unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OIDC provider temporarily unavailable",
            headers={"Retry-After": "30"},
        ) from exc

    role_repository = RoleRepository(session)
    username = claims.get("preferred_username")
    if not isinstance(username, str):
        username = None

    uid = claims.get("adh6_id")
    if not uid and username:
        try:
            uid = await role_repository.user_id_from_username(login=username)
        except MemberNotFoundError:
            # The account exists in Keycloak but has no ADH6 member yet.
            uid = None

    # Groups returned by keycloak start with /
    raw_groups = claims.get("groups")
    groups = (
        [group.lstrip("/") for group in raw_groups if isinstance(group, str)] if isinstance(raw_groups, list) else []
    )

    role_mappings = await role_repository.find_for_oidc_identity(groups=groups, username=username)

    return {
        "uid": uid,
        "scope": [Roles.USER.value, *(mapping.role for mapping in role_mappings)],
        "groups": groups,
        "username": username,
        "auth_method": "oidc",
    }


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

    uid: int | None
    try:
        uid = await role_repository.user_id_from_username(api_key.user_login)
    except MemberNotFoundError:
        uid = None

    return {
        "uid": uid,
        "scope": [Roles.USER.value, *roles],
        "groups": [],
        "adh6_id": uid,
        "username": api_key.user_login,
        "auth_method": "api_key",
        "api_key_id": api_key.id,
    }


async def authenticate(request: Request, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    """Attach the caller's identity to the request, in the same session as the route."""
    if not request.url.path.startswith("/api"):
        return

    auth_header = request.headers.get("Authorization", "")
    api_key_header = request.headers.get("X-API-KEY", "")
    try:
        if auth_header.startswith("Bearer "):
            token_info = await _validate_token_with_keycloak(auth_header.removeprefix("Bearer "), session)
        elif api_key_header:
            token_info = await _validate_api_key(api_key_header, session)
        else:
            return
    except HTTPException:
        raise
    except Exception as exc:
        # Not the caller's fault (database down, bug): a 401 would make the frontend log the user out.
        _log.exception("Authentication failed unexpectedly")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication failed") from exc

    request.state.token_info = token_info
    set_user(token_info.get("uid"))
    set_api_key_id(token_info.get("api_key_id"))
