import json
from ipaddress import IPv4Address, IPv4Network

import pytest
from adh6.device.storage.device_repository import DeviceType
from adh6.device.storage.models import Device
from adh6.member.storage.models import Adherent
from adh6.room.storage.models import Chambre
from adh6.storage import db
from sqlalchemy import select

from test.integration.resource import (
    TEST_HEADERS,
    TEST_HEADERS_SAMPLE,
    base_url as host_url,
)

base_url = f"{host_url}/room/"


@pytest.fixture
async def client(
    _test_client,
    sample_room1,
    sample_room2,
    sample_vlan,
    sample_vlan69,
    sample_member,
    wired_device,
    wireless_device,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_room1,
            sample_room2,
            sample_vlan69,
            sample_vlan,
            sample_member,
            wired_device,
            wireless_device,
        ]
    )

    yield _test_client

    await cleanup_test_data()


def assert_room_in_db(body):
    with db.sessionmaker.begin() as s:
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
    response = json.loads(r.content.decode())
    assert len(response) == 2


@pytest.mark.parametrize(
    "sample_only",
    [
        ("id"),
        ("roomNumber"),
        ("vlan"),
        ("description"),
    ],
)
def test_room_search_with_only(client, sample_only: str):
    r = client.get(
        f"{base_url}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 2
    assert len({*sample_only.split(","), "id"}) == len(set(response[0].keys()))


def test_room_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f"{base_url}?only={sample_only}",
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
    response = json.loads(r.content.decode())
    assert len(response) == 1


def test_room_filter_by_term(client, sample_room1):
    r = client.get(
        f"{base_url}?terms={sample_room1.description}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode())
    assert len(response) == 1


def test_room_get_valid_room(client, sample_room1):
    r = client.get(
        f"{base_url}{sample_room1.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode())
    assert len(response) == 4


def test_room_get_invalid_room(client):
    r = client.get(
        f"{base_url}{4900}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_post_new_room_invalid_vlan(client):
    room = {"roomNumber": 4285, "vlan": 45, "description": "Chambre 4285"}
    r = client.post(
        base_url,
        data=json.dumps(room),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_room_post_new_room(client, sample_vlan):
    room = {
        "roomNumber": 4285,
        "vlan": sample_vlan.numero,
        "description": "Chambre 4285",
    }
    r = client.post(
        base_url,
        data=json.dumps(room),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201
    assert_room_in_db(room)


def test_room_put_update_room(client, sample_room1, sample_vlan):
    room = {
        "vlan": sample_vlan.numero,
        "roomNumber": 4285,
        "description": "Chambre 4285",
    }
    r = client.put(
        f"{base_url}{sample_room1.id}",
        data=json.dumps(room),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    assert_room_in_db(room)


def test_room_delete_existant_room(client, sample_room1):
    r = client.delete(
        f"{base_url}{sample_room1.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    s = db.session
    q = s.query(Chambre)
    q = q.filter(Chambre.id == sample_room1.id)
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
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_room_add_member_unknown_member(client, sample_room1):
    r = client.post(
        f"{base_url}{sample_room1.id}/member/",
        data=json.dumps({"id": 4242}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_room_add_member(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204


def test_room_member_not_in_room(client, sample_member):
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_member_in_room(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == sample_room1.id


def test_room_add_member_change_vlan_check_wired(
    client, sample_room1, sample_room2, sample_member, sample_vlan, sample_vlan69
):
    r = client.post(
        f"{base_url}{sample_room2.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    assert IPv4Address(
        db.session.execute(
            select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))
        ).scalar()
    ) in IPv4Network(sample_vlan69.adresses)
    r = client.post(
        f"{base_url}{sample_room1.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    assert IPv4Address(
        db.session.execute(
            select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))
        ).scalar()
    ) in IPv4Network(sample_vlan.adresses)


def test_room_add_member_when_no_room(client, sample_room1, sample_room2, sample_member, sample_vlan69):
    r = client.delete(
        f"{base_url}{sample_room1.id}/member/?memberId={sample_member.id}",
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    with db.sessionmaker.begin() as s:
        assert s.execute(select(Adherent.subnet).where(Adherent.id == sample_member.id)).scalar() is None
        assert (
            s.execute(
                select(Device.ip).where(
                    (Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value)
                )
            ).scalar()
            == "En attente"
        )
    r = client.post(
        f"{base_url}{sample_room2.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    assert IPv4Address(
        db.session.execute(
            select(Device.ip).where((Device.adherent_id == sample_member.id) & (Device.type == DeviceType.wired.value))
        ).scalar()
    ) in IPv4Network(sample_vlan69.adresses)


def test_room_member_in_room_user_authorized(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}member/{sample_member.id}",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == sample_room1.id


def test_room_delete_member_unknown_room(client, sample_member):
    r = client.delete(
        f"{base_url}{4242}/member/?memberId={sample_member.id}",
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_room_delete_member_unknown_member(client, sample_room1):
    r = client.delete(
        f"{base_url}{sample_room1.id}/member/?memberId=4242",
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_room_delete_member(client, sample_room1, sample_member):
    r = client.delete(
        f"{base_url}{sample_room1.id}/member/?memberId={sample_member.id}",
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204


def test_room_delete_member_unauthorized(client, sample_room1, sample_member):
    r = client.delete(
        f"{base_url}{sample_room1.id}/member/?memberId={sample_member.id}",
        params=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS_SAMPLE},
    )
    assert r.status_code == 403


def test_room_list_member(client, sample_room1, sample_member):
    r = client.post(
        f"{base_url}{sample_room1.id}/member/",
        data=json.dumps({"id": sample_member.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    r = client.get(
        f"{base_url}{sample_room1.id}/member/",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.content.decode("utf-8"))
    assert response == [sample_member.id]


def test_room_list_member_unauthorized_user(client, sample_room1):
    r = client.get(
        f"{base_url}{sample_room1.id}/member/",
        headers=TEST_HEADERS_SAMPLE,
    )
    assert r.status_code == 403
