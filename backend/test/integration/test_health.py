import pytest

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/health"


@pytest.fixture
async def client(_test_client):
    """Client fixture for health tests."""
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures(api_key_fixtures())

    yield _test_client

    await cleanup_test_data()


def test_health_is_public(client):
    r = client.get(f"{base_url}")
    assert r.status_code == 200
    assert r.json() == {"healthy": True}


def test_health_with_admin_token(client):
    r = client.get(f"{base_url}", headers=TEST_HEADERS)
    assert r.status_code == 200


def test_health_with_unprivileged_token(client):
    r = client.get(f"{base_url}", headers=TEST_HEADERS_SAMPLE)
    assert r.status_code == 200


def test_health_invalid_api_key(client):
    # Credentials, when sent, are still validated by the global auth dependency
    r = client.get(f"{base_url}", headers={"X-API-KEY": "invalid-api-key"})
    assert r.status_code == 401
