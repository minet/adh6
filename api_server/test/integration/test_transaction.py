import datetime
import json

import pytest

from src.interface_adapter.sql.model.models import  db
from src.interface_adapter.sql.model.models import Transaction, Account, AccountType
from test.integration.resource import TEST_HEADERS, INVALID_TRANSACTION_VALUE, base_url


@pytest.fixture
def sample_account1():
    return Account(
        id=1,
        name='test1',
        actif=True,
        creation_date=datetime.datetime(2005, 7, 14, 12, 30),
        account_type=AccountType(
            id=1,
            name='adherent'
        ),
        adherent=None,
        compte_courant=False,
        pinned=False)


@pytest.fixture
def sample_account2():
    return Account(
        id=2,
        name='test3',
        actif=True,
        creation_date=datetime.datetime(2005, 7, 14, 12, 31),
        account_type=AccountType(
            id=2,
            name='event'
        ),
        adherent=None,
        compte_courant=False,
        pinned=False)


@pytest.fixture
def sample_transaction(sample_member, sample_account1, sample_account2, sample_payment_method):
    return Transaction(
        id=91,
        src_account=sample_account1,
        dst_account=sample_account2,
        name='description',
        value=200,
        attachments='',
        timestamp=datetime.datetime(2005, 7, 14, 12, 30),
        payment_method=sample_payment_method,
        author=sample_member,
        pending_validation=False)


@pytest.fixture
def sample_transaction_pending(sample_member, sample_account1, sample_account2, sample_payment_method):
    return Transaction(
        id=92,
        src_account=sample_account1,
        dst_account=sample_account2,
        name='description 2',
        value=230,
        attachments='',
        timestamp=datetime.datetime(2005, 7, 14, 12, 31),
        payment_method=sample_payment_method,
        author=sample_member,
        pending_validation=True)


@pytest.fixture
def client(sample_transaction, sample_transaction_pending):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            sample_transaction,
            sample_transaction_pending
        )
        yield c
        close_db()


def assert_transaction_in_db(body):
    s = db.session()
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
        "payment_method": "liquide"
    }
    r = client.post(
        "{}/transaction/".format(base_url),
        data=json.dumps(sample_transaction1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 400

#TODO: author should not be send and should be in readonly
@pytest.mark.xfail(reason="author id should not be send and instead be compute in the backend")
def test_transaction_post_valid(client, sample_member_admin):
    sample_transaction1 = {
        "src": 1,
        "dst": 2,
        "name": "test",
        "attachments": [],
        "value": 400,
        "paymentMethod": 1,
        "author": sample_member_admin.id
    }

    # Insert data to the database
    r = client.post(
        "{}/transaction/".format(base_url),
        data=json.dumps(sample_transaction1),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert r.status_code == 201
    assert_transaction_in_db(sample_transaction1)


def test_transaction_get_all_invalid_limit(client):
    r = client.get(
        "{}/transaction/?limit={}".format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_get_all_limit(client):
    r = client.get(
        "{}/transaction/?limit={}".format(base_url, 0),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.data.decode('utf-8'))
    assert len(t) == 0


def test_transaction_get_all(client):
    r = client.get(
        "{}/transaction/".format(base_url),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.data.decode('utf-8'))
    assert t
    assert len(t) == 2

@pytest.mark.parametrize(
    'sample_only', 
    [
        ("id"),
        ("dst"),
        ("src"),
        ("name"),
        ("paymentMethod"),
        ("pendingValidation"),
        ("timestamp"),
        ("value"),
    ])
def test_transaction_search_with_only(client, sample_only: str):
    r = client.get(
        f'{base_url}/transaction/?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 2
    assert len(set(sample_only.split(",") + ["__typename", "id"])) == len(set(response[0].keys()))


def test_transaction_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}/transaction/?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_validate_pending(client, sample_transaction_pending):
    r = client.get(
        '{}/transaction/{}/validate'.format(base_url, sample_transaction_pending.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    s = db.session()
    q = s.query(Transaction)
    q = q.filter(Transaction.name == sample_transaction_pending.name)
    sw = q.one()
    assert sw.pending_validation == False, "Transaction was not actually validated"


def test_device_validate_nonpending(client, sample_transaction):
    r = client.get(
        '{}/transaction/{}/validate'.format(base_url, sample_transaction.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_delete_pending(client, sample_transaction_pending):
    r = client.delete(
        '{}/transaction/{}'.format(base_url, sample_transaction_pending.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    s = db.session()
    q = s.query(Transaction)
    q = q.filter(Transaction.pending_validation == True)
    q = q.filter(Transaction.name == "description 2")
    assert not s.query(q.exists()).scalar(), "Object not actually deleted"


def test_device_delete_nonpending(client, sample_transaction):
    r = client.delete(
        '{}/transaction/{}'.format(base_url, sample_transaction.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_transaction_get_existant_transaction(client, sample_transaction):
    r = client.get(
        "{}/transaction/{}".format(base_url, sample_transaction.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_transaction_get_non_existant_transaction(client):
    r = client.get(
        "{}/transaction/{}".format(base_url, 100000),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_transaction_filter_by_term_desc(client):
    terms = "descri"
    r = client.get(
        "{}/transaction/?terms={}".format(base_url, terms),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert result
    assert len(result) == 2


def test_transaction_filter_by_term_nonexistant(client):
    terms = "BONJOUR?"
    r = client.get(
        "{}/transaction/?terms={}".format(base_url, terms),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert not result
