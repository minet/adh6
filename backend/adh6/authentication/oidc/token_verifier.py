# pyright: reportUnknownMemberType=false

"""Local verification of Keycloak access tokens.

Requests never contact Keycloak: each worker caches the realm's public signing keys and only
re-downloads them when they expire or when a token is signed by a key it does not know yet
(Keycloak key rotation).
"""

import asyncio
import json
import logging
import math
import time
from collections.abc import Callable
from typing import Any, cast

import httpx
from jwcrypto import jwk, jws, jwt
from jwcrypto.common import JWException

from adh6.config.configuration import settings

_log = logging.getLogger(__name__)

# Asymmetric algorithms only: accepting HS* would let anyone holding a public key forge tokens.
_ALLOWED_ALGORITHMS = ["RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512", "EdDSA"]


class InvalidOIDCToken(ValueError):
    """The bearer token is malformed, invalid, or not intended for ADH6."""


class OidcProviderUnavailable(RuntimeError):
    """The signing keys cannot be obtained, so no token can be verified."""


class OidcTokenVerifier:
    def __init__(
        self,
        issuer: str,
        client_id: str,
        *,
        http_client: httpx.AsyncClient,
        cache_ttl_seconds: float = 3600,
        refresh_cooldown_seconds: float = 30,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._issuer = issuer.rstrip("/")
        self._client_id = client_id
        self._http = http_client
        self._cache_ttl = cache_ttl_seconds
        self._refresh_cooldown = refresh_cooldown_seconds
        self._clock = clock
        self._keys: jwk.JWKSet | None = None
        self._fetched_at = -math.inf
        self._last_refresh_attempt = -math.inf
        self._lock = asyncio.Lock()

    async def verify(self, token: str) -> dict[str, Any]:
        """Return the claims of a valid ADH6 access token, or raise InvalidOIDCToken."""
        keys = await self._signing_keys(_key_id(token))
        try:
            verified = jwt.JWT(
                jwt=token,
                key=keys,
                algs=_ALLOWED_ALGORITHMS,
                check_claims={"exp": None, "iss": self._issuer},
                expected_type="JWS",
            )
            claims = cast(dict[str, Any], json.loads(verified.claims))
        except (JWException, ValueError) as exc:
            raise InvalidOIDCToken(f"validation failed: {exc}") from exc

        # Keycloak also signs ID tokens ("ID") and refresh tokens ("Refresh") with the same keys.
        if claims.get("typ") != "Bearer":
            raise InvalidOIDCToken("not an access token")
        audience = claims.get("aud", [])
        if isinstance(audience, str):
            audience = [audience]
        if claims.get("azp") != self._client_id and self._client_id not in audience:
            raise InvalidOIDCToken(f"token was not issued for client '{self._client_id}'")
        return claims

    async def close(self) -> None:
        await self._http.aclose()

    def _has_fresh_key(self, key_id: str | None) -> bool:
        return (
            self._keys is not None
            and self._clock() - self._fetched_at < self._cache_ttl
            and (key_id is None or self._keys.get_key(key_id) is not None)
        )

    async def _signing_keys(self, key_id: str | None) -> jwk.JWKSet:
        if self._has_fresh_key(key_id):
            return self._keys  # type: ignore[return-value]

        async with self._lock:
            # Another request may have refreshed the keys while this one was waiting.
            if self._has_fresh_key(key_id):
                return self._keys  # type: ignore[return-value]

            now = self._clock()
            # The cooldown stops tokens with made-up key ids from hammering Keycloak.
            if now - self._last_refresh_attempt >= self._refresh_cooldown:
                self._last_refresh_attempt = now
                try:
                    self._keys = await self._fetch_keys()
                    self._fetched_at = now
                except OidcProviderUnavailable:
                    _log.warning("Cannot refresh OIDC signing keys, keeping the cached ones", exc_info=True)

            # Expired keys stay usable for one more TTL, so a short Keycloak outage does not log everyone out.
            if self._keys is None or now - self._fetched_at >= 2 * self._cache_ttl:
                raise OidcProviderUnavailable("no usable OIDC signing keys")
            if key_id is not None and self._keys.get_key(key_id) is None:
                raise InvalidOIDCToken(f"unknown signing key '{key_id}'")
            return self._keys

    async def _fetch_keys(self) -> jwk.JWKSet:
        try:
            discovery = (await self._http.get(f"{self._issuer}/.well-known/openid-configuration")).raise_for_status()
            metadata = discovery.json()
            if metadata.get("issuer") != self._issuer:
                raise OidcProviderUnavailable(f"discovery issuer {metadata.get('issuer')!r} != {self._issuer!r}")
            certs = (await self._http.get(metadata["jwks_uri"])).raise_for_status().json()
            # Keycloak publishes an encryption key next to the signing ones.
            signing_keys = [key for key in certs["keys"] if key.get("use", "sig") == "sig"]
            if not signing_keys:
                raise OidcProviderUnavailable("the realm publishes no signing key")
            key_set = jwk.JWKSet()
            key_set.import_keyset(json.dumps({"keys": signing_keys}))
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, JWException) as exc:
            raise OidcProviderUnavailable(f"cannot load OIDC signing keys: {exc}") from exc
        _log.info("Loaded %d OIDC signing keys", len(signing_keys))
        return key_set


def _key_id(token: str) -> str | None:
    try:
        parsed = jws.JWS()
        parsed.deserialize(token)
    except (JWException, ValueError, TypeError) as exc:
        raise InvalidOIDCToken("malformed token") from exc
    header = cast(dict[str, Any], parsed.jose_header)
    key_id = header.get("kid")
    return key_id if isinstance(key_id, str) else None


_process_verifier: OidcTokenVerifier | None = None


def get_oidc_token_verifier() -> OidcTokenVerifier:
    """Return this worker's verifier, building it from the settings on first use."""
    global _process_verifier
    if _process_verifier is None:
        if not settings.oidc_issuer or not settings.oidc_client_id:
            raise ValueError("OIDC_ISSUER and OIDC_CLIENT_ID must be set")
        _process_verifier = OidcTokenVerifier(
            settings.oidc_issuer,
            settings.oidc_client_id,
            http_client=httpx.AsyncClient(timeout=settings.oidc_http_timeout_seconds),
            cache_ttl_seconds=settings.oidc_jwks_cache_ttl_seconds,
            refresh_cooldown_seconds=settings.oidc_jwks_refresh_cooldown_seconds,
        )
    return _process_verifier


async def close_oidc_token_verifier() -> None:
    global _process_verifier
    verifier, _process_verifier = _process_verifier, None
    if verifier is not None:
        await verifier.close()
