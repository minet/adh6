import json

import pytest

from test import SAMPLE_CLIENT
from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_API_KEY_ADMIN,
    TEST_HEADERS_API_KEY_USER,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/role/"


@pytest.fixture
def client(_test_client, sample_member):
    """Add test-specific fixtures to the transaction."""
    from .conftest import (
        add_test_fixtures,
        api_key_fixtures,
        cleanup_test_data,
        oidc_admin_prod_role,
        oidc_admin_read_role,
        oidc_admin_write_role,
        oidc_treasurer_read_role,
        oidc_treasurer_write_role,
        oidc_network_read_role,
        oidc_network_write_role,
    )

    oidc_roles = [
        oidc_admin_prod_role(),
        oidc_admin_read_role(),
        oidc_admin_write_role(),
        oidc_treasurer_read_role(),
        oidc_treasurer_write_role(),
        oidc_network_read_role(),
        oidc_network_write_role(),
    ]
    add_test_fixtures([*api_key_fixtures(), *oidc_roles, sample_member])

    yield _test_client

    cleanup_test_data()


def test_role_search(client):
    r = client.get(
        f"{base_url}?auth=oidc",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 7


def test_role_search_no_result(client):
    r = client.get(
        f"{base_url}?auth=oidc&id=minet",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 0


def test_role_search_filter_unknown_authentication(client):
    r = client.get(
        f"{base_url}?auth=minet",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_role_search_filter_unauthorized_user(client):
    r = client.get(
        f"{base_url}?auth=oidc",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_role_search_filter_unauthorized_api_key(client):
    r = client.get(
        f"{base_url}?auth=oidc",
        headers=TEST_HEADERS_API_KEY_USER,
    )
    assert r.status_code == 401


def test_role_search_filter_no_result_authorized_api_key_admin(client):
    r = client.get(
        f"{base_url}?auth=user&id={SAMPLE_CLIENT}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 0


def test_role_search_filter_with_identifier_authorized_api_key_admin(client):
    body = {"auth": "user", "identifier": SAMPLE_CLIENT, "roles": ["admin:write"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201
    r = client.get(
        f"{base_url}?auth=user&id={SAMPLE_CLIENT}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_role_search_filter_no_identifier_authorized_api_key_admin(client):
    body = {"auth": "user", "identifier": SAMPLE_CLIENT, "roles": ["admin:write"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201
    r = client.get(
        f"{base_url}?auth=user",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_role_post(client):
    body = {"auth": "user", "identifier": SAMPLE_CLIENT, "roles": ["admin:write"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201
    r = client.get(
        f"{base_url}?auth=user",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_role_post_multiple_roles(client):
    body = {
        "auth": "user",
        "identifier": SAMPLE_CLIENT,
        "roles": ["admin:write", "admin:read"],
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201
    r = client.get(
        f"{base_url}?auth=user",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 2


def test_role_post_unknown_user(client):
    body = {"auth": "user", "identifier": "minet", "roles": ["admin:write"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_role_post_unknown_role(client):
    body = {"auth": "user", "identifier": SAMPLE_CLIENT, "roles": ["minet"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_role_post_unauthorized_user(client):
    body = {"auth": "user", "identifier": SAMPLE_CLIENT, "roles": ["admin:write"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS_SAMPLE},
    )
    assert r.status_code == 403


def test_role_post_unauthorized_api_key_admin(client):
    body = {"auth": "user", "identifier": SAMPLE_CLIENT, "roles": ["admin:write"]}
    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS_API_KEY_ADMIN},
    )
    assert r.status_code == 401


def test_role_delete(client):
    r = client.delete(
        f"{base_url}{1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204


def test_role_delete_unknown_mapping(client):
    r = client.delete(
        f"{base_url}{4242}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_role_delete_unauthorized_user(client):
    r = client.delete(
        f"{base_url}{1}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_role_delete_unauthorized_api_key_user(client):
    r = client.delete(
        f"{base_url}{1}",
        headers=TEST_HEADERS_API_KEY_USER,
    )
    assert r.status_code == 401


def test_role_delete_authorized_api_key_admin(client):
    r = client.delete(
        f"{base_url}{1}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 204
