import json

import pytest
from adh6.treasury.storage.models import Product

from test.integration.resource import TEST_HEADERS, base_url as host_url

base_url = f"{host_url}/product/"


@pytest.fixture
def sample_product():
    yield Product(name="test", buying_price=2.0, selling_price=2.0)


@pytest.fixture
async def client(_test_client, sample_product):
    from .conftest import add_test_fixtures, cleanup_test_data

    # Add test data
    await add_test_fixtures([sample_product])

    yield _test_client

    # Cleanup after test
    await cleanup_test_data()


def test_product_get_all_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_product_get_all_limit(client):
    r = client.get(
        f"{base_url}?limit={0}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert len(t) == 0


def test_product_get_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert t
    assert len(t) == 1


def test_product_get_existant_product(client):
    r = client.get(
        f"{base_url}{1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8"))


def test_product_get_non_existant_product(client):
    r = client.get(
        f"{base_url}{100000}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_product_filter_by_term_name(client):
    r = client.get(
        f"{base_url}?terms={'te'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result
    assert len(result) == 1


def test_product_filter_by_unknown_term_name(client):
    r = client.get(
        f"{base_url}?terms={'azertyuiop'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 0
