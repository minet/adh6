"""Tests for OIDC access token verification (signature, claims and signing key cache)."""

import json
import time

import httpx
import pytest
from adh6.authentication.oidc.token_verifier import InvalidOIDCToken, OidcProviderUnavailable, OidcTokenVerifier
from jwcrypto import jwk, jwt

ISSUER = "https://keycloak.example/realms/MiNET"
CLIENT_ID = "adh6-keycloak"


def _rsa_key(kid: str) -> jwk.JWK:
    return jwk.JWK.generate(kty="RSA", size=2048, kid=kid, alg="RS256", use="sig")


KEY = _rsa_key("key-1")
ROTATED_KEY = _rsa_key("key-2")


def _token(key: jwk.JWK = KEY, alg: str = "RS256", **overrides) -> str:
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "exp": now + 300,
        "iat": now,
        "typ": "Bearer",
        "azp": CLIENT_ID,
        "sub": "user-uuid",
        "preferred_username": "testuser",
    }
    claims.update(overrides)
    claims = {name: value for name, value in claims.items() if value is not None}
    token = jwt.JWT(header={"alg": alg, "kid": key.key_id}, claims=claims)
    token.make_signed_token(key)
    return token.serialize()


class FakeKeycloak:
    """Serves discovery and JWKS, and counts how often the keys are downloaded."""

    def __init__(self, *keys: jwk.JWK, issuer: str = ISSUER):
        self.keys = list(keys)
        self.issuer = issuer
        self.up = True
        self.jwks_requests = 0

    def handler(self, request: httpx.Request) -> httpx.Response:
        if not self.up:
            return httpx.Response(503)
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json={"issuer": self.issuer, "jwks_uri": f"{ISSUER}/certs"})
        self.jwks_requests += 1
        encryption_key = {"kid": "enc", "kty": "RSA", "use": "enc", "alg": "RSA-OAEP", "n": "AQAB", "e": "AQAB"}
        public_keys = [json.loads(key.export_public()) for key in self.keys]
        return httpx.Response(200, json={"keys": [*public_keys, encryption_key]})


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def keycloak():
    return FakeKeycloak(KEY)


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def verifier(keycloak, clock):
    return OidcTokenVerifier(
        ISSUER,
        CLIENT_ID,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(keycloak.handler)),
        cache_ttl_seconds=3600,
        refresh_cooldown_seconds=30,
        clock=clock,
    )


async def test_valid_token_returns_claims(verifier):
    claims = await verifier.verify(_token())

    assert claims["preferred_username"] == "testuser"


async def test_client_can_be_in_audience_instead_of_azp(verifier):
    claims = await verifier.verify(_token(azp="other-client", aud=["account", CLIENT_ID]))

    assert claims["sub"] == "user-uuid"


async def test_token_without_sub_is_accepted(verifier):
    """Keycloak 25+ only adds `sub` when the `basic` client scope is assigned."""
    claims = await verifier.verify(_token(sub=None))

    assert "sub" not in claims


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(lambda: _token(exp=int(time.time()) - 3600), id="expired"),
        pytest.param(lambda: _token(iss="https://evil.example/realms/MiNET"), id="wrong-issuer"),
        pytest.param(lambda: _token(azp="other-client", aud="account"), id="other-client"),
        pytest.param(lambda: _token(typ="ID"), id="id-token"),
        pytest.param(lambda: _token(typ="Refresh"), id="refresh-token"),
        pytest.param(lambda: _token(key=_rsa_key("key-1")), id="forged-signature"),
        pytest.param(lambda: _token(key=jwk.JWK.generate(kty="oct", size=256, kid="key-1"), alg="HS256"), id="hmac"),
        pytest.param(lambda: "not.a.jwt", id="malformed"),
        pytest.param(lambda: "", id="empty"),
    ],
)
async def test_invalid_tokens_are_rejected(verifier, token):
    with pytest.raises(InvalidOIDCToken):
        await verifier.verify(token())


async def test_signing_keys_are_cached(verifier, keycloak):
    for _ in range(5):
        await verifier.verify(_token())

    assert keycloak.jwks_requests == 1


async def test_expired_cache_is_refreshed(verifier, keycloak, clock):
    await verifier.verify(_token())
    clock.now += 3601

    await verifier.verify(_token())

    assert keycloak.jwks_requests == 2


async def test_rotated_key_triggers_refresh(verifier, keycloak, clock):
    await verifier.verify(_token())
    # A key rotated less than one cooldown after the last download is only picked up once the cooldown ends.
    clock.now += 31
    keycloak.keys.append(ROTATED_KEY)

    claims = await verifier.verify(_token(key=ROTATED_KEY))

    assert claims["typ"] == "Bearer"
    assert keycloak.jwks_requests == 2


async def test_unknown_key_ids_do_not_hammer_keycloak(verifier, keycloak, clock):
    await verifier.verify(_token())
    clock.now += 31
    unknown_key = _rsa_key("made-up")

    for _ in range(10):
        with pytest.raises(InvalidOIDCToken):
            await verifier.verify(_token(key=unknown_key))

    assert keycloak.jwks_requests == 2


async def test_keycloak_down_without_cached_keys(verifier, keycloak):
    keycloak.up = False

    with pytest.raises(OidcProviderUnavailable):
        await verifier.verify(_token())


async def test_keycloak_down_keeps_expired_keys_for_one_more_ttl(verifier, keycloak, clock):
    await verifier.verify(_token())
    keycloak.up = False

    clock.now += 3601
    assert (await verifier.verify(_token()))["typ"] == "Bearer"

    clock.now += 3600
    with pytest.raises(OidcProviderUnavailable):
        await verifier.verify(_token())


async def test_discovery_issuer_mismatch_is_refused(clock):
    keycloak = FakeKeycloak(KEY, issuer="https://keycloak.example/auth/realms/MiNET")
    verifier = OidcTokenVerifier(
        ISSUER,
        CLIENT_ID,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(keycloak.handler)),
        clock=clock,
    )

    with pytest.raises(OidcProviderUnavailable):
        await verifier.verify(_token())
