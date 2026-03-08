import json
from datetime import datetime, timedelta

import pytest
from adh6.member.storage.models import Adherent
from adh6.storage import db

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_SAMPLE,
    assert_modification_was_created,
    base_url as host_url,
)

base_url = f"{host_url}/member/"


@pytest.fixture
def client(
    _test_client,
    sample_member,
    sample_member2,
    sample_member3,
    sample_member_admin,
    account_type,
    sample_account,
    sample_payment_method,
    sample_complete_membership,
    sample_pending_validation_membership,
):
    """Client fixture for member tests."""
    from .conftest import add_test_fixtures, cleanup_test_data

    add_test_fixtures(
        [
            account_type,
            sample_member,
            sample_member2,
            sample_member3,
            sample_member_admin,
            sample_account,
            sample_payment_method,
            sample_complete_membership,
            sample_pending_validation_membership,
        ]
    )

    yield _test_client

    cleanup_test_data()


def assert_member_in_db(body):
    # Actually check that the object was inserted
    with db.sessionmaker.begin() as s:
        q = s.query(Adherent)
        q = q.filter(Adherent.login == body["username"])
        r = q.one()
        assert r.nom == body["lastName"]
        assert r.prenom == body["firstName"]
        assert r.mail == body["mail"]
        assert r.login == body["username"]


def test_member_filter_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 4  # 4 because of the admin user


def test_member_filter_all_with_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_limit(client):
    r = client.get(
        f"{base_url}?limit={1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_by_ip(client, sample_member: Adherent):
    r = client.get(
        f"{base_url}?filter[ip]={sample_member.ip}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_by_departure_date_since_now(client):
    r = client.get(
        f"{base_url}?filter[since]={datetime.now().isoformat()}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 3


def test_member_filter_by_departure_date_since_previous_week(client):
    r = client.get(
        f"{base_url}?filter[since]={(datetime.now() + timedelta(days=-7)).isoformat()}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 4


def test_member_filter_by_departure_date_until_now(client):
    r = client.get(
        f"{base_url}?filter[until]={datetime.now().isoformat()}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_by_departure_date_until_next_week(client):
    r = client.get(
        f"{base_url}?filter[until]={(datetime.now() + timedelta(days=7)).isoformat()}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 4


def test_member_filter_terms_first_name(client):
    r = client.get(
        f"{base_url}?terms={'Jean'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 2  # Both Jean-Louis and Jean


def test_member_filter_terms_last_name(client):
    r = client.get(
        f"{base_url}?terms={'ubois'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_terms_email(client):
    r = client.get(
        f"{base_url}?terms={'bgdu78'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_terms_login(client, sample_member: Adherent):
    r = client.get(
        f"{base_url}?terms={sample_member.login}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_terms_comment(client):
    r = client.get(
        f"{base_url}?terms={'routeur'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_terms_nonexistant(client):
    r = client.get(
        f"{base_url}?terms={'azerty'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 0


def test_member_filter_terms_test_upper_case(client, sample_member: Adherent):
    r = client.get(
        f"{base_url}?terms={sample_member.login.upper()}",  # type: ignore  # TODO: fix typing
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_unauthorized(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    "sample_only",
    [
        ("id"),
        ("username"),
        ("firstName"),
        ("lastName"),
    ],
)
def test_member_get_with_only(client, sample_member, sample_only: str):
    r = client.get(
        f"{base_url}{sample_member.id}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len({*sample_only.split(","), "id"}) == len(set(response.keys()))


def test_member_get_with_unknown_only(client, sample_member):
    sample_only = "azerty"
    r = client.get(
        f"{base_url}{sample_member.id}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_get_existant(client, sample_member):
    r = client.get(
        f"{base_url}{sample_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8"))


def test_member_get_nonexistant(client):
    r = client.get(
        f"{base_url}{4242}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_member_get_unauthorized(client):
    r = client.get(
        f"{base_url}{4242}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_get_another_user(client, sample_member2):
    r = client.get(
        f"{base_url}{sample_member2.id}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_delete_existant(client, sample_member):
    r = client.delete(f"{base_url}{sample_member.id}", headers=TEST_HEADERS)
    assert r.status_code == 204
    assert_modification_was_created(db.session)

    s = db.session
    q = s.query(Adherent)
    q = q.filter(Adherent.login == "dubois_j")
    assert not s.query(q.exists()).scalar()


def test_member_delete_non_existant(client):
    r = client.delete(f"{base_url}{4242}", headers=TEST_HEADERS)
    assert r.status_code == 404


def test_member_delete_unauthorized(client):
    r = client.delete(
        f"{base_url}{4242}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_post_member_create_invalid_email(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "INVALID_EMAIL",
        "username": "doe_john",
    }
    res = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert res.status_code == 400


def test_member_post_member_create(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "john.doe@gmail.com",
        "username": "doe_john",
    }
    res = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert res.status_code == 201
    assert_member_in_db(body)

    r = client.get(
        f"{host_url}/mailinglist/member/{int(res.text)}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == 249


def test_member_post_member_same_login(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "john.doe@gmail.com",
        "username": "doe_john",
    }
    res = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert res.status_code == 201

    res = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert res.status_code == 400


def test_member_post_unauthorized(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "john.doe@gmail.com",
        "username": "doe_john",
    }
    r = client.post(
        f"{base_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS_SAMPLE},
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    "key, value",
    [
        ("firstName", "TEST"),
        ("lastName", "TEST"),
        ("mail", "TEST@TEST.FR"),
        ("username", "TESTTEST"),
    ],
)
def test_member_patch(client, sample_member: Adherent, key: str, value: str):
    body = {
        key: value,
    }
    res = client.patch(
        f"{base_url}{sample_member.id}",
        json=body,
        headers=TEST_HEADERS,
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session)
    member_to_check = {
        "firstName": sample_member.prenom,
        "lastName": sample_member.nom,
        # "comment": sample_member.commentaires,
        "mail": sample_member.mail,
        "username": sample_member.login,
    }
    member_to_check[key] = value
    assert_member_in_db(member_to_check)


@pytest.mark.parametrize(
    "key, value",
    [
        ("firstName", "TEST"),
        ("lastName", "TEST"),
        ("mail", "TEST@TEST.FR"),
        ("username", "TESTTEST"),
    ],
)
def test_member_patch_membership_pending(
    client, sample_member2: Adherent, key: str, value: str
):
    body = {
        key: value,
    }
    res = client.patch(
        f"{base_url}{sample_member2.id}",
        json=body,
        headers=TEST_HEADERS,
    )
    assert res.status_code == 400


def test_member_patch_unknown(client):
    r = client.patch(
        f"{base_url}{4242}",
        json={},
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_member_patch_unauthorized(client):
    r = client.patch(
        f"{base_url}{4242}",
        json={},
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_get_logs(client, sample_member):
    body = {
        "dhcp": False,
    }
    result = client.get(
        f"{base_url}{sample_member.id}/logs/",
        params=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert result.status_code == 200
    response_data = json.loads(result.content.decode("utf-8"))

    # Check the structure of the new paginated response
    assert "logs" in response_data
    assert "total" in response_data
    assert "hasMore" in response_data
    assert isinstance(response_data["logs"], list)
    assert isinstance(response_data["total"], int)
    assert isinstance(response_data["hasMore"], bool)

    # Should have some logs in the mock data
    assert len(response_data["logs"]) > 0

    # Each log should have timestamp and message
    for log in response_data["logs"]:
        assert "timestamp" in log
        assert "message" in log


def test_member_get_logs_unauthorized(client):
    r = client.get(
        f"{base_url}{4242}/logs/",
        params=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize("headers", [TEST_HEADERS, TEST_HEADERS_SAMPLE])
def test_member_get_statuses(client, sample_member, headers):
    result = client.get(
        f"{base_url}{sample_member.id}/statuses/",
        headers={"Content-Type": "application/json", **headers},
    )
    assert result.status_code == 200


def test_member_get_statuses_unauthorized(client):
    r = client.get(
        f"{base_url}{4242}/statuses/",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_comment_put(client, sample_member):
    body = {
        "comment": "test_comment",
    }
    result = client.put(
        f"{base_url}{sample_member.id}/comment/",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert result.status_code == 204


def test_member_comment_put_unauthorized(client):
    r = client.put(
        f"{base_url}{4242}/comment/",
        data=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_comment_get(client, sample_member):
    body = {
        "comment": "test_comment",
    }
    result = client.put(
        f"{base_url}{sample_member.id}/comment/",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert result.status_code == 204

    result = client.get(
        f"{base_url}{sample_member.id}/comment/",
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert result.status_code == 200
    assert result.json()["comment"] == "test_comment"


def test_member_comment_get_empty(client, sample_member):
    result = client.get(
        f"{base_url}{sample_member.id}/comment/",
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert result.status_code == 200
    assert result.json()["comment"] == ""


def test_member_comment_get_unauthorized(client):
    r = client.get(
        f"{base_url}{4242}/comment/",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_comment_too_long(client, sample_member):
    body = {
        "comment": "a" * 256,
    }
    result = client.put(
        f"{base_url}{sample_member.id}/comment/",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert result.status_code == 400
