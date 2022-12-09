from ipaddress import IPv4Address, IPv4Network
import json
import pytest
from sqlalchemy import select
from adh6.device.enums import DeviceType

from adh6.storage import  db
from adh6.member.storage.models import Adherent
from adh6.device.storage.models import Device
from adh6.room.storage.models import Chambre
from test.integration.resource import TEST_HEADERS, TEST_HEADERS_SAMPLE, base_url as host_url


base_url = f'{host_url}/room/'


@pytest.fixture
def client(sample_room1,
           sample_room2,
           sample_vlan,
           sample_vlan69,
           sample_member,
           wired_device,
           wireless_device):
    from .context import app
    from .conftest import prep_db, close_db
    if app.app is None:
        return
    with app.app.test_client() as c:
        prep_db(
            sample_room1,
            sample_room2,
            sample_vlan69,
            sample_vlan,
            sample_member,
            wired_device,
            wireless_device
        )
        yield c
        close_db()


def assert_room_in_db(body):
    s = db.session()
    q = s.query(Chambre)
    q = q.filter(body["roomNumber"] == Chambre.numero)
    c = q.one()
    assert body["description"] == c.description


def test_room_filter_all_rooms(client):
    r = client.get(
        base_url,
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 2


@pytest.mark.parametrize(
    'sample_only', 
    [
        ("id"),
        ("roomNumber"),
        ("vlan"),
        ("description"),
    ])
def test_room_search_with_only(client, sample_only: str):
    r = client.get(
        f'{base_url}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.data.decode('utf-8'))
    assert len(response) == 2
    assert len(set(sample_only.split(",") + ["id"])) == len(set(response[0].keys()))


def test_room_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f'{base_url}?only={sample_only}',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_room_filter_all_rooms_limit_invalid(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_room_filter_all_rooms_limit(client):
    r = client.get(
        f"{base_url}?limit={1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 1


def test_room_filter_by_term(client, sample_room1):
    r = client.get(
        f"{base_url}?terms={sample_room1.description}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 1


def test_room_get_valid_room(client, sample_room1):
    r = client.get(
        f"{base_url}{sample_room1.numero}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 4


def test_room_get_invalid_room(client):
    r = client.get(
        f"{base_url}{4900}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_post_new_room_invalid_vlan(client):
    room = {
        "roomNumber": 5111,
        "vlan": 45,
        "description": "Chambre 5111"
    }
    r = client.post(
        base_url,
        data=json.dumps(room),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_post_new_room(client, sample_vlan):
    room = {
        "roomNumber": 5111,
        "vlan": sample_vlan.numero,
        "description": "Chambre 5111",
    }
    r = client.post(
        base_url,
        data=json.dumps(room),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 201
    assert_room_in_db(room)


def test_room_put_update_room(client, sample_room1, sample_vlan):
    room = {
        "vlan": sample_vlan.numero,
        "roomNumber": 5111,
        "description": "Chambre 5111"
    }
    r = client.put(
        f"{base_url}{sample_room1.numero}",
        data=json.dumps(room),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert_room_in_db(room)


def test_room_delete_existant_room(client, sample_room1):
    r = client.delete(
        f"{base_url}{sample_room1.numero}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    s = db.session()
    q = s.query(Chambre)
    q = q.filter(Chambre.numero == sample_room1.numero)
    assert q.count() == 0


def test_room_delete_non_existant_room(client):
    r = client.delete(
        f"{base_url}{4900}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_add_member_unknown_room(client, sample_member):
    r = client.post(
        f"{base_url}{4242}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_add_member_unknown_member(client, sample_room1):
    r = client.post(
        f"{base_url}{sample_room1.numero}/member/",
        data=json.dumps({"login": "4242"}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_add_member(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204


def test_room_member_not_in_room(client, sample_member):
    r = client.get(
        f"{base_url}member/{sample_member.login}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_member_in_room(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}member/{sample_member.login}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert response == sample_room1.numero


def test_room_add_member_change_vlan_check_wired(client, sample_room1, sample_room2, sample_member, sample_vlan, sample_vlan69):
    r = client.post(
        f"{base_url}{sample_room2.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert IPv4Address(db.session().execute(select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))).scalar()) in IPv4Network(sample_vlan69.adresses)
    r = client.post(
        f"{base_url}{sample_room1.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert IPv4Address(db.session().execute(select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))).scalar()) in IPv4Network(sample_vlan.adresses)


def test_room_add_member_when_no_room(client, sample_room1, sample_room2, sample_member, sample_vlan69):
    r = client.delete(
        f"{base_url}member/{sample_member.login}",
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert db.session().execute(select(Adherent.subnet).where(Adherent.id == sample_member.id)).scalar() is None
    assert db.session().execute(select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))).scalar() == 'En attente'
    r = client.post(
        f"{base_url}{sample_room2.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert IPv4Address(db.session().execute(select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))).scalar()) in IPv4Network(sample_vlan69.adresses)


def test_room_member_in_room_user_authorized(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}member/{sample_member.login}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert response == sample_room1.numero


def test_room_delete_member_unknown_member(client):
    r = client.delete(
        f"{base_url}member/4242",
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_delete_member(client, sample_member):
    r = client.delete(
        f"{base_url}member/{sample_member.login}",
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204


def test_room_delete_member_unauthorized(client, sample_member):
    r = client.delete(
        f"{base_url}member/{sample_member.login}",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403


def test_room_list_member(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.numero}/member/",
        data=json.dumps({"login": sample_member.login}),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}{sample_room1.numero}/member/",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode('utf-8'))
    assert response == [sample_member.login] 


def test_room_list_member_unauthorized_user(client, sample_room1):
    r = client.get(
        f"{base_url}{sample_room1.numero}/member/",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
