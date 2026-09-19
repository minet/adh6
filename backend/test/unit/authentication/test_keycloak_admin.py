import httpx
import pytest
from adh6.authentication.keycloak_admin import (
    KeycloakAdminClient,
    KeycloakAdminConfig,
    KeycloakAdminError,
    KeycloakPasswordPolicyError,
)


def config() -> KeycloakAdminConfig:
    return KeycloakAdminConfig(
        base_url="https://keycloak.example",
        realm="MiNET",
        client_id="adh6-service",
        client_secret="secret",
        action_lifespan_seconds=900,
        timeout_seconds=5,
    )


@pytest.mark.asyncio
async def test_sends_update_password_action_to_exact_user():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        if request.method == "GET":
            assert request.url.params["username"] == "alice"
            assert request.url.params["exact"] == "true"
            return httpx.Response(200, json=[{"id": "user-id", "username": "alice"}])
        assert request.url.params["lifespan"] == "900"
        assert request.content == b'["UPDATE_PASSWORD"]'
        return httpx.Response(204)

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))
    await client.send_update_password_email("alice")

    assert [request.method for request in requests] == ["POST", "GET", "PUT"]
    assert all(request.headers.get("authorization") == "Bearer access-token" for request in requests[1:])


@pytest.mark.asyncio
async def test_refuses_ambiguous_user_lookup():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        return httpx.Response(
            200,
            json=[
                {"id": "first", "username": "alice"},
                {"id": "second", "username": "alice"},
            ],
        )

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))
    with pytest.raises(KeycloakAdminError, match="exactly one"):
        await client.send_update_password_email("alice")


@pytest.mark.asyncio
async def test_does_not_expose_keycloak_error_body():
    client = KeycloakAdminClient(
        config(),
        transport=httpx.MockTransport(lambda request: httpx.Response(401, text="sensitive upstream details")),
    )

    with pytest.raises(KeycloakAdminError, match="authentication failed") as error:
        await client.send_update_password_email("alice")

    assert "sensitive" not in str(error.value)


@pytest.mark.asyncio
async def test_admin_password_is_forwarded_to_keycloak():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        if request.method == "GET":
            return httpx.Response(200, json=[{"id": "user-id", "username": "alice"}])
        return httpx.Response(204)

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))
    await client.reset_password("alice", "ValidPassword1!")

    reset_request = requests[-1]
    assert reset_request.url.path.endswith("/users/user-id/reset-password")
    assert reset_request.content == b'{"type":"password","value":"ValidPassword1!","temporary":false}'


@pytest.mark.asyncio
async def test_get_password_policy_returns_user_facing_rules():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        assert request.url.path == "/admin/realms/MiNET"
        return httpx.Response(
            200,
            json={
                "passwordPolicy": (
                    "length(12) and digits(2) and notUsername and "
                    "regexPattern(^[A-Z](foo and bar)[0-9]+$) and hashAlgorithm(argon2)"
                )
            },
        )

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))

    assert await client.get_password_policy() == [
        {"name": "length", "value": "12"},
        {"name": "digits", "value": "2"},
        {"name": "notUsername", "value": ""},
        {"name": "regexPattern", "value": "^[A-Z](foo and bar)[0-9]+$"},
    ]
    assert [request.method for request in requests] == ["POST", "GET"]
    assert requests[-1].headers["authorization"] == "Bearer access-token"


@pytest.mark.asyncio
async def test_get_password_policy_accepts_an_unconfigured_realm():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        return httpx.Response(200, json={"realm": "MiNET"})

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))

    assert await client.get_password_policy() == []


@pytest.mark.asyncio
async def test_get_password_policy_reports_a_controlled_upstream_error():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        return httpx.Response(403, text="sensitive upstream details")

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))

    with pytest.raises(KeycloakAdminError, match="policy lookup failed") as error:
        await client.get_password_policy()

    assert "sensitive" not in str(error.value)


@pytest.mark.asyncio
async def test_password_policy_rejection_exposes_its_safe_description():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        if request.method == "GET":
            return httpx.Response(200, json=[{"id": "user-id", "username": "alice"}])
        return httpx.Response(
            400,
            json={
                "error": "invalidPasswordMinLengthMessage",
                "error_description": "Invalid password: minimum length 12.",
            },
        )

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))
    with pytest.raises(KeycloakPasswordPolicyError, match="minimum length 12"):
        await client.reset_password("alice", "weak")


@pytest.mark.asyncio
async def test_password_policy_rejection_does_not_expose_unrecognized_error_details():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json={"access_token": "access-token"})
        if request.method == "GET":
            return httpx.Response(200, json=[{"id": "user-id", "username": "alice"}])
        return httpx.Response(
            400,
            json={"error": "unexpectedError", "error_description": "sensitive upstream details"},
        )

    client = KeycloakAdminClient(config(), transport=httpx.MockTransport(handler))
    with pytest.raises(KeycloakPasswordPolicyError, match="password policy") as error:
        await client.reset_password("alice", "weak")

    assert "sensitive" not in str(error.value)
