import json
from dateutil import parser
from pytest import mark

from src.interface_adapter.sql.model.models import db
from src.interface_adapter.sql.model.models import Adherent
from test.integration.resource import (
    base_url, TEST_HEADERS, assert_modification_was_created)
from test.integration.context import tomorrow


def prep_db(session,
            sample_member, sample_member2, sample_member3,
            wired_device, wireless_device,
            account_type,
            sample_room1, sample_room12, sample_vlan, sample_account, sample_membership):
    session.add_all([
        sample_room1, sample_room12,
        wired_device, wireless_device,
        account_type,
        sample_member, sample_member2, sample_member3,
        sample_vlan, sample_account, sample_membership])
    session.commit()


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
    assert r.chambre.id == body["room"]
    assert r.commentaires == body["comment"]
    assert r.login == body["username"]


def test_member_filter_all(api_client):
    r = api_client.get(
        '{}/member/'.format(base_url),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 4 # 4 because of the admin user


def test_member_filter_all_with_invalid_limit(api_client):
    r = api_client.get(
        '{}/member/?limit={}'.format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_member_filter_all_with_limit(api_client):
    r = api_client.get(
        '{}/member/?limit={}'.format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_by_room_id(api_client, sample_member):
    r = api_client.get(
        '{}/member/?filter[room]={}'.format(base_url, sample_member.chambre_id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 2


def test_member_filter_by_non_existant_id(api_client):
    r = api_client.get(
        '{}/member/?filter[room]={}'.format(base_url, 6666),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 0


def test_member_filter_terms_first_name(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "Jean"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_last_name(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "ubois"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_email(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "bgdu78"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_login(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "dubois_j"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_comment(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "routeur"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_filter_terms_nonexistant(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "azerty"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 0


def test_member_filter_terms_test_upper_case(api_client):
    r = api_client.get(
        '{}/member/?terms={}'.format(base_url, "DUBOIS_J"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 1


def test_member_get_existant(api_client, sample_member):
    r = api_client.get(
        '{}/member/{}'.format(base_url, sample_member.id),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.data.decode('utf-8'))


def test_member_get_nonexistant(api_client):
    r = api_client.get(
        '{}/member/{}'.format(base_url, 4242),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_member_delete_existant(api_client, sample_member):
    r = api_client.delete(
        '{}/member/{}'.format(base_url, sample_member.id),
        headers=TEST_HEADERS
    )
    assert r.status_code == 204
    assert_modification_was_created(db.session())

    s = db.session()
    q = s.query(Adherent)
    q = q.filter(Adherent.login == "dubois_j")
    assert not s.query(q.exists()).scalar()


def test_member_delete_non_existant(api_client):
    r = api_client.delete(
        '{}/member/{}'.format(base_url, 4242),
        headers=TEST_HEADERS
    )
    assert r.status_code == 404


def test_member_post_member_create_invalid_email(api_client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "room": 4592,
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "INVALID_EMAIL",
        "username": "doe_john"
    }
    res = api_client.post(
        '{}/member/'.format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 400


def test_member_post_member_create_unknown_room(api_client):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "room": 9999,
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "john.doe@gmail.com",
        "username": "doe_john"
    }
    res = api_client.post(
        '{}/member/'.format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 404 == res.status_code


def test_member_post_member_create(api_client, sample_room1):
    body = {
        "firstName": "John",
        "lastName": "Doe",
        "room": sample_room1.id,
        "comment": "comment",
        "departureDate": "2000-01-23T04:56:07.000+00:00",
        "email": "john.doe@gmail.com",
        "username": "doe_john"
    }
    res = api_client.post(
        '{}/member/'.format(base_url),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert 201 == res.status_code
    assert_modification_was_created(db.session())

    assert_member_in_db(body)


def test_member_patch_username(api_client, sample_member, sample_room1):
    body = {
        "username": "TESTTEST",
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "TESTTEST"
    })


def test_member_patch_email(api_client, sample_member, sample_room1):
    body = {
        "email": "TEST@TEST.FR",
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "TEST@TEST.FR",
        "username": "dubois_j"
    })


@mark.skip(reason="PATCH on member is not the way we should handle this")
def test_member_patch_associationmode(api_client, sample_member, sample_room1):
    body = {
        "associationMode": "1996-01-01T00:00:00Z",
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "dubois_j"
    })


def test_member_patch_departuredate(api_client, sample_member, sample_room1):
    body = {
        "departureDate": str(tomorrow),
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "dubois_j"
    })


def test_member_patch_comment(api_client, sample_member, sample_room1):
    body = {
        "comment": "TEST",
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": "TEST",
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "dubois_j"
    })


def test_member_patch_room(api_client, sample_member, sample_room2):
    body = {
        "room": sample_room2.id,
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room2.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "dubois_j"
    })


def test_member_patch_lastname(api_client, sample_member, sample_room1):
    body = {
        "lastName": "TEST",
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "Jean-Louis",
        "lastName": "TEST",
        "room": sample_room1.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "dubois_j"
    })


def test_member_patch_firstname(api_client, sample_member, sample_room1):
    body = {
        "firstName": "TEST",
    }
    res = api_client.patch(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 204
    assert_modification_was_created(db.session())
    assert_member_in_db({
        "firstName": "TEST",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": None,
        "departureDate": str(tomorrow),
        "email": "j.dubois@free.fr",
        "username": "dubois_j"
    })


def test_member_put_member_update(api_client, sample_member, sample_room1):
    body = {
        "firstName": "Jean-Louis",
        "lastName": "Dubois",
        "room": sample_room1.id,
        "comment": "comment",
        "departureDate": str(tomorrow),
        "email": "john.doe@gmail.com",
        "username": "dubois_j"
    }
    res = api_client.put(
        '{}/member/{}'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS
    )
    assert res.status_code == 201
    assert_modification_was_created(db.session())

    assert_member_in_db(body)


def test_member_get_logs(api_client, sample_member):
    body = {
        "dhcp": False,
    }
    result = api_client.get(
        '{}/member/{}/logs/'.format(base_url, sample_member.id),
        data=json.dumps(body),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert result.status_code == 200
    assert json.loads(result.data.decode('utf-8')) == ["1 test_log"]
