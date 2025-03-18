import typing as t
from connexion import request

def get_roles() -> t.List[str]:
    return request.context.get("token_info", {}).get("scope", [])

def get_user() -> str:
    return request.context.get("token_info", {}).get("uid", [])
