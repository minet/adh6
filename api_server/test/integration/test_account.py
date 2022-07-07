import datetime
import json
import pytest

from test.integration.resource import TEST_HEADERS, base_url

from adh6.storage.sql.models import AccountType, Account, Adherent

@pytest.fixture
def sample_account1(sample_member: Adherent):
    return Account(
        id=1,
        name='test1',
        actif=True,
        creation_date=datetime.datetime(2005, 7, 14, 12, 30),
        account_type=AccountType(
            id=1,
            name='adherent'
        ),
        adherent=sample_member,
        compte_courant=False,
        pinned=True)


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
def client(sample_member, sample_room1, sample_account1, sample_account2):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            sample_room1,
            sample_member,
            sample_account1,
            sample_account2
        )
        yield c
        close_db()


def test_account_filter_all_with_invalid_limit(client):
    r = client.get(
        '{}/account/?limit={}'.format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_account_filter_all_with_limit(client):
    r = client.get(
        '{}/account/?limit={}'.format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_account_filter_by_terms(client):
    r = client.get(
        "{}/account/?terms={}".format(base_url, "test"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 2


def test_account_filter_by_terms_one_result(client):
    r = client.get(
        "{}/account/?terms={}".format(base_url, "test1"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_account_filter_by_id(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[id]={}".format(base_url, sample_account1.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_account_filter_by_name(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[name]={}".format(base_url, sample_account1.name),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_account_filter_by_compte_courant(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[compteCourant]={}".format(base_url, sample_account1.compte_courant),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 2


def test_account_filter_by_actif(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[actif]={}".format(base_url, sample_account1.actif),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 2


def test_account_filter_by_pinned(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[pinned]={}".format(base_url, sample_account1.pinned),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_account_filter_by_account_type(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[accountType]={}".format(base_url, sample_account1.account_type.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1


def test_account_filter_by_member(client, sample_account1: Account):
    r = client.get(
        "{}/account/?filter[member]={}".format(base_url, sample_account1.adherent.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.data.decode('utf-8'))
    assert len(result) == 1
