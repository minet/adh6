import datetime
import json

import pytest
from adh6.treasury.storage.models import Transaction

from test.integration.resource import (
    TEST_HEADERS_API_KEY_TRESO,
    base_url as host_url,
)

base_url = f"{host_url}/transaction/"


@pytest.fixture
def sample_transaction(sample_member, sample_payment_method):
    return Transaction(
        id=91,
        name="description",
        value=200,
        timestamp=datetime.datetime(2005, 7, 14, 12, 30),
        type=sample_payment_method.id,
        author_id=sample_member.id,
    )


@pytest.fixture
def sample_transaction_pending(sample_member, sample_payment_method):
    return Transaction(
        id=92,
        name="description 2",
        value=230,
        timestamp=datetime.datetime(2005, 7, 14, 12, 31),
        type=sample_payment_method.id,
        author_id=sample_member.id,
    )


@pytest.fixture
async def client(
    _test_client,
    sample_payment_method,
    sample_vlan,
    sample_room1,
    sample_member,
    sample_member_admin,
    sample_transaction,
    sample_transaction_pending,
):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_vlan,
            sample_room1,
            sample_payment_method,
            sample_member,
            sample_member_admin,
            sample_transaction,
            sample_transaction_pending,
            *api_key_fixtures(),
        ]
    )

    yield _test_client

    await cleanup_test_data()


def test_transaction_get_all_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 400


def test_transaction_get_all_limit_zero(client):
    r = client.get(
        f"{base_url}?limit={0}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert len(t) == 0


def test_transaction_get_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert t
    assert len(t) == 2


def test_transaction_post_valid(client):
    sample_transaction1 = {
        "name": "test",
        "value": 400,
        "paymentMethod": 1,
    }

    r = client.post(
        f"{base_url}",
        data=json.dumps(sample_transaction1),
        headers={"Content-Type": "application/json", **TEST_HEADERS_API_KEY_TRESO},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "test"
    assert body["value"] == 400


def test_transaction_delete(client, sample_transaction):
    r = client.delete(
        f"{base_url}{sample_transaction.id}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 204


def test_transaction_get_existant(client, sample_transaction):
    r = client.get(
        f"{base_url}{sample_transaction.id}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8"))


def test_transaction_get_nonexistant(client):
    r = client.get(
        f"{base_url}{100000}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 404


def test_transaction_filter_by_term(client):
    r = client.get(
        f"{base_url}?terms=descri",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 2


def test_transaction_filter_by_term_nonexistant(client):
    r = client.get(
        f"{base_url}?terms=BONJOUR?",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert not result


def test_transaction_filter_by_payment_method(client, sample_transaction: Transaction):
    r = client.get(
        f"{base_url}?filter[paymentMethod]={sample_transaction.type}",
        headers=TEST_HEADERS_API_KEY_TRESO,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 2
