import pytest

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/profile"


@pytest.fixture
async def client(_test_client, sample_member, sample_member_admin):
    """Add test-specific fixtures to the transaction."""
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures([sample_member, sample_member_admin])

    yield _test_client

    await cleanup_test_data()


def test_profile_admin(client):
    r = client.get(
        base_url,
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200


def test_profile_user(client):
    r = client.get(
        base_url,
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 200
