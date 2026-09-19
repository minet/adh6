import base64
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from adh6.authentication.oidc.client import OidcClient, OidcExchangeRejected, TokenResponse, get_oidc_client
from adh6.authentication.oidc.token_verifier import OidcProviderUnavailable
from adh6.authentication.session.cookies import (
    LOGIN_COOKIE,
    pkce_challenge,
)
from adh6.authentication.session.router import router
from fastapi import FastAPI
from fastapi.testclient import TestClient

APP_HEADERS = {"X-Requested-With": "XMLHttpRequest"}


def _id_token(nonce: str | None) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"nonce": nonce}).encode()).decode().rstrip("=")
    return f"e30.{payload}.sig"


@pytest.fixture
def keycloak() -> MagicMock:
    client = MagicMock(spec=OidcClient)
    client.redirect_uri = "https://adh6.test/api/auth/callback"
    client.authorization_url = AsyncMock(return_value="https://keycloak.test/auth?x=1")
    client.end_session_url = AsyncMock(return_value="https://keycloak.test/logout?client_id=adh6")
    client.refresh = AsyncMock(return_value=TokenResponse("new-access", 300, "new-refresh", 1800))
    return client


@pytest.fixture
def http(keycloak):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_oidc_client] = lambda: keycloak
    # The cookies are Secure and the test server is plain http: they are passed by hand.
    return TestClient(app, follow_redirects=False, base_url="https://adh6.test")


def _start_login(http: TestClient, keycloak: MagicMock, return_to: str = "/en/member/12"):
    response = http.get("/api/auth/login", params={"return_to": return_to})
    login_cookie = response.cookies.get(LOGIN_COOKIE)
    call = keycloak.authorization_url.await_args.kwargs
    return response, login_cookie, call


def _callback(http: TestClient, keycloak: MagicMock, login_cookie: str | None, call: dict, **overrides):
    keycloak.exchange_code = AsyncMock(
        return_value=TokenResponse("access", 300, "refresh", 0, _id_token(overrides.pop("nonce", call["nonce"])))
    )
    params = {"code": "the-code", "state": call["state"], **overrides}
    cookies = {LOGIN_COOKIE: login_cookie} if login_cookie else {}
    return http.get("/api/auth/callback", params={k: v for k, v in params.items() if v is not None}, cookies=cookies)


def test_login_hands_over_to_keycloak_and_remembers_the_attempt(http, keycloak):
    response, login_cookie, call = _start_login(http, keycloak)

    assert response.status_code == 302
    assert response.headers["location"] == "https://keycloak.test/auth?x=1"
    assert login_cookie
    assert call["code_challenge"] == pkce_challenge(_verifier_from(login_cookie))
    assert call["state"] and call["nonce"] and call["state"] != call["nonce"]
    # The verifier stays in the cookie: it must not travel through the URL.
    assert _verifier_from(login_cookie) not in response.headers["location"]


def _verifier_from(cookie: str) -> str:
    payload = cookie.rsplit(".", 1)[0]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["code_verifier"]


def test_login_never_returns_to_another_site(http, keycloak):
    _, login_cookie, _ = _start_login(http, keycloak, return_to="https://evil.example/")
    response = _callback(http, keycloak, login_cookie, keycloak.authorization_url.await_args.kwargs)

    assert response.headers["location"] == "/"


def test_login_reports_an_unavailable_keycloak_to_the_app(http, keycloak):
    keycloak.authorization_url.side_effect = OidcProviderUnavailable("down")

    response = http.get("/api/auth/login", params={"return_to": "/en/room"})

    assert response.status_code == 302
    assert response.headers["location"] == "/en/room?auth_error=provider_unavailable"
    assert LOGIN_COOKIE not in response.headers.get("set-cookie", "") or "Max-Age=0" in response.headers["set-cookie"]


def test_callback_opens_the_session_and_returns_where_the_user_was(http, keycloak):
    _, login_cookie, call = _start_login(http, keycloak)
    assert login_cookie

    response = _callback(http, keycloak, login_cookie, call)

    assert response.status_code == 302
    assert response.headers["location"] == "/en/member/12"
    keycloak.exchange_code.assert_awaited_once_with("the-code", _verifier_from(login_cookie))
    set_cookies = response.headers.get_list("set-cookie")
    assert {c.split("=")[0] for c in set_cookies} == {LOGIN_COOKIE, "adh6_access", "adh6_refresh", "adh6_id"}
    login_reset = next(c for c in set_cookies if c.startswith(f"{LOGIN_COOKIE}="))
    assert "Max-Age=0" in login_reset


@pytest.mark.parametrize(
    "overrides",
    [
        {"state": "another-state"},
        {"state": None},
        {"code": None},
        {"error": "access_denied"},
        {"nonce": "another-nonce"},
    ],
)
def test_callback_refuses_what_this_browser_did_not_ask_for(http, keycloak, overrides):
    _, login_cookie, call = _start_login(http, keycloak)

    response = _callback(http, keycloak, login_cookie, call, **overrides)

    assert response.status_code == 302
    assert response.headers["location"] == "/en/member/12?auth_error=login_failed"
    assert "adh6_access" not in response.headers.get("set-cookie", "")


def test_callback_without_a_login_in_progress_is_refused(http, keycloak):
    _, _, call = _start_login(http, keycloak)
    http.cookies.clear()

    response = _callback(http, keycloak, None, call)

    assert response.headers["location"] == "/?auth_error=login_failed"
    keycloak.exchange_code.assert_not_awaited()


def test_callback_reports_a_rejected_code_and_an_unavailable_keycloak(http, keycloak):
    _, login_cookie, call = _start_login(http, keycloak)
    keycloak.exchange_code = AsyncMock(side_effect=OidcExchangeRejected("invalid_grant"))
    rejected = http.get(
        "/api/auth/callback", params={"code": "c", "state": call["state"]}, cookies={LOGIN_COOKIE: login_cookie}
    )
    keycloak.exchange_code = AsyncMock(side_effect=OidcProviderUnavailable("down"))
    unavailable = http.get(
        "/api/auth/callback", params={"code": "c", "state": call["state"]}, cookies={LOGIN_COOKIE: login_cookie}
    )

    assert rejected.headers["location"].endswith("auth_error=login_failed")
    assert unavailable.headers["location"].endswith("auth_error=provider_unavailable")


def test_refresh_renews_the_access_token(http, keycloak):
    response = http.post("/api/auth/refresh", headers=APP_HEADERS, cookies={"adh6_refresh": "old-refresh"})

    assert response.status_code == 204
    keycloak.refresh.assert_awaited_once_with("old-refresh")
    assert {c.split("=")[0] for c in response.headers.get_list("set-cookie")} == {"adh6_access", "adh6_refresh"}


def test_refresh_needs_the_app_header_and_a_session(http, keycloak):
    no_header = http.post("/api/auth/refresh", cookies={"adh6_refresh": "old"})
    no_session = http.post("/api/auth/refresh", headers=APP_HEADERS)

    assert no_header.status_code == 403
    assert no_session.status_code == 401
    keycloak.refresh.assert_not_awaited()


def test_refresh_ends_a_session_keycloak_no_longer_knows(http, keycloak):
    keycloak.refresh.side_effect = OidcExchangeRejected("invalid_grant")

    response = http.post("/api/auth/refresh", headers=APP_HEADERS, cookies={"adh6_refresh": "old"})

    assert response.status_code == 401
    assert all("Max-Age=0" in c for c in response.headers.get_list("set-cookie"))
    assert len(response.headers.get_list("set-cookie")) == 3


def test_refresh_reports_an_unavailable_keycloak_without_ending_the_session(http, keycloak):
    keycloak.refresh.side_effect = OidcProviderUnavailable("down")

    response = http.post("/api/auth/refresh", headers=APP_HEADERS, cookies={"adh6_refresh": "old"})

    assert response.status_code == 503
    assert not response.headers.get_list("set-cookie")


def test_logout_clears_the_session_and_says_where_to_end_the_keycloak_one(http, keycloak):
    response = http.post("/api/auth/logout", headers=APP_HEADERS, cookies={"adh6_id": "the-id-token"})

    assert response.status_code == 200
    assert response.json() == {"logout_url": "https://keycloak.test/logout?client_id=adh6"}
    keycloak.end_session_url.assert_awaited_once_with(
        post_logout_redirect_uri="https://adh6.test/", id_token_hint="the-id-token"
    )
    assert len(response.headers.get_list("set-cookie")) == 3
    assert all("Max-Age=0" in c for c in response.headers.get_list("set-cookie"))


def test_logout_cannot_be_triggered_from_another_site(http, keycloak):
    assert http.get("/api/auth/logout").status_code == 405
    assert http.post("/api/auth/logout", headers={"Sec-Fetch-Site": "cross-site", **APP_HEADERS}).status_code == 403
    assert http.post("/api/auth/logout").status_code == 403


def test_logout_still_closes_the_local_session_when_keycloak_is_down(http, keycloak):
    keycloak.end_session_url.side_effect = OidcProviderUnavailable("down")

    response = http.post("/api/auth/logout", headers=APP_HEADERS)

    assert response.json() == {"logout_url": "/"}
    assert len(response.headers.get_list("set-cookie")) == 3


def test_the_login_routes_are_not_part_of_the_api_spec():
    app = FastAPI()
    app.include_router(router, prefix="/api")

    assert not [path for path in app.openapi()["paths"] if path.startswith("/api/auth")]
