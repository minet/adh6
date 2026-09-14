import pytest

from test import SAMPLE_CLIENT
from test.integration.resource import TEST_HEADERS, base_url


@pytest.fixture
async def client(_test_client, sample_member):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures([*api_key_fixtures(), sample_member])
    yield _test_client
    await cleanup_test_data()


def test_create_and_list_naina(client):
    response = client.post(f"{base_url}/naina/{SAMPLE_CLIENT}", headers=TEST_HEADERS)

    assert response.status_code == 201

    response = client.get(f"{base_url}/naina", headers=TEST_HEADERS)

    assert response.status_code == 200
    nainas = response.json()
    assert [naina["login"] for naina in nainas] == [SAMPLE_CLIENT]
    assert nainas[0]["expires_at"]


def test_revoke_naina(client):
    response = client.post(f"{base_url}/naina/{SAMPLE_CLIENT}", headers=TEST_HEADERS)
    assert response.status_code == 201

    response = client.delete(f"{base_url}/naina/{SAMPLE_CLIENT}", headers=TEST_HEADERS)
    assert response.status_code == 204

    response = client.get(f"{base_url}/naina", headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json() == []
