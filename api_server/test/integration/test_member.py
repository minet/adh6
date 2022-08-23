from datetime import datetime, timedelta
import json
import pytest

from adh6.storage.sql.models import db
from adh6.storage.sql.models import Adherent
from test.integration.resource import (
    TEST_HEADERS_SAMPLE, base_url as host_url, TEST_HEADERS, assert_modification_was_created)


base_url = f'{host_url}/member/'

def assert_member_in_db(body):
    # Actually check that the object was inserted
    s = db.session()
    q = s.query(Adherent)
    q = q.filter(Adherent.login == body["username"])
    r = q.one()
    assert r.nom == body["lastName"]
    assert r.prenom == body["firstName"]
    assert r.mail == body["mail"]
#    assert r.commentaires == body["comment"]
    assert r.login == body["username"]


def test_member_filter_all(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4 # 4 because of the admin user


def test_member_filter_all_with_invalid_limit(client):
    r = client.get(
        f'{base_url}?limit={-1}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_limit(client):
    r = client.get(
        f'{base_url}?limit={1}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_by_ip(client, sample_member: Adherent):
    r = client.get(
        f'{base_url}?filter[ip]={sample_member.ip}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_by_departure_date_since_now(client):
    r = client.get(
        f'{base_url}?filter[since]={datetime.now().isoformat()}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 3


def test_member_filter_by_departure_date_since_previous_week(client):
    r = client.get(
        f'{base_url}?filter[since]={(datetime.now() + timedelta(days=-7)).isoformat()}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4


def test_member_filter_by_departure_date_until_now(client):
    r = client.get(
        f'{base_url}?filter[until]={datetime.now().isoformat()}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_by_departure_date_until_next_week(client):
    r = client.get(
        f'{base_url}?filter[until]={(datetime.now() + timedelta(days=7)).isoformat()}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4


def test_member_filter_terms_first_name(client):
    r = client.get(
        f'{base_url}?terms={"Jean"}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_last_name(client):
    r = client.get(
        f'{base_url}?terms={"ubois"}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_email(client):
    r = client.get(
        f'{base_url}?terms={"bgdu78"}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_login(client, sample_member: Adherent):
    r = client.get(
        f'{base_url}?terms={sample_member.login}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_comment(client):
    r = client.get(
        f'{base_url}?terms={"routeur"}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_nonexistant(client):
    r = client.get(
        f'{base_url}?terms={"azerty"}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 0


def test_member_filter_terms_test_upper_case(client, sample_member: Adherent):
    r = client.get(
        f'{base_url}?terms={sample_member.login.upper()}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_unauthorized(client):
    r = client.get(
        f'{base_url}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403

@pytest.mark.parametrize(
    'sample_only', 
    [
        ("id"),
        ("username"),
        ("firstName"),
        ("lastName"),
    ])
def test_member_get_with_only(client, sample_member, sample_only: str):
    r = client.get(
        f'{base_url}{sample_member.id}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(set(sample_only.split(",") + ["id"])) == len(set(response.keys()))


def test_member_get_with_unknown_only(client, sample_member):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}{sample_member.id}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400



def test_member_get_existant(client, sample_member):
    r = client.get(
        f'{base_url}{sample_member.id}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_member_get_nonexistant(client):
    r = client.get(
        f'{base_url}{4242}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_member_get_unauthorized(client):
    r = client.get(
        f'{base_url}{4242}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_delete_existant(client, sample_member):
    r = client.delete(
        f'{base_url}{sample_member.id}',
        headers=TEST_HEADERS
    )
    assert r.status_code == 204
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Adherent)
    q = q.filter(Adherent.login == "dubois_j")
    assert not s.query(q.exists()).scalar()


def test_member_delete_non_existant(client):
    r = client.delete(
        f'{base_url}{4242}',
        headers=TEST_HEADERS
    )
    assert r.status_code == 404


def test_member_delete_unauthorized(client):
    r = client.delete(
        f'{base_url}{4242}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_post_member_create_invalid_email(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "INVALID_EMAIL",
        "username": "doe_john"
    }
    res = client.post(
        f'{base_url}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400


def test_member_post_member_create(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "john.doe@gmail.com",
        "username": "doe_john"
    }
    res = client.post(
        f'{base_url}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 201 == res.status_code
    assert_modification_was_created(db.session())
    assert_member_in_db(body)

    r = client.get(
        f"{host_url}/mailinglist/member/{int(res.text)}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert response == 249
    


def test_member_post_member_same_login(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "john.doe@gmail.com",
        "username": "doe_john"
    }
    res = client.post(
        f'{base_url}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 201 == res.status_code

    res = client.post(
        f'{base_url}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 400 == res.status_code


def test_member_post_unauthorized(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "mail": "john.doe@gmail.com",
        "username": "doe_john"
    }
    r = client.post(
        f'{base_url}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize(
    'key, value',
    [
        ("firstName", "TEST"),
        ("lastName", "TEST"),
        ("mail", "TEST@TEST.FR"),
        ("username", "TESTTEST"),
    ]
)
def test_member_patch(client, sample_member: Adherent, key: str, value: str):
    body = {
        key: value,
    }
    res = client.patch(
        f'{base_url}{sample_member.id}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    member_to_check = {
        "firstName": sample_member.prenom,
        "lastName": sample_member.nom,
        # "comment": sample_member.commentaires,
        "mail": sample_member.mail,
        "username": sample_member.login
    }
    member_to_check[key] = value
    assert_member_in_db(member_to_check)

@pytest.mark.parametrize(
    'key, value',
    [
        ("firstName", "TEST"),
        ("lastName", "TEST"),
        ("mail", "TEST@TEST.FR"),
        ("username", "TESTTEST"),
    ]
)
def test_member_patch_membership_pending(client, sample_member2: Adherent, key: str, value: str):
    body = {
        key: value,
    }
    res = client.patch(
        f'{base_url}{sample_member2.id}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400


def test_member_patch_unknown(client):
    r = client.patch(
        f'{base_url}{4242}',
        data=json.dumps({}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_member_patch_unauthorized(client):
    r = client.patch(
        f'{base_url}{4242}',
        data=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_get_logs(client, sample_member):
    body = {
        "dhcp": False,
    }
    result = client.get(
        f'{base_url}{sample_member.id}/logs/',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200
    assert json.loads(result.data.decode('utf-8')) == ["1 test_log"]


def test_member_get_logs_unauthorized(client):
    r = client.get(
        f'{base_url}{4242}/logs/',
        data=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize('headers', [TEST_HEADERS, TEST_HEADERS_SAMPLE])
def test_member_get_statuses(client, sample_member, headers):
    result = client.get(
        f'{base_url}{sample_member.id}/statuses/',
        content_type='application/json',
        headers=headers,
    )
    assert result.status_code == 200


def test_member_get_statuses_unauthorized(client):
    r = client.get(
        f'{base_url}{4242}/statuses/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
