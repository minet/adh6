from typing import Any

from connexion.exceptions import Unauthorized
from flask import current_app
from jwcrypto.jwt import (
    JWTExpired,
    JWTInvalidClaimFormat,
    JWTInvalidClaimValue,
    JWTMissingClaim,
    JWTMissingKey,
    JWTNotYetValid,
)

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage import RoleRepository

JWTInvalid = (JWTExpired, JWTInvalidClaimFormat, JWTInvalidClaimValue, JWTMissingClaim, JWTMissingKey, JWTNotYetValid)


role_repository = RoleRepository()


def oidc_info(token, required_scopes=None) -> dict[str, Any] | None:
    if required_scopes and not isinstance(required_scopes, list):
        raise Unauthorized("Invalid OIDC token: required scopes must be a list")

    keycloak = current_app.config["KEYCLOAK_CLIENT"]
    try:
        token_data = keycloak.decode_token(token)
    except JWTInvalid as e:
        raise Unauthorized(f"Invalid OIDC token ({type(e).__name__.replace('JWT', '')}) : {e}") from e

    if not token_data:
        raise Unauthorized("Invalid OIDC token: no data found")
    if not isinstance(token_data, dict):
        raise Unauthorized("Invalid OIDC token: the data is not properly formatted")

    uid = token_data.get("adh6_id")
    if not uid:
        username = token_data.get("preferred_username")
        if username:
            uid = role_repository.user_id_from_username(login=username)

    # Groups returned by keycloak start with /
    groups = [group.lstrip("/") for group in token_data.get("groups", []) if group is not None]

    # Find roles based on groups (OIDC method) and username (USER method)
    roles = []
    if groups:
        result, _ = role_repository.find(
            method=AuthenticationMethod.OIDC,
            identifiers=groups,
        )
        roles.extend([i.role for i in result])

    if token_data.get("preferred_username"):
        username = token_data.get("preferred_username")
        if username:
            result, _ = role_repository.find(
                method=AuthenticationMethod.USER,
                identifiers=[username],
            )
            roles.extend([i.role for i in result])

    scope = [Roles.USER.value, *roles]

    # Check if the user is authenticated properly
    if required_scopes and not all(req in scope for req in required_scopes):
        raise Unauthorized(f"Invalid OIDC token: missing required scopes {required_scopes}")

    result = {"uid": uid, "scope": scope, "groups": groups, "username": token_data.get("preferred_username")}
    return result
