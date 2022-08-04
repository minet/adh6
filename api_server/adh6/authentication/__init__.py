import os
import requests

from enum import Enum
from typing import Any, Dict, Optional
from connexion.exceptions import OAuthResponseProblem, Unauthorized

from adh6.misc.log import LOG


class Roles(Enum):
    USER = "user"
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_PROD = "admin:prod"
    TRESO_READ = "treasurer:read"
    TRESO_WRITE = "treasurer:write"
    NETWORK_READ = "network:read"
    NETWORK_WRITE = "network:write"
    NETWORK_PROD = "network:write:prod"
    NETWORK_DEV = "network:write:dev"
    NETWORK_HOSTING = "network:write:hosting" 


class AuthenticationMethod(Enum):
    NONE = "none"
    API_KEY = "api_key"
    OIDC = "oidc"
    USER = "user"


class Method(Enum):
    READ = 0
    WRITE = 1


from adh6.authentication.storage.api_key_repository import ApiKeySQLRepository
from adh6.authentication.storage.role_repository import RoleSQLRepository


role_repository = RoleSQLRepository() 
api_key_repository = ApiKeySQLRepository()


def apikey_auth(token: str, required_scopes):
    try:
        from hashlib import sha512
        api_key = api_key_repository.find(token_hash=sha512().update(token.encode("utf-8")))[0]
        if not api_key or not api_key.login:
            raise
    except Exception as e:
        LOG.info(e)
        raise Unauthorized('invalid api key')
    return {
        "uid": role_repository.user_id_from_username(login=api_key.login),
        "scope": [
            i.role for i in role_repository.find(
                method=AuthenticationMethod.API_KEY, 
                identifiers=[str(api_key.id) if api_key.id else ""]
            )[0]
        ] + [Roles.USER.value]
    }


def token_info(access_token) -> Optional[Dict[str, Any]]:
    infos = get_sso_groups(access_token)

    groups = ['adh6_user']
    if 'attributes' in infos and 'memberOf' in infos['attributes']:
        groups += [e.split(",")[0].split("=")[1] for e in infos['attributes']['memberOf']]

    uid = role_repository.user_id_from_username(login=infos["id"])
    if not uid:
        raise Unauthorized('invalid api key')
    return {
        "uid": uid,
        "scope": [
            i.role for i in role_repository.find(
                method=AuthenticationMethod.OIDC, 
                identifiers=groups, 
            )[0]
        ] + [Roles.USER.value] + [i.role for i in role_repository.find(
                    method=AuthenticationMethod.USER,
                    identifiers=[infos["id"]]
                )[0]
            ]
    }

def get_sso_groups(token):
    try:
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(
            url='{}/profile'.format(os.environ.get("OAUTH2_BASE_PATH", "http://localhost")),
            headers=headers,
            timeout=1,
            verify=True
        )
    except requests.exceptions.ReadTimeout:
        raise OAuthResponseProblem("Could not authenticate")

    if r.status_code != 200 or "id" not in r.json(): 
        raise OAuthResponseProblem("Could not authenticate")
    return r.json()

