import json
import pytest

from test.integration.resource import TEST_HEADERS, TEST_HEADERS_SAMPLE, base_url

from adh6.treasury.storage.models import AccountType

@pytest.fixture
def sample_account_type1():
    return AccountType(
        id=1,
        name='test1'
    )


@pytest.fixture
def sample_account_type2():
    return AccountType(
        id=2,
        name='test2'
    )


@pytest.fixture
def client(sample_account_type1, sample_account_type2, sample_member):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            sample_account_type1,
            sample_account_type2,
            sample_member
        )
        yield c
        close_db()


def test_account_type_filter_all_with_invalid_limit(client):
    r = client.get(
        '{}/account_type/?limit={}'.format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_account_type_filter_all_with_limit(client):
    r = client.get(
        '{}/account_type/?limit={}'.format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_account_type_filter_by_terms(client):
    r = client.get(
        "{}/account_type/?terms={}".format(base_url, "test"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 2


def test_account_type_filter_by_terms_one_result(client):
    r = client.get(
        "{}/account_type/?terms={}".format(base_url, "test1"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_account_type_filter_unauthorized(client):
    r = client.get(
        f"{base_url}/account_type/",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
