import json
from datetime import datetime

import pytest
from adh6.treasury.storage.models import Caisse

from test.integration.resource import TEST_HEADERS, TEST_HEADERS_SAMPLE, base_url


@pytest.fixture
def sample_caisse():
    return Caisse(id=1, fond=0, coffre=0, date=datetime.now())


@pytest.fixture
async def client(_test_client, sample_caisse, sample_member):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures([sample_caisse, sample_member])

    yield _test_client

    await cleanup_test_data()


def test_cashbox_get(client):
    r = client.get(
        f"{base_url}/treasury/cashbox",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response["coffre"] == 0
    assert response["fond"] == 0


def test_cashbox_get_unaithorized(client):
    r = client.get(
        f"{base_url}/treasury/cashbox",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
