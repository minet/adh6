import json

import pytest
from adh6.member.storage.models import Adherent
from adh6.treasury.storage.models import Account, AccountType, PaymentMethod, Product

from test.integration.context import tomorrow
from test.integration.resource import TEST_HEADERS, base_url as host_url

TESTING_CLIENT = "TestingClient"
TESTING_CLIENT_ID = 28

base_url = f"{host_url}/product/"


@pytest.fixture
def sample_product():
    yield Product(id=1, name="test", buying_price=2.0, selling_price=2.0)


@pytest.fixture
async def client(_test_client, sample_product):
    from .conftest import add_test_fixtures, cleanup_test_data

    # Add test data
    await add_test_fixtures([sample_product])

    yield _test_client

    # Cleanup after test
    await cleanup_test_data()


@pytest.fixture
async def buy_client(
    _test_client,
    sample_product,
    sample_account_type,
    sample_member,
    sample_account,
    sample_account_frais_techniques,
    sample_payment_method,
    sample_member_admin,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_account_type,
            sample_member_admin,
            sample_member,
            sample_account,
            sample_account_frais_techniques,
            sample_payment_method,
            sample_product,
        ]
    )

    yield _test_client

    await cleanup_test_data()


@pytest.fixture
def sample_account_type():
    yield AccountType(id=10, name="Adhérent")


@pytest.fixture
def sample_member_admin():
    yield Adherent(
        id=TESTING_CLIENT_ID,
        login=TESTING_CLIENT,
        mail="admin@test.net",
        nom="Admin",
        prenom="Test",
        password="",
        mail_membership=1,
        date_de_depart=tomorrow,
    )


@pytest.fixture
def sample_member():
    yield Adherent(
        id=50,
        login="testbuyer",
        mail="buyer@test.net",
        nom="Buyer",
        prenom="Test",
        password="",
        mail_membership=1,
        date_de_depart=tomorrow,
    )


@pytest.fixture
def sample_account(sample_account_type, sample_member):
    from datetime import datetime

    yield Account(
        id=10,
        type=sample_account_type.id,
        creation_date=datetime.now(),
        name="buyer account",
        actif=True,
        compte_courant=False,
        pinned=False,
        adherent_id=sample_member.id,
    )


@pytest.fixture
def sample_account_frais_techniques(sample_account_type):
    from datetime import datetime

    yield Account(
        id=11,
        type=sample_account_type.id,
        creation_date=datetime.now(),
        name="MiNET frais techniques",
        actif=True,
        compte_courant=True,
        pinned=True,
    )


@pytest.fixture
def sample_payment_method():
    yield PaymentMethod(id=10, name="liquide")


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


def test_buy_product_sets_author(buy_client, sample_member, sample_payment_method, sample_product):
    """Regression: buying a product must persist author_id (was NULL → IntegrityError)."""
    r = buy_client.post(
        f"{base_url}buy?memberId={sample_member.id}&paymentMethod={sample_payment_method.id}&products={sample_product.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
