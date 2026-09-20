"""The cookies of a browser session and of a login in progress."""

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import asdict, dataclass
from typing import Literal, cast
from urllib.parse import urlsplit

from fastapi import Request, Response

from adh6.authentication.oidc.client import TokenResponse
from adh6.config.configuration import settings

ACCESS_COOKIE = "adh6_access"
REFRESH_COOKIE = "adh6_refresh"
ID_COOKIE = "adh6_id"
LOGIN_COOKIE = "adh6_oidc_login"

SESSION_PATH = "/api"
LOGIN_PATH = "/api/auth"


@dataclass(frozen=True)
class LoginTransaction:
    state: str
    nonce: str
    code_verifier: str
    return_to: str
    created_at: int


def new_login_transaction(return_to: str) -> LoginTransaction:
    return LoginTransaction(
        state=secrets.token_urlsafe(32),
        nonce=secrets.token_urlsafe(32),
        code_verifier=secrets.token_urlsafe(64),
        return_to=safe_return_to(return_to),
        created_at=int(time.time()),
    )


def pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def safe_return_to(target: str) -> str:
    if not target.startswith("/") or target.startswith("//") or "\\" in target:
        return "/"
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or any(ord(char) < 0x20 or ord(char) == 0x7F for char in target):
        return "/"
    return target


def _signature(payload: str) -> str:
    if settings.session_secret is None:
        raise ValueError("SESSION_SECRET must be set")
    key = settings.session_secret.get_secret_value().encode()
    return hmac.new(key, payload.encode("ascii"), hashlib.sha256).hexdigest()


def _sign(transaction: LoginTransaction) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(asdict(transaction)).encode()).decode("ascii").rstrip("=")
    return f"{payload}.{_signature(payload)}"


def read_login_transaction(request: Request, *, now: float | None = None) -> LoginTransaction | None:
    raw = request.cookies.get(LOGIN_COOKIE)
    if not raw or not raw.isascii() or "." not in raw:
        return None
    payload, signature = raw.rsplit(".", 1)
    if not hmac.compare_digest(signature, _signature(payload)):
        return None
    try:
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        transaction = LoginTransaction(**data)
    except (ValueError, TypeError):
        return None
    if (now if now is not None else time.time()) - transaction.created_at > settings.oidc_login_ttl_seconds:
        return None
    return transaction


def _set(
    response: Response,
    key: str,
    value: str,
    *,
    max_age: int,
    path: str,
    same_site: Literal["lax", "strict"],
) -> None:
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        path=path,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=same_site,
    )


def set_login_cookie(response: Response, transaction: LoginTransaction) -> None:
    _set(
        response,
        LOGIN_COOKIE,
        _sign(transaction),
        max_age=settings.oidc_login_ttl_seconds,
        path=LOGIN_PATH,
        same_site="lax",
    )


def clear_login_cookie(response: Response) -> None:
    response.delete_cookie(LOGIN_COOKIE, path=LOGIN_PATH)


def set_session_cookies(response: Response, tokens: TokenResponse) -> None:
    cap = settings.oidc_refresh_cookie_max_age_seconds
    refresh_lifetime = min(tokens.refresh_expires_in, cap) if tokens.refresh_expires_in > 0 else cap

    _set(
        response,
        ACCESS_COOKIE,
        tokens.access_token,
        max_age=max(tokens.expires_in, 1),
        path=SESSION_PATH,
        same_site="strict",
    )
    if tokens.refresh_token:
        _set(
            response,
            REFRESH_COOKIE,
            tokens.refresh_token,
            max_age=refresh_lifetime,
            path=SESSION_PATH,
            same_site="strict",
        )
    if tokens.id_token:
        _set(
            response,
            ID_COOKIE,
            tokens.id_token,
            max_age=refresh_lifetime,
            path=SESSION_PATH,
            same_site="strict",
        )


def clear_session_cookies(response: Response) -> None:
    for key in (ACCESS_COOKIE, REFRESH_COOKIE, ID_COOKIE):
        response.delete_cookie(key, path=SESSION_PATH)


def id_token_nonce(id_token: str) -> str | None:
    try:
        payload = id_token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except (IndexError, ValueError):
        return None
    nonce = cast(dict[str, object], claims).get("nonce") if isinstance(claims, dict) else None
    return nonce if isinstance(nonce, str) else None
