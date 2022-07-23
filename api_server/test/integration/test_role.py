import pytest
import json
from test import SAMPLE_CLIENT

from test.integration.resource import TEST_HEADERS, TEST_HEADERS_API_KEY_ADMIN, TEST_HEADERS_SAMPLE, base_url

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
        f"{base_url}/role/",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 8


def test_role_search_filter_unknown_authentication(client):
    r = client.get(
        f"{base_url}/role/?filter[authentication]=minet",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_role_search_filter_unknown_role(client):
    r = client.get(
        f"{base_url}/role/?filter[role]=minet",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_role_search_filter_unauthorized_user(client):
    r = client.get(
        f"{base_url}/role/",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_role_search_filter_unauthorized_admin(client):
    r = client.get(
        f"{base_url}/role/",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 401


def test_role_post(client):
    body = {
        "login": SAMPLE_CLIENT,
        "role": "admin:write"
    }
    r = client.post(
        f"{base_url}/role/",
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 201


def test_role_post_unknown_user(client):
    body = {
        "login": "minet",
        "role": "admin:write"
    }
    r = client.post(
        f"{base_url}/role/",
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_role_post_unknown_role(client):
    body = {
        "login": SAMPLE_CLIENT,
        "role": "minet"
    }
    r = client.post(
        f"{base_url}/role/",
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_role_post_unauthorized_user(client):
    body = {
        "login": SAMPLE_CLIENT,
        "role": "admin:write"
    }
    r = client.post(
        f"{base_url}/role/",
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_role_post_unauthorized_admin(client):
    body = {
        "login": SAMPLE_CLIENT,
        "role": "admin:write"
    }
    r = client.post(
        f"{base_url}/role/",
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 401
