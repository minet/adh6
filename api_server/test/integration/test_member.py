import json
from dateutil import parser
from pytest_lazyfixture import lazy_fixture
import pytest

from adh6.storage.sql.models import Chambre, db
from adh6.storage.sql.models import Adherent
from test.integration.resource import (
    TEST_HEADERS_SAMPLE, base_url, TEST_HEADERS, assert_modification_was_created)
from test.integration.context import tomorrow


def assert_member_in_db(body):
    # Actually check that the object was inserted
    s = db.session()
    q = s.query(Adherent)
    q = q.filter(Adherent.login == body["username"])
    r = q.one()
    assert r.nom == body["lastName"]
    assert r.prenom == body["firstName"]
    assert r.mail == body["email"]
    assert r.date_de_depart == parser.parse(body["departureDate"]).date()
    assert r.chambre.numero == body["roomNumber"]
    assert r.commentaires == body["comment"]
    assert r.login == body["username"]


def test_member_filter_all(client):
    r = client.get(
        '{}/member/'.format(base_url),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4 # 4 because of the admin user


@pytest.mark.parametrize(
    'sample_only', 
    [
        ("id"),
        ("username"),
        ("firstName"),
        ("lastName"),
        ("roomNumber"),
    ])
def test_member_search_with_only(client, sample_only: str):
    r = client.get(
        f'{base_url}/member/?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4
    assert len(set(sample_only.split(",") + ["__typename", "id"])) == len(set(response[0].keys()))


def test_member_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}/member/?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_invalid_limit(client):
    r = client.get(
        '{}/member/?limit={}'.format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_limit(client):
    r = client.get(
        '{}/member/?limit={}'.format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_by_room_number(client, sample_room1):
    r = client.get(
        '{}/member/?filter[roomNumber]={}'.format(base_url, sample_room1.numero),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 2


def test_member_filter_by_non_existant_id(client):
    r = client.get(
        '{}/member/?filter[roomNumber]={}'.format(base_url, 6666),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 0


def test_member_filter_by_ip(client, sample_member: Adherent):
    r = client.get(
        '{}/member/?filter[ip]={}'.format(base_url, sample_member.ip),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_first_name(client):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, "Jean"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_last_name(client):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, "ubois"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_email(client):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, "bgdu78"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_login(client, sample_member: Adherent):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, sample_member.login),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_comment(client):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, "routeur"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_nonexistant(client):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, "azerty"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 0


def test_member_filter_terms_test_upper_case(client, sample_member: Adherent):
    r = client.get(
        '{}/member/?terms={}'.format(base_url, sample_member.login.upper()),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_unauthorized(client):
    r = client.get(
        f'{base_url}/member/',
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
        ("roomNumber"),
    ])
def test_member_get_with_only(client, sample_member, sample_only: str):
    r = client.get(
        f'{base_url}/member/{sample_member.id}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(set(sample_only.split(",") + ["__typename", "id"])) == len(set(response.keys()))


def test_member_get_with_unknown_only(client, sample_member):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}/member/{sample_member.id}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400



def test_member_get_existant(client, sample_member):
    r = client.get(
        '{}/member/{}'.format(base_url, sample_member.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_member_get_nonexistant(client):
    r = client.get(
        '{}/member/{}'.format(base_url, 4242),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_member_get_unauthorized(client):
    r = client.get(
        f'{base_url}/member/{4242}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_delete_existant(client, sample_member):
    r = client.delete(
        '{}/member/{}'.format(base_url, sample_member.id),
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
        '{}/member/{}'.format(base_url, 4242),
        headers=TEST_HEADERS
    )
    assert r.status_code == 404


def test_member_delete_unauthorized(client):
    r = client.delete(
        f'{base_url}/member/{4242}',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_post_member_create_invalid_email(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "roomNumber": 4592,
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "INVALID_EMAIL",
        "username": "doe_john"
    }
    res = client.post(
        '{}/member/'.format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400


def test_member_post_member_create_unknown_room(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "roomNumber": 9999,
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "john.doe@gmail.com",
        "username": "doe_john"
    }
    res = client.post(
        '{}/member/'.format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 404 == res.status_code


def test_member_post_member_create(client, sample_room1):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "roomNumber": sample_room1.numero,
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "john.doe@gmail.com",
        "username": "doe_john"
    }
    res = client.post(
        '{}/member/'.format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 201 == res.status_code
    assert_modification_was_created(db.session())

    assert_member_in_db(body)


def test_member_post_unauthorized(client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "john.doe@gmail.com",
        "username": "doe_john"
    }
    r = client.post(
        f'{base_url}/member/',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.fixture
def sample_room_id(sample_room2: Chambre):
    return sample_room2.numero


@pytest.mark.parametrize(
    'key, value',
    [
        ("firstName", "TEST"),
        ("lastName", "TEST"),
        ("comment", "TEST"),
        ("email", "TEST@TEST.FR"),
        ("username", "TESTTEST"),
        ("roomNumber", lazy_fixture('sample_room_id')),
        ("mailinglist", 2),
    ]
)
def test_member_patch(client, sample_member: Adherent, key: str, value: str):
    body = {
        key: value,
    }
    res = client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    member_to_check = {
        "firstName": sample_member.prenom,
        "lastName": sample_member.nom,
        "roomNumber": sample_member.chambre.numero,
        "comment": sample_member.commentaires,
        "departureDate": str(sample_member.date_de_depart),
        "email": sample_member.mail,
        "username": sample_member.login
    }
    member_to_check[key] = value
    assert_member_in_db(member_to_check)

@pytest.mark.parametrize(
    'key, value',
    [
        ("firstName", "TEST"),
        ("lastName", "TEST"),
        ("comment", "TEST"),
        ("email", "TEST@TEST.FR"),
        ("username", "TESTTEST"),
        ("roomNumber", lazy_fixture('sample_room_id')),
        ("mailinglist", 2),
    ]
)
def test_member_patch_membership_pending(client, sample_member2: Adherent, key: str, value: str):
    body = {
        key: value,
    }
    res = client.patch(
        f'{base_url}/member/{sample_member2.id}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400

@pytest.mark.parametrize('value', [-1, -2, -5, 256, 257])
def test_member_patch_bad_mailinglist(client, sample_member: Adherent, value: int):
    body = {
        "mailinglist": value,
    }
    res = client.patch(
        f'{base_url}/member/{sample_member.id}',
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400


def test_member_patch_unauthorized(client):
    r = client.patch(
        f'{base_url}/member/{4242}',
        data=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_put_member_update(client, sample_member, sample_room1):
    body = {
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "roomNumber": sample_room1.numero,
        "comment": "comment",
        "departureDate": str(tomorrow),
        "email": "john.doe@gmail.com",
        "username": "dubois_j"
    }
    res = client.put(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 201
    assert_modification_was_created(db.session())

    assert_member_in_db(body)


def test_member_put_member_membership_pending(client, sample_member2: Adherent, sample_room1):
    body = {
        "firstName": sample_member2.prenom,
        "lastName": sample_member2.nom,
        "roomNumber": sample_room1.numero,
        "comment": sample_member2.commentaires,
        "departureDate": str(sample_member2.date_de_depart),
        "email": sample_member2.mail,
        "username": sample_member2.login
    }
    res = client.put(
        '{}/member/{}'.format(base_url, sample_member2.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400


def test_member_put_unauthorized(client):
    r = client.put(
        f'{base_url}/member/{4242}',
        data=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_member_get_logs(client, sample_member):
    body = {
        "dhcp": False,
    }
    result = client.get(
        '{}/member/{}/logs/'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200
    assert json.loads(result.data.decode('utf-8')) == ["1 test_log"]


def test_member_get_logs_unauthorized(client):
    r = client.get(
        f'{base_url}/member/{4242}/logs/',
        data=json.dumps({}),
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


@pytest.mark.parametrize('headers', [TEST_HEADERS, TEST_HEADERS_SAMPLE])
def test_member_get_statuses(client, sample_member, headers):
    result = client.get(
        f'{base_url}/member/{sample_member.id}/statuses/',
        content_type='application/json',
        headers=headers,
    )
    print(result.text)
    assert result.status_code == 200


def test_member_get_statuses_unauthorized(client):
    r = client.get(
        f'{base_url}/member/{4242}/statuses/',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
