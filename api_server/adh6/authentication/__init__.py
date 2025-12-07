import os
from enum import Enum

from connexion.exceptions import Unauthorized

from adh6.authentication.storage import ApiKeyRepository, RoleRepository

from .enums import AuthenticationMethod, Roles


class Method(Enum):
    READ = 0
    WRITE = 1


role_repository = RoleRepository()
api_key_repository = ApiKeyRepository()


def apikey_admin_auth(token: str, required_scopes):
    return apikey_auth(token, [Roles.ADMIN_READ.value, Roles.ADMIN_WRITE.value])


def apikey_network_auth(token: str, required_scopes):
    return apikey_auth(token, [Roles.NETWORK_READ.value, Roles.NETWORK_WRITE.value])


def apikey_treasury_auth(token: str, required_scopes):
    return apikey_auth(token, [Roles.TRESO_READ.value, Roles.TRESO_WRITE.value])


def apikey_auth(token: str, required_scopes):
    try:
        from hashlib import sha3_512

        api_key = api_key_repository.find(token_hash=sha3_512(token.encode("utf-8")).hexdigest())[0]
        if not api_key or not api_key.login:
            raise
        roles = [
            i.role
            for i in role_repository.find(
                method=AuthenticationMethod.API_KEY, identifiers=[str(api_key.id) if api_key.id else ""]
            )[0]
        ]
        if len(set(roles) & set(required_scopes)) != len(required_scopes):
            raise Unauthorized("invalid api key")  # noqa: TRY301
    except Exception:
        raise Unauthorized("invalid api key")
    return {"uid": role_repository.user_id_from_username(login=api_key.login), "scope": roles}


user_id = "preferred_username" if "keycloak" in os.environ.get("OAUTH2_BASE_PATH", "http://localhost") else "id"
