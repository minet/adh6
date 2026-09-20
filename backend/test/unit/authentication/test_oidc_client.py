from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from adh6.authentication.oidc.client import OidcClient, OidcExchangeRejected
from adh6.authentication.oidc.token_verifier import OidcProviderUnavailable

ISSUER = "https://keycloak.test/realms/MiNET"
METADATA = {
    "issuer": ISSUER,
    "authorization_endpoint": f"{ISSUER}/protocol/openid-connect/auth",
    "token_endpoint": f"{ISSUER}/protocol/openid-connect/token",
    "end_session_endpoint": f"{ISSUER}/protocol/openid-connect/logout",
}


def _client(handler, **kwargs) -> tuple[OidcClient, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    http = httpx.AsyncClient(transport=httpx.MockTransport(record))
    client = OidcClient(ISSUER, "adh6", "https://adh6.test/api/auth/callback", http_client=http, **kwargs)
    return client, seen


def _keycloak(token_response: httpx.Response | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=METADATA)
        return token_response or httpx.Response(
            200,
            json={
                "access_token": "a",
                "expires_in": 300,
                "refresh_token": "r",
                "refresh_expires_in": 0,
                "id_token": "i",
            },
        )

    return handler


async def test_the_authorization_url_carries_pkce_state_and_nonce():
    client, _ = _client(_keycloak(), scope="openid offline_access")

    url = await client.authorization_url(state="s", nonce="n", code_challenge="c")

    parts = urlsplit(url)
    query = {key: values[0] for key, values in parse_qs(parts.query).items()}
    assert f"{parts.scheme}://{parts.netloc}{parts.path}" == METADATA["authorization_endpoint"]
    assert query == {
        "client_id": "adh6",
        "response_type": "code",
        "scope": "openid offline_access",
        "redirect_uri": "https://adh6.test/api/auth/callback",
        "state": "s",
        "nonce": "n",
        "code_challenge": "c",
        "code_challenge_method": "S256",
    }


async def test_the_code_is_exchanged_with_its_verifier_and_no_secret_for_a_public_client():
    client, seen = _client(_keycloak())

    tokens = await client.exchange_code("the-code", "the-verifier")

    form = {key: values[0] for key, values in parse_qs(seen[-1].content.decode()).items()}
    assert form == {
        "client_id": "adh6",
        "grant_type": "authorization_code",
        "code": "the-code",
        "redirect_uri": "https://adh6.test/api/auth/callback",
        "code_verifier": "the-verifier",
    }
    assert (tokens.access_token, tokens.refresh_token, tokens.id_token) == ("a", "r", "i")
    assert (tokens.expires_in, tokens.refresh_expires_in) == (300, 0)


async def test_a_confidential_client_sends_its_secret():
    client, seen = _client(_keycloak(), client_secret="s3cret")

    await client.refresh("r")

    form = parse_qs(seen[-1].content.decode())
    assert form["client_secret"] == ["s3cret"]
    assert form["grant_type"] == ["refresh_token"]


async def test_a_refused_code_is_a_rejection_not_an_outage():
    client, _ = _client(_keycloak(httpx.Response(400, json={"error": "invalid_grant"})))

    with pytest.raises(OidcExchangeRejected):
        await client.exchange_code("used", "v")


@pytest.mark.parametrize("response", [httpx.Response(503), httpx.ConnectError("down")])
async def test_an_unreachable_keycloak_is_an_outage(response):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=METADATA)
        if isinstance(response, Exception):
            raise response
        return response

    client, _ = _client(handler)

    with pytest.raises(OidcProviderUnavailable):
        await client.refresh("r")


async def test_a_token_response_without_an_access_token_is_rejected():
    client, _ = _client(_keycloak(httpx.Response(200, json={"expires_in": 300})))

    with pytest.raises(OidcExchangeRejected):
        await client.refresh("r")


async def test_discovery_of_another_issuer_is_refused_and_discovery_is_cached():
    client, _ = _client(lambda request: httpx.Response(200, json={**METADATA, "issuer": "https://evil.test"}))
    with pytest.raises(OidcProviderUnavailable):
        await client.authorization_url(state="s", nonce="n", code_challenge="c")

    client, seen = _client(_keycloak())
    await client.authorization_url(state="s", nonce="n", code_challenge="c")
    await client.authorization_url(state="s", nonce="n", code_challenge="c")
    assert len(seen) == 1


async def test_the_logout_url_names_the_client_and_the_id_token():
    client, _ = _client(_keycloak())

    url = await client.end_session_url(post_logout_redirect_uri="https://adh6.test/", id_token_hint="i")

    query = {key: values[0] for key, values in parse_qs(urlsplit(url).query).items()}
    assert query == {"client_id": "adh6", "post_logout_redirect_uri": "https://adh6.test/", "id_token_hint": "i"}
    assert url.startswith(METADATA["end_session_endpoint"])


@pytest.mark.parametrize("status", [408, 425, 429])
async def test_a_rate_limit_or_timeout_is_an_outage_not_a_refusal(status):
    client, _ = _client(_keycloak(httpx.Response(status)))

    with pytest.raises(OidcProviderUnavailable):
        await client.refresh("r")


@pytest.mark.parametrize("document", [None, [], "text", 3])
async def test_a_discovery_document_that_is_not_an_object_is_an_outage(document):
    client, _ = _client(lambda request: httpx.Response(200, json=document))

    with pytest.raises(OidcProviderUnavailable):
        await client.authorization_url(state="s", nonce="n", code_challenge="c")
