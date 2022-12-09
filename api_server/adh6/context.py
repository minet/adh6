import typing as t
from connexion import context

def get_roles() -> t.List[str]:
    return context.get("token_info", {}).get("scope", [])

def get_user() -> str:
    return context.get("token_info", {}).get("uid", [])

def get_login() -> str:
    return context.get("token_info", {}).get("login", [])