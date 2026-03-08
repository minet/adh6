import json

import pytest

from test import SAMPLE_CLIENT, TESTING_CLIENT
from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_API_KEY_ADMIN,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/api_keys/"


@pytest.fixture
def client(_test_client, sample_member, sample_member_admin):
    """Add test-specific fixtures to the transaction."""
    from .conftest import (
        add_test_fixtures,
        cleanup_test_data,
        api_key_admin,
        api_key_admin_read_roles,
        api_key_admin_write_roles,
        api_key_admin_network_read_roles,
        api_key_admin_network_write_roles,
    )

    add_test_fixtures(
        [
            sample_member,
            sample_member_admin,
            api_key_admin(),
            api_key_admin_read_roles(),
            api_key_admin_write_roles(),
            api_key_admin_network_read_roles(),
            api_key_admin_network_write_roles(),
        ]
    )

    yield _test_client

    cleanup_test_data()


def test_api_key_search(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_api_key_search_login(client):
    r = client.get(
        f"{base_url}?login={TESTING_CLIENT}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_api_key_search_unknown_login(client):
    r = client.get(
        f"{base_url}?login=minet",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_api_key_search_unauthorized_user(client):
    r = client.get(
        f"{base_url}?login={TESTING_CLIENT}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_api_key_search_unauthorized_admin(client):
    r = client.get(
        f"{base_url}?login={TESTING_CLIENT}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 401


def test_api_key_post_role(client):
    body = {"login": TESTING_CLIENT, "roles": ["admin:read"]}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 36


def test_api_key_post_no_role(client):
    body = {"login": TESTING_CLIENT, "roles": []}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_api_key_post_unknown_user(client):
    body = {"login": "minet", "roles": ["admin:read"]}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_api_key_post_unknown_role(client):
    body = {"login": "minet", "roles": ["admin:rea"]}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_api_key_post_unauthorized_user(client):
    body = {"login": TESTING_CLIENT, "roles": ["admin:read"]}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS_SAMPLE},
    )
    assert r.status_code == 403


def test_api_key_post_unauthorized_admin(client):
    body = {"login": TESTING_CLIENT, "roles": ["admin:read"]}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS_API_KEY_ADMIN},
    )
    assert r.status_code == 401


def test_api_key_delete(client):
    body = {"login": SAMPLE_CLIENT, "roles": ["admin:read"]}
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )

    r = client.get(
        f"{base_url}?login={SAMPLE_CLIENT}",
        headers=TEST_HEADERS,
    )
    result = json.loads(r.content.decode("utf-8"))

    r = client.delete(
        f"{base_url}{result[0]['id']}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204


def test_api_key_delete_unknown(client):
    r = client.delete(
        f"{base_url}{4242}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_api_key_delete_unauthorized_user(client):
    r = client.delete(
        f"{base_url}{4242}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_api_key_delete_unauthorized_admin(client):
    r = client.delete(
        f"{base_url}{4242}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 401
