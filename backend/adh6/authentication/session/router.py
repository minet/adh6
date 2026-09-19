"""Routes of the browser login. They are followed by the browser itself, so they are not part of the API spec."""

import hmac
import logging
from typing import Annotated
from urllib.parse import urlencode, urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from adh6.authentication.oidc.client import OidcClient, OidcExchangeRejected, get_oidc_client
from adh6.authentication.oidc.token_verifier import OidcProviderUnavailable

from .cookies import (
    ID_COOKIE,
    REFRESH_COOKIE,
    clear_login_cookie,
    clear_session_cookies,
    id_token_nonce,
    new_login_transaction,
    pkce_challenge,
    read_login_transaction,
    set_login_cookie,
    set_session_cookies,
)
from .csrf import enforce_csrf_protection

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", include_in_schema=False)

OidcClientDep = Annotated[OidcClient, Depends(get_oidc_client)]


def _back_to_app(target: str, reason: str) -> RedirectResponse:
    separator = "&" if "?" in target else "?"
    response = RedirectResponse(f"{target}{separator}{urlencode({'auth_error': reason})}", status_code=302)
    clear_login_cookie(response)
    return response


@router.get("/login")
async def login(client: OidcClientDep, return_to: str = "/") -> RedirectResponse:
    transaction = new_login_transaction(return_to)
    try:
        url = await client.authorization_url(
            state=transaction.state,
            nonce=transaction.nonce,
            code_challenge=pkce_challenge(transaction.code_verifier),
        )
    except OidcProviderUnavailable:
        _log.warning("Cannot start a login: OIDC provider unavailable", exc_info=True)
        return _back_to_app(transaction.return_to, "provider_unavailable")

    response = RedirectResponse(url, status_code=302)
    set_login_cookie(response, transaction)
    return response


@router.get("/callback")
async def callback(
    request: Request,
    client: OidcClientDep,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    transaction = read_login_transaction(request)
    if transaction is None:
        _log.info("Login callback without a valid login in progress")
        return _back_to_app("/", "login_failed")
    if error or not code or not state or not hmac.compare_digest(state, transaction.state):
        _log.info("Login callback refused (error=%r)", error)
        return _back_to_app(transaction.return_to, "login_failed")

    try:
        tokens = await client.exchange_code(code, transaction.code_verifier)
    except OidcExchangeRejected:
        _log.info("Keycloak rejected the authorization code", exc_info=True)
        return _back_to_app(transaction.return_to, "login_failed")
    except OidcProviderUnavailable:
        _log.warning("Cannot finish a login: OIDC provider unavailable", exc_info=True)
        return _back_to_app(transaction.return_to, "provider_unavailable")

    if not tokens.id_token or not hmac.compare_digest(id_token_nonce(tokens.id_token) or "", transaction.nonce):
        _log.warning("Login callback with a missing or foreign nonce")
        return _back_to_app(transaction.return_to, "login_failed")

    response = RedirectResponse(transaction.return_to, status_code=302)
    clear_login_cookie(response)
    set_session_cookies(response, tokens)
    return response


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(request: Request, client: OidcClientDep) -> Response:
    enforce_csrf_protection(request)
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session to renew")

    try:
        tokens = await client.refresh(refresh_token)
    except OidcExchangeRejected as exc:
        response = JSONResponse({"detail": "Session expired"}, status_code=status.HTTP_401_UNAUTHORIZED)
        clear_session_cookies(response)
        _log.info("Keycloak rejected the refresh token: %s", exc)
        return response
    except OidcProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OIDC provider temporarily unavailable",
            headers={"Retry-After": "30"},
        ) from exc

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    set_session_cookies(response, tokens)
    return response


@router.post("/logout")
async def logout(request: Request, client: OidcClientDep) -> JSONResponse:
    enforce_csrf_protection(request)
    redirect = urlsplit(client.redirect_uri)
    try:
        logout_url = await client.end_session_url(
            post_logout_redirect_uri=f"{redirect.scheme}://{redirect.netloc}/",
            id_token_hint=request.cookies.get(ID_COOKIE),
        )
    except OidcProviderUnavailable:
        _log.warning("Cannot reach Keycloak to end its session", exc_info=True)
        logout_url = "/"

    response = JSONResponse({"logout_url": logout_url})
    clear_session_cookies(response)
    return response
