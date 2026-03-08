import pytest

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_API_KEY_ADMIN,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/health"


@pytest.fixture
def client(_test_client):
    """Client fixture for health tests."""
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    add_test_fixtures(api_key_fixtures())

    yield _test_client

    cleanup_test_data()


def test_good_health(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200


def test_good_health_api_key(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200


def test_good_health_unauthorized(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_good_health_invalid_api_key(client):
    r = client.get(
        f"{base_url}",
        headers={"X-API-KEY": "invalid-api-key"},
    )
    assert r.status_code == 401
