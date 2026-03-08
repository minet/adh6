import json

import pytest

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/mailinglist/"


@pytest.fixture
def client(_test_client, sample_member):
    """Add test-specific fixtures to the transaction."""
    from .conftest import add_test_fixtures, cleanup_test_data

    add_test_fixtures(sample_member)

    yield _test_client

    cleanup_test_data()


@pytest.mark.parametrize("value", [(-1,), (256,)])
def test_mailinglist_list_members_bad_value(client, value):
    r = client.get(
        f"{base_url}?value={value}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_mailinglist_list_members(client, sample_member):
    r = client.get(
        f"{base_url}?value={sample_member.mail_membership}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == [sample_member.id]


def test_room_mailinglist_member_unauthorized_user(client):
    r = client.get(
        f"{base_url}?value={249}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_mailinglist_get_member_membership(client, sample_member):
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == sample_member.mail_membership


def test_mailinglist_get_member_membership_user_authorized(client, sample_member):
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == sample_member.mail_membership


def test_mailinglist_get_member_membership_unknown_member(client):
    r = client.get(
        f"{base_url}member/{200}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_mailinglist_get_member_membership_user_unauthorized(client):
    r = client.get(
        f"{base_url}member/{999}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_mailinglist_update_member_membership(client, sample_member):
    r = client.put(
        f"{base_url}member/{sample_member.id}",
        data=json.dumps({"value": 251}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == 251


def test_mailinglist_update_member_membership_user_authorized(client, sample_member):
    r = client.put(
        f"{base_url}member/{sample_member.id}",
        data=json.dumps({"value": 251}),
        headers={"Content-Type": "application/json", **TEST_HEADERS_SAMPLE},
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == 251


def test_mailinglist_update_member_membership_unknown_member(client):
    r = client.put(
        f"{base_url}member/{4242}",
        data=json.dumps({"value": 251}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


@pytest.mark.parametrize("headers", [TEST_HEADERS, TEST_HEADERS_SAMPLE])
@pytest.mark.parametrize("value", [-1, 256])
def test_mailinglist_update_member_membership_bad_value(
    client, sample_member, value, headers
):
    r = client.put(
        f"{base_url}member/{sample_member.id}",
        data=json.dumps({"value": value}),
        headers={"Content-Type": "application/json", **headers},
    )
    assert r.status_code == 400


def test_mailinglist_update_member_membership_user_unauthorized(client):
    r = client.put(
        f"{base_url}member/{4242}",
        data=json.dumps({"value": 251}),
        headers={"Content-Type": "application/json", **TEST_HEADERS_SAMPLE},
    )
    assert r.status_code == 403
