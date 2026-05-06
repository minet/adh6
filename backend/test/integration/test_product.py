import json

import pytest
from adh6.treasury.storage.models import Product

from test.integration.resource import TEST_HEADERS_API_KEY_ADMIN, base_url as host_url

base_url = f"{host_url}/product/"


@pytest.fixture
def sample_product():
    yield Product(id=1, name="test", buying_price=2.0, selling_price=2.0)


@pytest.fixture
async def client(_test_client, sample_product, sample_member_admin):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures([sample_member_admin, sample_product, *api_key_fixtures()])

    yield _test_client

    await cleanup_test_data()


@pytest.fixture
async def buy_client(
    _test_client,
    sample_vlan,
    sample_room1,
    sample_member,
    sample_member_admin,
    sample_payment_method,
    sample_product,
):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_vlan,
            sample_room1,
            sample_member_admin,
            sample_member,
            sample_payment_method,
            sample_product,
            *api_key_fixtures(),
        ]
    )

    yield _test_client

    await cleanup_test_data()


def test_product_get_all_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 400


def test_product_get_all_limit(client):
    r = client.get(
        f"{base_url}?limit={0}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert len(t) == 0


def test_product_get_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert t
    assert len(t) == 1


def test_product_get_existant_product(client):
    r = client.get(
        f"{base_url}{1}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8"))


def test_product_get_non_existant_product(client):
    r = client.get(
        f"{base_url}{100000}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 404


def test_product_filter_by_term_name(client):
    r = client.get(
        f"{base_url}?terms={'te'}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result
    assert len(result) == 1


def test_product_filter_by_unknown_term_name(client):
    r = client.get(
        f"{base_url}?terms={'azertyuiop'}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 0


def test_buy_product_sets_author(buy_client, sample_member, sample_payment_method, sample_product):
    """Regression: buying a product must persist author_id (was NULL → IntegrityError)."""
    r = buy_client.post(
        f"{base_url}buy?memberId={sample_member.id}&paymentMethod={sample_payment_method.id}&products={sample_product.id}",
        headers=TEST_HEADERS_API_KEY_ADMIN,
    )
    assert r.status_code == 204
