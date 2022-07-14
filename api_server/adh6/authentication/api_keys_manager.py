from connexion.exceptions import Unauthorized
from adh6.authentication import AuthenticationMethod
from adh6.authentication.storage import RoleRepository

from adh6.storage import cache

@cache.memoize(300)
def apikey_auth(token: str, required_scopes):
    role_handler = RoleRepository()
    try:
        name = role_handler.get_api_key_user(api_key=token)
    except:
        raise Unauthorized('invalid api key')
    return {
        "uid": role_handler.get_user_id(user_name=name),
        "scope": role_handler.get_roles(method=AuthenticationMethod.API_KEY, roles=[token], user_name=name)
    }

