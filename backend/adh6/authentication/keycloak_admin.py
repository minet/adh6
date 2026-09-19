"""Minimal Keycloak Admin API client for password lifecycle operations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import cast

import httpx

from adh6.config.configuration import settings


class KeycloakAdminError(RuntimeError):
    """Keycloak could not accept a password-action request."""


class KeycloakPasswordPolicyError(KeycloakAdminError):
    """The proposed credential does not satisfy Keycloak's password policy."""


_GENERIC_CREDENTIAL_POLICY_ERROR = "Password rejected by Keycloak's password policy"

# Only descriptions attached to known password-policy errors are safe and useful
# to expose. Other Keycloak 400 responses may contain implementation details.
_PASSWORD_POLICY_ERROR_CODES = frozenset(
    {
        "invalidPasswordBlacklistedMessage",
        "invalidPasswordGenericMessage",
        "invalidPasswordHistoryMessage",
        "invalidPasswordMaxLengthMessage",
        "invalidPasswordMinDigitsMessage",
        "invalidPasswordMinLengthMessage",
        "invalidPasswordMinLowerCaseCharsMessage",
        "invalidPasswordMinSpecialCharsMessage",
        "invalidPasswordMinUpperCaseCharsMessage",
        "invalidPasswordNotContainsUsernameMessage",
        "invalidPasswordNotEmailMessage",
        "invalidPasswordNotUsernameMessage",
        "invalidPasswordRegexPatternMessage",
    }
)

_INTERNAL_PASSWORD_POLICY_PROVIDERS = frozenset(
    {
        "argon2Iterations",
        "argon2Memory",
        "argon2Parallelism",
        "hashAlgorithm",
        "hashIterations",
        "maxAuthAge",
        "recoveryCodesWarningThreshold",
    }
)


def _split_password_policy(policy: str) -> list[str]:
    """Split Keycloak's ``provider(value) and ...`` representation safely."""
    clauses: list[str] = []
    clause_start = 0
    depth = 0
    escaped = False
    in_character_class = False
    index = 0

    while index < len(policy):
        character = policy[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "[":
            in_character_class = True
        elif character == "]":
            in_character_class = False
        elif not in_character_class:
            if character == "(":
                depth += 1
            elif character == ")" and depth:
                depth -= 1
            elif depth == 0 and policy.startswith(" and ", index):
                clauses.append(policy[clause_start:index].strip())
                index += len(" and ")
                clause_start = index
                continue
        index += 1

    clauses.append(policy[clause_start:].strip())
    return [clause for clause in clauses if clause]


def _parse_password_policy(policy: str) -> list[dict[str, str]]:
    """Turn the realm policy into user-relevant provider/value pairs."""
    rules: list[dict[str, str]] = []
    for clause in _split_password_policy(policy):
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*)(?:\((.*)\))?", clause, flags=re.DOTALL)
        if match is None:
            rules.append({"name": clause, "value": ""})
            continue

        name, value = match.groups()
        if name not in _INTERNAL_PASSWORD_POLICY_PROVIDERS:
            rules.append({"name": name, "value": value or ""})
    return rules


def _password_policy_error_message(response: httpx.Response) -> str:
    """Return Keycloak's user-facing policy description, if recognized."""
    try:
        body = response.json()
    except (ValueError, TypeError):
        return _GENERIC_CREDENTIAL_POLICY_ERROR

    if not isinstance(body, dict) or body.get("error") not in _PASSWORD_POLICY_ERROR_CODES:
        return _GENERIC_CREDENTIAL_POLICY_ERROR

    description = body.get("error_description")
    if isinstance(description, str) and 0 < len(description) <= 500:
        return description
    return _GENERIC_CREDENTIAL_POLICY_ERROR


@dataclass(frozen=True)
class KeycloakAdminConfig:
    base_url: str
    realm: str
    client_id: str
    client_secret: str
    action_lifespan_seconds: int
    timeout_seconds: float


class KeycloakAdminClient:
    """Use a narrowly-scoped service account for password lifecycle operations."""

    def __init__(self, config: KeycloakAdminConfig, transport: httpx.AsyncBaseTransport | None = None):
        self.config = config
        self.transport = transport

    async def send_update_password_email(self, username: str) -> None:
        try:
            await self._send_update_password_email(username)
        except (httpx.HTTPError, ValueError, TypeError) as error:
            raise KeycloakAdminError("Keycloak is unavailable or returned an invalid response") from error

    async def reset_password(self, username: str, password: str) -> None:
        """Forward an admin-selected password to Keycloak without storing or hashing it in ADH6."""
        try:
            await self._reset_password(username, password)
        except (httpx.HTTPError, ValueError, TypeError) as error:
            raise KeycloakAdminError("Keycloak is unavailable or returned an invalid response") from error

    async def get_password_policy(self) -> list[dict[str, str]]:
        """Return the realm's user-facing password constraints."""
        try:
            return await self._get_password_policy()
        except (httpx.HTTPError, ValueError, TypeError) as error:
            raise KeycloakAdminError("Keycloak is unavailable or returned an invalid response") from error

    async def _send_update_password_email(self, username: str) -> None:
        base_url = self.config.base_url.rstrip("/")
        realm = self.config.realm
        timeout = httpx.Timeout(self.config.timeout_seconds)
        async with httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=self.transport) as client:
            headers, user_id = await self._authenticate_and_find_user(client, username)

            action_response = await client.put(
                f"/admin/realms/{realm}/users/{user_id}/execute-actions-email",
                params={"lifespan": self.config.action_lifespan_seconds},
                json=["UPDATE_PASSWORD"],
                headers=headers,
            )
            if action_response.status_code != httpx.codes.NO_CONTENT:
                raise KeycloakAdminError("Keycloak refused the password-action email")

    async def _reset_password(self, username: str, password: str) -> None:
        base_url = self.config.base_url.rstrip("/")
        realm = self.config.realm
        timeout = httpx.Timeout(self.config.timeout_seconds)
        async with httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=self.transport) as client:
            headers, user_id = await self._authenticate_and_find_user(client, username)
            response = await client.put(
                f"/admin/realms/{realm}/users/{user_id}/reset-password",
                json={"type": "password", "value": password, "temporary": False},
                headers=headers,
            )
            if response.status_code == httpx.codes.BAD_REQUEST:
                raise KeycloakPasswordPolicyError(_password_policy_error_message(response))
            if response.status_code != httpx.codes.NO_CONTENT:
                raise KeycloakAdminError("Keycloak refused the password update")

    async def _get_password_policy(self) -> list[dict[str, str]]:
        base_url = self.config.base_url.rstrip("/")
        realm = self.config.realm
        timeout = httpx.Timeout(self.config.timeout_seconds)
        async with httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=self.transport) as client:
            headers = await self._authenticate(client)
            response = await client.get(f"/admin/realms/{realm}", headers=headers)
            if response.status_code != httpx.codes.OK:
                raise KeycloakAdminError("Keycloak password policy lookup failed")

            body = response.json()
            if not isinstance(body, dict):
                raise KeycloakAdminError("Keycloak returned an invalid password policy")

            policy = body.get("passwordPolicy")
            if policy is None:
                return []
            if not isinstance(policy, str):
                raise KeycloakAdminError("Keycloak returned an invalid password policy")
            return _parse_password_policy(policy)

    async def _authenticate_and_find_user(self, client: httpx.AsyncClient, username: str) -> tuple[dict[str, str], str]:
        headers = await self._authenticate(client)
        realm = self.config.realm
        users_response = await client.get(
            f"/admin/realms/{realm}/users",
            params={"username": username, "exact": "true", "max": 2},
            headers=headers,
        )
        if users_response.status_code != httpx.codes.OK:
            raise KeycloakAdminError("Keycloak user lookup failed")

        users = users_response.json()
        matches = [user for user in users if user.get("username") == username and isinstance(user.get("id"), str)]
        if len(matches) != 1:
            raise KeycloakAdminError("The member does not map to exactly one Keycloak user")
        return headers, matches[0]["id"]

    async def _authenticate(self, client: httpx.AsyncClient) -> dict[str, str]:
        realm = self.config.realm
        token_response = await client.post(
            f"/realms/{realm}/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            },
        )
        if token_response.status_code != httpx.codes.OK:
            raise KeycloakAdminError("Keycloak service-account authentication failed")

        access_token = token_response.json().get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise KeycloakAdminError("Keycloak returned an invalid service-account token")
        return {"Authorization": f"Bearer {access_token}"}


def get_keycloak_admin_client() -> KeycloakAdminClient:
    required = {
        "KEYCLOAK_ADMIN_URL": settings.keycloak_admin_url,
        "KEYCLOAK_ADMIN_CLIENT_ID": settings.keycloak_admin_client_id,
        "KEYCLOAK_ADMIN_CLIENT_SECRET": settings.keycloak_admin_client_secret,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise KeycloakAdminError(f"Missing Keycloak administration configuration: {', '.join(missing)}")

    base_url = cast(str, settings.keycloak_admin_url)
    client_id = cast(str, settings.keycloak_admin_client_id)
    client_secret = cast(str, settings.keycloak_admin_client_secret)

    return KeycloakAdminClient(
        KeycloakAdminConfig(
            base_url=base_url,
            realm=settings.keycloak_admin_realm,
            client_id=client_id,
            client_secret=client_secret,
            action_lifespan_seconds=settings.keycloak_password_action_lifespan_seconds,
            timeout_seconds=settings.oidc_http_timeout_seconds,
        )
    )
