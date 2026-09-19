"""A browser session: the same identity as a Bearer token, but changes must prove they come from the app."""

import pytest

from test import TESTING_CLIENT_TOKEN
from test.integration.resource import base_url as host_url

SESSION_COOKIE = {"Cookie": f"adh6_access={TESTING_CLIENT_TOKEN}"}
FROM_THE_APP = {"X-Requested-With": "XMLHttpRequest"}


@pytest.fixture
async def client(_test_client, sample_member_admin):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures([sample_member_admin], api_key_fixtures())

    yield _test_client

    await cleanup_test_data()


def test_the_session_cookie_identifies_the_user(client):
    r = client.get(f"{host_url}/profile", headers=SESSION_COOKIE)

    assert r.status_code == 200


def test_nobody_signed_in_is_told_to_authenticate(client):
    r = client.get(f"{host_url}/profile")

    assert r.status_code == 401


def test_a_change_made_with_the_cookie_alone_is_refused(client):
    r = client.post(f"{host_url}/api_keys", json={"name": "csrf"}, headers=SESSION_COOKIE)

    assert r.status_code == 403
    assert r.json()["detail"] == "Cross-site request refused"


def test_a_change_made_by_the_app_goes_through_the_same_checks_as_a_bearer_token(client):
    from_the_app = client.get(f"{host_url}/api_keys", headers={**SESSION_COOKIE, **FROM_THE_APP})
    bearer = client.get(f"{host_url}/api_keys", headers={"Authorization": f"Bearer {TESTING_CLIENT_TOKEN}"})

    assert from_the_app.status_code == bearer.status_code == 200


def test_the_login_routes_work_in_the_real_app_even_with_an_expired_session_cookie(client):
    from unittest.mock import AsyncMock, MagicMock

    from adh6.authentication.oidc.client import OidcClient, get_oidc_client

    keycloak = MagicMock(spec=OidcClient)
    keycloak.authorization_url = AsyncMock(return_value="https://keycloak.test/auth")
    client.app.dependency_overrides[get_oidc_client] = lambda: keycloak
    try:
        r = client.get(
            "/api/auth/login",
            params={"return_to": "/fr/member"},
            headers={"Cookie": "adh6_access=expired"},
            follow_redirects=False,
        )
    finally:
        client.app.dependency_overrides.pop(get_oidc_client, None)

    assert r.status_code == 302
    assert r.headers["location"] == "https://keycloak.test/auth"
    assert "adh6_oidc_login=" in r.headers["set-cookie"]
