from typing import Any, Dict, Optional
import requests as requests
import requests.exceptions as r_exceptions
from connexion.exceptions import OAuthProblem
import os
from adh6.authentication.interfaces.role_repository import AuthenticationMethod
from adh6.authentication.storage import RoleRepository

from adh6.storage import cache


def token_info(access_token) -> Optional[Dict[str, Any]]:
    infos = get_sso_groups(access_token)
    if not infos:
        raise OAuthProblem('invalid access token, no info found')

    role_handler = RoleRepository()
    groups = ['adh6_user']
    if 'attributes' in infos and 'memberOf' in infos['attributes']:
        groups += [e.split(",")[0].split("=")[1] for e in infos['attributes']['memberOf']]
    return {
        "uid": infos["id"],
        "scope": role_handler.get_roles(AuthenticationMethod.OIDC, groups)
    }

@cache.memoize(300)
def get_sso_groups(token):
    try:
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(
            '{}/profile'.format(os.environ.get("OAUTH2_BASE_PATH", "http://localhost")),
            headers=headers,
            timeout=1,
            verify=True
        )
    except r_exceptions.ReadTimeout:
        return None

    if r.status_code != 200 or "id" not in r.json():
        return None
    return r.json()

