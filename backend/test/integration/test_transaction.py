import datetime
import json

import pytest
from adh6.storage import db
from adh6.treasury.storage.models import Account, AccountType, Transaction

from test.integration.resource import (
    INVALID_TRANSACTION_VALUE,
    TEST_HEADERS,
    base_url as host_url,
)

base_url = f"{host_url}/transaction/"


@pytest.fixture
def sample_account_type1():
    return AccountType(id=1, name="adherent")


@pytest.fixture
def sample_account_type2():
    return AccountType(id=2, name="adherent")


@pytest.fixture
def sample_account1(sample_account_type1):
    return Account(
        id=1,
        name="test1",
        actif=True,
        creation_date=datetime.datetime(2005, 7, 14, 12, 30),
        type=sample_account_type1.id,
        adherent_id=None,
        compte_courant=False,
        pinned=False,
    )


@pytest.fixture
def sample_account2(sample_account_type2):
    return Account(
        id=2,
        name="test3",
        actif=True,
        creation_date=datetime.datetime(2005, 7, 14, 12, 31),
        type=sample_account_type2.id,
        adherent_id=None,
        compte_courant=False,
        pinned=False,
    )


@pytest.fixture
def sample_transaction(sample_member, sample_account1, sample_account2, sample_payment_method):
    return Transaction(
        id=91,
        src=sample_account1.id,
        dst=sample_account2.id,
        name="description",
        value=200,
        attachments="",
        timestamp=datetime.datetime(2005, 7, 14, 12, 30),
        type=sample_payment_method.id,
        author_id=sample_member.id,
        pending_validation=False,
    )


@pytest.fixture
def sample_transaction_pending(sample_member, sample_account1, sample_account2, sample_payment_method):
    return Transaction(
        id=92,
        src=sample_account1.id,
        dst=sample_account2.id,
        name="description 2",
        value=230,
        attachments="",
        timestamp=datetime.datetime(2005, 7, 14, 12, 31),
        type=sample_payment_method.id,
        author_id=sample_member.id,
        pending_validation=True,
    )


@pytest.fixture
async def client(
    _test_client,
    sample_account_type1,
    sample_account_type2,
    sample_account1,
    sample_account2,
    sample_payment_method,
    sample_member,
    sample_transaction,
    sample_transaction_pending,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_account_type1,
            sample_account_type2,
            sample_account1,
            sample_account2,
            sample_payment_method,
            sample_member,
            sample_transaction,
            sample_transaction_pending,
        ]
    )

    yield _test_client

    await cleanup_test_data()


def assert_transaction_in_db(body):
    with db.sessionmaker.begin() as s:
        q = s.query(Transaction)
        q = q.filter(Transaction.name == body["name"])
        sw = q.one()
        assert sw.name == body["name"]
        assert sw.src == body["src"]
        assert sw.dst == body["dst"]
        assert sw.value == body["value"]


@pytest.mark.parametrize("test_value", INVALID_TRANSACTION_VALUE)
def test_switch_post_invalid_value(client, test_value):
    sample_transaction1 = {
        "src": 1,
        "dst": 2,
        "name": "test",
        "attachments": "",
        "value": test_value,
        "payment_method": "liquide",
    }
    r = client.post(
        f"{base_url}",
        data=json.dumps(sample_transaction1),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_transaction_post_valid(client):
    sample_transaction1 = {
        "src": 1,
        "dst": 2,
        "name": "test",
        "attachments": [],
        "value": 400,
        "paymentMethod": 1,
    }

    r = client.post(
        f"{base_url}",
        data=json.dumps(sample_transaction1),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["author"] is not None, "author must be set from authenticated user, not null"
    assert_transaction_in_db(sample_transaction1)


def test_transaction_get_all_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_get_all_limit(client):
    r = client.get(
        f"{base_url}?limit={0}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert len(t) == 0


def test_transaction_get_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert t
    assert len(t) == 2


@pytest.mark.parametrize(
    "sample_only",
    [
        ("id"),
        ("dst"),
        ("src"),
        ("name"),
        ("paymentMethod"),
        ("pendingValidation"),
        ("timestamp"),
        ("value"),
    ],
)
def test_transaction_search_with_only(client, sample_only: str):
    r = client.get(
        f"{base_url}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 2
    assert len({*sample_only.split(","), "id"}) == len(set(response[0].keys()))


def test_transaction_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f"{base_url}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_validate_pending(client, sample_transaction_pending):
    r = client.get(
        f"{base_url}{sample_transaction_pending.id}/validate",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    with db.sessionmaker.begin() as s:
        q = s.query(Transaction)
        q = q.filter(Transaction.name == sample_transaction_pending.name)
        sw = q.one()
        assert sw.pending_validation is False, "Transaction was not actually validated"


def test_device_validate_nonpending(client, sample_transaction):
    r = client.get(
        f"{base_url}{sample_transaction.id}/validate",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_delete_pending(client, sample_transaction_pending):
    r = client.delete(
        f"{base_url}{sample_transaction_pending.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    s = db.session
    q = s.query(Transaction)
    q = q.filter(Transaction.pending_validation.is_(True))
    q = q.filter(Transaction.name == "description 2")
    assert not s.query(q.exists()).scalar(), "Object not actually deleted"


def test_device_delete_nonpending(client, sample_transaction):
    r = client.delete(
        f"{base_url}{sample_transaction.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_get_existant_transaction(client, sample_transaction):
    r = client.get(
        f"{base_url}{sample_transaction.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8"))


def test_transaction_get_non_existant_transaction(client):
    r = client.get(
        f"{base_url}{100000}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_transaction_filter_by_term_desc(client):
    terms = "descri"
    r = client.get(
        f"{base_url}?terms={terms}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result
    assert len(result) == 2


def test_transaction_filter_by_term_nonexistant(client):
    terms = "BONJOUR?"
    r = client.get(
        f"{base_url}?terms={terms}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert not result


def test_transaction_filter_by_id(client, sample_transaction: Transaction):
    r = client.get(
        f"{base_url}?filter[id]={sample_transaction.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_transaction_filter_by_payment_method(client, sample_transaction: Transaction):
    r = client.get(
        f"{base_url}?filter[paymentMethod]={sample_transaction.type}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 2


def test_transaction_filter_by_pending_validation(client, sample_transaction: Transaction):
    r = client.get(
        f"{base_url}?filter[pendingValidation]={sample_transaction.pending_validation}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 1


def test_transaction_filter_by_src(client, sample_transaction: Transaction):
    r = client.get(
        f"{base_url}?filter[src]={sample_transaction.src}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 2


def test_transaction_filter_by_dst(client, sample_transaction: Transaction):
    r = client.get(
        f"{base_url}?filter[dst]={sample_transaction.dst}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert len(result) == 2
