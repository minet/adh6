import pytest
import json
from test import SAMPLE_CLIENT

from test.integration.resource import TEST_HEADERS, TEST_HEADERS_API_KEY_ADMIN, TEST_HEADERS_SAMPLE, base_url as host_url


base_url = f"{host_url}/role/"


@pytest.fixture
def client(sample_member):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(sample_member)
        yield c
        close_db()


def test_role_search(client):
    r = client.get(
        f"{base_url}?auth=oidc",
        headers=TEST_HEADERS,
    )
    print(r.text)
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 7


def test_role_search_no_result(client):
    r = client.get(
        f"{base_url}?auth=oidc&id=minet",
        headers=TEST_HEADERS,
    )
    print(r.text)
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
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


def test_role_search_filter_unauthorized_admin(client):
    r = client.get(
        f"{base_url}?auth=oidc",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 401


def test_role_post(client):
    body = {
        "auth": "user",
        "identifier": SAMPLE_CLIENT,
        "roles": ["admin:write"]
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 201
    r = client.get(
        f"{base_url}?auth=user",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_role_post_multiple_roles(client):
    body = {
        "auth": "user",
        "identifier": SAMPLE_CLIENT,
        "roles": ["admin:write", "admin:read"]
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 201
    r = client.get(
        f"{base_url}?auth=user",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 2


def test_role_post_unknown_user(client):
    body = {
        "auth": "user",
        "identifier": "minet",
        "roles": ["admin:write"]
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_role_post_unknown_role(client):
    body = {
        "auth": "user",
        "identifier": SAMPLE_CLIENT,
        "roles": ["minet"]
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_role_post_unauthorized_user(client):
    body = {
        "auth": "user",
        "identifier": SAMPLE_CLIENT,
        "roles": ["admin:write"]
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_role_post_unauthorized_admin(client):
    body = {
        "auth": "user",
        "identifier": SAMPLE_CLIENT,
        "roles": ["admin:write"]
    }
    r = client.post(
        base_url,
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 401
