"""Authorization-code flow with PKCE, run by the backend so the browser never handles a token."""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import urlencode

import httpx

from adh6.authentication.oidc.token_verifier import OidcProviderUnavailable
from adh6.config.configuration import settings

TRANSIENT_STATUSES = frozenset({408, 425, 429})


class OidcExchangeRejected(ValueError):
    """Keycloak refused the authorization code or the refresh token."""


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    expires_in: int
    refresh_token: str | None = None
    refresh_expires_in: int = 0
    id_token: str | None = None


class OidcClient:
    def __init__(
        self,
        issuer: str,
        client_id: str,
        redirect_uri: str,
        *,
        http_client: httpx.AsyncClient,
        scope: str = "openid",
        client_secret: str | None = None,
        metadata_ttl_seconds: float = 3600,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._issuer = issuer.rstrip("/")
        self._client_id = client_id
        self._redirect_uri = redirect_uri
        self._http = http_client
        self._scope = scope
        self._client_secret = client_secret
        self._metadata_ttl = metadata_ttl_seconds
        self._clock = clock
        self._metadata: dict[str, Any] | None = None
        self._fetched_at: float = float("-inf")
        self._lock = asyncio.Lock()

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    async def authorization_url(self, *, state: str, nonce: str, code_challenge: str) -> str:
        endpoint = (await self._endpoints())["authorization_endpoint"]
        query = urlencode(
            {
                "client_id": self._client_id,
                "response_type": "code",
                "scope": self._scope,
                "redirect_uri": self._redirect_uri,
                "state": state,
                "nonce": nonce,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        )
        return f"{endpoint}?{query}"

    async def exchange_code(self, code: str, code_verifier: str) -> TokenResponse:
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self._redirect_uri,
                "code_verifier": code_verifier,
            }
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        return await self._token_request({"grant_type": "refresh_token", "refresh_token": refresh_token})

    async def end_session_url(self, *, post_logout_redirect_uri: str, id_token_hint: str | None = None) -> str:
        """Where to send the browser to end the Keycloak session as well."""
        endpoint = (await self._endpoints())["end_session_endpoint"]
        params = {"client_id": self._client_id, "post_logout_redirect_uri": post_logout_redirect_uri}
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        return f"{endpoint}?{urlencode(params)}"

    async def close(self) -> None:
        await self._http.aclose()

    async def _token_request(self, form: dict[str, str]) -> TokenResponse:
        endpoint = (await self._endpoints())["token_endpoint"]
        payload = {"client_id": self._client_id, **form}
        if self._client_secret:
            payload["client_secret"] = self._client_secret
        try:
            response = await self._http.post(endpoint, data=payload)
        except httpx.HTTPError as exc:
            raise OidcProviderUnavailable(f"token endpoint unreachable: {exc}") from exc

        if response.is_server_error or response.status_code in TRANSIENT_STATUSES:
            raise OidcProviderUnavailable(f"token endpoint answered {response.status_code}")
        if response.is_error:
            raise OidcExchangeRejected(f"token endpoint answered {response.status_code}")
        try:
            body = response.json()
            return TokenResponse(
                access_token=str(body["access_token"]),
                expires_in=int(body.get("expires_in", 0)),
                refresh_token=body.get("refresh_token"),
                refresh_expires_in=int(body.get("refresh_expires_in", 0)),
                id_token=body.get("id_token"),
            )
        except (ValueError, KeyError, TypeError) as exc:
            raise OidcExchangeRejected("malformed token response") from exc

    async def _endpoints(self) -> dict[str, Any]:
        if self._metadata is not None and self._clock() - self._fetched_at < self._metadata_ttl:
            return self._metadata
        async with self._lock:
            if self._metadata is not None and self._clock() - self._fetched_at < self._metadata_ttl:
                return self._metadata
            try:
                response = (await self._http.get(f"{self._issuer}/.well-known/openid-configuration")).raise_for_status()
                document: object = response.json()
                if not isinstance(document, dict):
                    raise OidcProviderUnavailable("discovery document is not an object")
                metadata = cast(dict[str, Any], document)
                if metadata.get("issuer") != self._issuer:
                    raise OidcProviderUnavailable(f"discovery issuer {metadata.get('issuer')!r} != {self._issuer!r}")
                for endpoint in ("authorization_endpoint", "token_endpoint", "end_session_endpoint"):
                    if not isinstance(metadata.get(endpoint), str):
                        raise OidcProviderUnavailable(f"discovery lacks {endpoint}")
            except (httpx.HTTPError, ValueError) as exc:
                raise OidcProviderUnavailable(f"cannot load OIDC metadata: {exc}") from exc
            self._metadata = metadata
            self._fetched_at = self._clock()
            return metadata


_process_client: OidcClient | None = None


def get_oidc_client() -> OidcClient:
    """Return this worker's client, building it from the settings on first use."""
    global _process_client
    if _process_client is None:
        if not settings.oidc_issuer or not settings.oidc_client_id:
            raise ValueError("OIDC_ISSUER and OIDC_CLIENT_ID must be set")
        redirect_uri = settings.oidc_redirect_uri or f"https://{settings.adh6_url}/api/auth/callback"
        _process_client = OidcClient(
            settings.oidc_issuer,
            settings.oidc_client_id,
            redirect_uri,
            http_client=httpx.AsyncClient(timeout=settings.oidc_http_timeout_seconds),
            scope=settings.oidc_scope,
            client_secret=settings.oidc_client_secret.get_secret_value() if settings.oidc_client_secret else None,
        )
    return _process_client


async def close_oidc_client() -> None:
    global _process_client
    client, _process_client = _process_client, None
    if client is not None:
        await client.close()
