import typing as t
from connexion import request


def get_roles() -> t.List[str]:
    return request.context.get("token_info", {}).get("scope", [])


def get_user() -> int:
    return request.context.get("token_info", {}).get("uid", [])  # TODO: why return a list when we want an id ????
