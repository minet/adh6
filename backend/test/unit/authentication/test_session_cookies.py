import base64
import json

import pytest
from adh6.authentication.oidc.client import TokenResponse
from adh6.authentication.session.cookies import (
    LOGIN_COOKIE,
    LoginTransaction,
    id_token_nonce,
    new_login_transaction,
    pkce_challenge,
    read_login_transaction,
    safe_return_to,
    set_login_cookie,
    set_session_cookies,
)
from adh6.config.configuration import settings
from fastapi import Request, Response


def _cookie_header(response: Response, name: str) -> str:
    return next(v.decode() for k, v in response.raw_headers if k == b"set-cookie" and v.decode().startswith(f"{name}="))


def _request_with_cookie(name: str, value: str) -> Request:
    return Request({"type": "http", "headers": [(b"cookie", f"{name}={value}".encode())]})


def _login_cookie_value(transaction: LoginTransaction) -> str:
    response = Response()
    set_login_cookie(response, transaction)
    return _cookie_header(response, LOGIN_COOKIE).split(";")[0].split("=", 1)[1]


def test_pkce_challenge_matches_the_rfc_7636_example():
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"

    assert pkce_challenge(verifier) == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


@pytest.mark.parametrize(
    "target",
    [
        "//evil.example",
        "https://evil.example/",
        "/\\evil.example",
        "evil",
        "",
        "/ok\nSet-Cookie: x=1",
        "javascript:alert(1)",
    ],
)
def test_only_paths_of_this_site_are_valid_places_to_return_to(target):
    assert safe_return_to(target) == "/"


@pytest.mark.parametrize("target", ["/", "/en/member/12", "/en/member/12?tab=devices"])
def test_paths_of_this_site_are_kept(target):
    assert safe_return_to(target) == target


def test_a_login_transaction_survives_the_round_trip_to_keycloak():
    transaction = new_login_transaction("/en/room/4")

    read = read_login_transaction(_request_with_cookie(LOGIN_COOKIE, _login_cookie_value(transaction)))

    assert read is not None
    assert read == transaction
    assert read.return_to == "/en/room/4"


def test_the_login_cookie_never_needs_to_leave_the_browser_readable_by_scripts():
    response = Response()
    set_login_cookie(response, new_login_transaction("/"))

    attributes = _cookie_header(response, LOGIN_COOKIE).lower()

    assert "httponly" in attributes
    assert "samesite=lax" in attributes
    assert "path=/api/auth" in attributes
    assert f"max-age={settings.oidc_login_ttl_seconds}" in attributes


def test_a_forged_login_cookie_is_refused():
    transaction = new_login_transaction("/")
    value = _login_cookie_value(transaction)
    payload, signature = value.rsplit(".", 1)
    data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    data["return_to"] = "/admin"
    forged = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

    assert read_login_transaction(_request_with_cookie(LOGIN_COOKIE, f"{forged}.{signature}")) is None
    assert read_login_transaction(_request_with_cookie(LOGIN_COOKIE, f"{payload}.{'0' * 64}")) is None
    assert read_login_transaction(_request_with_cookie(LOGIN_COOKIE, "garbage")) is None


@pytest.mark.parametrize("value", ["é.abcd", "abcd.é", "é"])
def test_a_login_cookie_with_non_ascii_characters_is_refused_instead_of_failing(value):
    assert read_login_transaction(_request_with_cookie(LOGIN_COOKIE, value)) is None


def test_an_old_login_is_refused_on_the_server_clock():
    transaction = new_login_transaction("/")
    request = _request_with_cookie(LOGIN_COOKIE, _login_cookie_value(transaction))

    assert read_login_transaction(request, now=transaction.created_at + settings.oidc_login_ttl_seconds - 1)
    assert read_login_transaction(request, now=transaction.created_at + settings.oidc_login_ttl_seconds + 1) is None


def test_a_session_is_kept_in_strict_http_only_cookies_scoped_to_the_api():
    response = Response()
    tokens = TokenResponse("access", 300, "refresh", 1800, "id")

    set_session_cookies(response, tokens)

    for name, max_age in (("adh6_access", 300), ("adh6_refresh", 1800), ("adh6_id", 1800)):
        attributes = _cookie_header(response, name).lower()
        assert "httponly" in attributes
        assert "samesite=strict" in attributes
        assert "path=/api" in attributes
        assert f"max-age={max_age}" in attributes
        assert "secure" in attributes


def test_offline_refresh_tokens_are_capped_because_they_report_no_expiry():
    response = Response()

    set_session_cookies(response, TokenResponse("access", 300, "refresh", 0, "id"))

    assert f"max-age={settings.oidc_refresh_cookie_max_age_seconds}" in _cookie_header(response, "adh6_refresh").lower()


def test_a_renewal_without_new_refresh_or_id_token_keeps_the_existing_ones():
    response = Response()

    set_session_cookies(response, TokenResponse("access", 300))

    names = [v.decode().split("=")[0] for k, v in response.raw_headers if k == b"set-cookie"]
    assert names == ["adh6_access"]


def _id_token(claims: dict) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"e30.{payload}.sig"


def test_the_nonce_is_read_from_the_id_token():
    assert id_token_nonce(_id_token({"nonce": "abc"})) == "abc"
    assert id_token_nonce(_id_token({"sub": "1"})) is None
    assert id_token_nonce("not-a-token") is None
