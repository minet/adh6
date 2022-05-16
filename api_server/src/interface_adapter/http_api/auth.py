# coding=utf-8
from typing import Any, Dict, Optional
import requests
import requests.exceptions
from flask_caching import Cache
from src.interface_adapter.sql.model.models import ApiKey, db
from connexion.exceptions import OAuthProblem

cache = Cache()

@cache.memoize(300)
def apikey_auth(token: str, required_scopes):
    exist: Optional[ApiKey] = db.session().query(ApiKey).filter(ApiKey.uuid == token).one_or_none()
    if exist is None:
        raise OAuthProblem('invalid api key')
    return {
        "uid": exist.name,
        "scope": ["profile"],
        "groups": [exist.role]
    }

def token_info(access_token) -> Optional[Dict[str, Any]]:
    infos = get_sso_groups(access_token)
    if not infos:
        raise OAuthProblem('invalid access token, no info found')
    groups = ['adh6_user']
    if 'attributes' in infos and 'memberOf' in infos['attributes']:
        groups += [e.split(",")[0].split("=")[1] for e in infos['attributes']['memberOf']]

    return {
        "uid": infos["id"],
        "scope": ['profile'],
        "groups": groups
    }

@cache.memoize(300)
def get_sso_groups(token):
    try:
        headers = {"Authorization": "Bearer " + token}
        r = requests.get(
            '{}/profile'.format(os.environ.get("OAUTH2_BASE_PATH")),
            headers=headers,
            timeout=1,
            verify=True
        )
    except requests.exceptions.ReadTimeout:
        return None
    if r.status_code != 200 or "id" not in r.json():
        return None

    result = r.json()
    return result

