import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_API_KEY_ADMIN,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/profile"


@pytest.fixture
async def client(_test_client, sample_member, sample_member_admin):
    """Add test-specific fixtures to the transaction."""
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures([sample_member, sample_member_admin], api_key_fixtures())

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


def test_authentication_and_route_share_one_session(client):
    sessions: set[int] = set()

    def on_begin(session, transaction, connection):
        sessions.add(id(session))

    event.listen(Session, "after_begin", on_begin)
    try:
        # API keys are resolved from the database, unlike the fake test OIDC tokens.
        r = client.get(base_url, headers=TEST_HEADERS_API_KEY_ADMIN)
    finally:
        event.remove(Session, "after_begin", on_begin)

    assert r.status_code == 200
    assert len(sessions) == 1
