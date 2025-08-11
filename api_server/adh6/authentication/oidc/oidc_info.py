from typing import Any

from jwcrypto.jwt import JWTExpired, JWTInvalidClaimFormat, JWTInvalidClaimValue, JWTMissingClaim, JWTMissingKey, JWTNotYetValid
from connexion.exceptions import Unauthorized
from flask import current_app

from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.storage import RoleRepository

JWTInvalid = (JWTExpired, JWTInvalidClaimFormat, JWTInvalidClaimValue, JWTMissingClaim, JWTMissingKey, JWTNotYetValid)


role_repository = RoleRepository()


def oidc_info(token, required_scopes=None) -> dict[str, Any] | None:
    keycloak = current_app.config["KEYCLOAK_CLIENT"]
    try:
        token_data = keycloak.decode_token(token)
    except JWTInvalid as e:
        raise Unauthorized(f"Invalid OIDC token ({type(e).__name__.replace('JWT', '')}) : {e})") from e
    print(f"oidc_info token_data: {token_data}")

    if not token_data:
        raise Unauthorized("Invalid OIDC token: no data found")
    if not isinstance(token_data, dict):
        raise Unauthorized("Invalid OIDC token: the data is not properly formatted")

    uid = token_data.get("adh6_id")
    if not uid:
        uid = role_repository.user_id_from_username(login=token_data.get("preferred_username"))

    # Groups returned by keycloak start with /
    groups = list(map(lambda group: group.lstrip("/"), token_data.get("groups", [])))

    # Find roles based on groups (OIDC method) and username (USER method)
    roles = []
    if groups:
        roles.extend(
            [
                i.role
                for i in role_repository.find(
                    method=AuthenticationMethod.OIDC,
                    identifiers=groups,
                )[0]
            ]
        )

    if token_data.get("preferred_username"):
        roles.extend(
            [
                i.role
                for i in role_repository.find(
                    method=AuthenticationMethod.USER, identifiers=[token_data.get("preferred_username")]
                )[0]
            ]
        )

    scope = [Roles.USER.value, *roles]

    # Check if the user is authenticated properly
    if required_scopes:
        print("REQUIRED SCOPES:", required_scopes)
        if not isinstance(required_scopes, list):
            raise Unauthorized("Invalid OIDC token: required scopes must be a list")
        if not all(req in scope for req in required_scopes):
            raise Unauthorized(f"Invalid OIDC token: missing required scopes {required_scopes}")

    result = {"uid": uid, "scope": scope, "groups": groups, "username": token_data.get("preferred_username")}
    print(f"oidc_info result: {result}")
    return result
