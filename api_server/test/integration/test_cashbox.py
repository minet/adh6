import json
from datetime import datetime

import pytest
from adh6.treasury.storage.models import Caisse

from test.integration.resource import TEST_HEADERS, TEST_HEADERS_SAMPLE, base_url


@pytest.fixture
def sample_caisse():
    return Caisse(id=1, fond=0, coffre=0, date=datetime.now())


@pytest.fixture
def client(sample_caisse, sample_member):
    from .conftest import close_db, prep_db
    from .context import app

    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(sample_caisse, sample_member)
        yield c
        close_db()


def test_cashbox_get(client):
    r = client.get(
        f"{base_url}/treasury/cashbox",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode("utf-8"))
    assert response["coffre"] == 0
    assert response["fond"] == 0


def test_cashbox_get_unaithorized(client):
    r = client.get(
        f"{base_url}/treasury/cashbox",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
