import json
from unittest.mock import AsyncMock, patch

import pytest
from adh6.network.storage.models import Port, Switch
from adh6.storage import db
from pytest_lazy_fixtures import lf

from test.integration.resource import TEST_HEADERS, base_url as host_url

base_url = f"{host_url}/port/"


@pytest.fixture
async def client(
    _test_client,
    sample_port1,
    sample_port2,
    sample_room1,
    sample_member,
    sample_switch1,
    sample_switch2,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_port1,
            sample_port2,
            sample_room1,
            sample_member,
            sample_switch1,
            sample_switch2,
        ]
    )

    yield _test_client

    await cleanup_test_data()


@pytest.fixture(autouse=True)
def discovered_ports():
    with patch("adh6.network.snmp.SwitchNetworkManager.discover_ports", new_callable=AsyncMock) as discover:
        discover.return_value = [{"portNumber": "1/0/4", "oid": "10104"}]
        yield discover


def assert_port_in_db(body):
    with db.sessionmaker.begin() as s:
        q = s.query(Port)
        q = q.filter(Port.numero == body["portNumber"])
        p = q.one()
        assert body["portNumber"] == p.numero
        assert body["room"] == p.chambre_id
        assert body["switchObj"] == p.switch_id


def test_port_get_filter_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    switches = json.loads(r.content.decode())
    assert switches
    assert len(switches) == 2


@pytest.mark.parametrize(
    "sample_only",
    [
        ("id"),
        ("portNumber"),
        ("oid"),
        ("switchObj"),
    ],
)
def test_port_search_with_only(client, sample_only: str):
    r = client.get(
        f"{base_url}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 2
    assert len({*sample_only.split(","), "id"}) == len(set(response[0].keys()))


def test_port_get_filter_all_with_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


@pytest.mark.parametrize("limit", [1, 2, 3])
def test_port_get_filter_all_with_limit(client, limit: int):
    r = client.get(
        f"{base_url}?limit={limit}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    ports = json.loads(r.content.decode())
    assert ports
    assert len(ports) == (min(limit, 2))


@pytest.fixture
def sample_switch2_id(sample_switch2: Switch):
    yield sample_switch2.id


@pytest.fixture
def sample_port1_room_id(sample_port1: Port):
    yield sample_port1.chambre_id


@pytest.mark.parametrize(
    "filter_name,filter_value,quantity",
    [
        ("switchObj", lf("sample_switch2_id"), 1),
        ("room", lf("sample_port1_room_id"), 2),
        ("room", 4242, 0),
    ],
)
def test_port_get_filter_by_filter(client, filter_name, filter_value, quantity: int):
    r = client.get(f"{base_url}?filter[{filter_name}]={filter_value}", headers=TEST_HEADERS)
    assert r.status_code == 200
    ports = json.loads(r.content.decode())
    assert len(ports) == quantity


@pytest.mark.parametrize("term", ["1.2", "0/0/1"])
def test_port_get_filter_by_term(client, term: str):
    r = client.get(
        f"{base_url}?terms={term}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    ports = json.loads(r.content.decode())
    assert ports
    assert len(ports) == 1


def test_port_post_create_port_invalid_switch(client, sample_room1):
    body = {
        "room": sample_room1.id,
        "switchObj": 4242,
        "portNumber": "1/0/4",
        "oid": "10104",
    }

    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_port_post_create_port_invalid_room(client, sample_switch1):
    body = {
        "room": 4242,
        "switchObj": sample_switch1.id,
        "portNumber": "1/0/4",
        "oid": "10104",
    }

    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_port_post_create_port(client, sample_switch1, sample_room1):
    body = {
        "room": sample_room1.id,
        "switchObj": sample_switch1.id,
        "portNumber": "1/0/4",
        "oid": "10104",
    }

    r = client.post(
        base_url,
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201


def test_port_get_existant_port(client, sample_port1):
    r = client.get(
        f"{base_url}{sample_port1.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    switch = json.loads(r.content.decode())
    assert switch


def test_port_get_non_existant_port(client):
    r = client.get(
        f"{base_url}{4242}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


@pytest.fixture
def sample_ports1_id(sample_port1: Port):
    yield sample_port1.id


@pytest.mark.parametrize(
    "port_id,key,value,status_code",
    [
        (lf("sample_ports1_id"), "switchObj", 999, 404),
        (4242, None, None, 404),
        (lf("sample_ports1_id"), "portNumber", "1/2/3", 204),
    ],
)
def test_port_put_update_port(
    client,
    sample_switch1: Switch,
    sample_port1: Port,
    port_id: int,
    key: str,
    value,
    status_code: int,
):
    body = {
        "room": sample_port1.chambre_id,
        "oid": sample_port1.oid,
        "switchObj": sample_switch1.id,
        "portNumber": sample_port1.numero,
    }

    if key is not None:
        body[key] = value
        if key == "switchObj":
            body["oid"] = "10104"

    r = client.put(
        f"{base_url}{port_id}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == status_code
    if r.status_code == 204:
        assert_port_in_db(body)


@pytest.mark.parametrize("port_id, status_code", [(lf("sample_ports1_id"), 204), (4242, 404)])
def test_port_delete_port(client, port_id: int, status_code: int):
    r = client.delete(
        f"{base_url}{port_id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == status_code

    if status_code == 204:
        s = db.session
        q = s.query(Port)
        q = q.filter(Port.id == port_id)
        assert not s.query(q.exists()).scalar()


def test_duplicate_create_returns_conflict(client, sample_switch1, discovered_ports):
    body = {"switchObj": sample_switch1.id, "oid": "10104", "portNumber": "wrong name", "room": None}
    first = client.post(base_url, json=body, headers=TEST_HEADERS)
    assert first.status_code == 201
    assert first.json()["portNumber"] == "1/0/4"
    duplicate = client.post(base_url, json=body, headers=TEST_HEADERS)
    assert duplicate.status_code == 409


@pytest.mark.parametrize("oid", ["Gi1/0/1", "0", "1.2.3", "10105"])
def test_invalid_or_undiscovered_oid_is_rejected(client, sample_switch1, oid):
    response = client.post(
        base_url, json={"switchObj": sample_switch1.id, "oid": oid, "portNumber": "Gi1/0/1"}, headers=TEST_HEADERS
    )
    assert response.status_code == 400


def test_discovery_failure_does_not_block_assignment_of_existing_port(
    client, sample_port1, sample_room1, discovered_ports
):
    from adh6.exceptions import NetworkManagerReadError

    discovered_ports.side_effect = NetworkManagerReadError("unreachable")
    response = client.patch(
        f"{base_url}{sample_port1.id}/room",
        json={"room": sample_room1.id, "expectedRoom": sample_room1.id},
        headers=TEST_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["oid"] == sample_port1.oid
    discovered_ports.assert_not_awaited()
    response = client.post(base_url, json={"switchObj": 1, "oid": "10104", "portNumber": "1/0/4"}, headers=TEST_HEADERS)
    assert response.status_code == 502


def test_bulk_duplicate_does_not_rollback_other_ports(client):
    body = {"switchObj": 1, "oid": "10104", "portNumber": "1/0/4"}
    response = client.post(f"{base_url}bulk", json=[body, body], headers=TEST_HEADERS)
    assert response.status_code == 200
    assert response.json()["success"] == 1
    assert response.json()["failed"] == 1
    ports = client.get(base_url, headers=TEST_HEADERS).json()
    assert len([port for port in ports if port["oid"] == "10104"]) == 1


def test_repeated_assignment_to_same_room_is_idempotent(client, sample_port1, sample_room1):
    response = client.patch(
        f"{base_url}{sample_port1.id}/room", json={"room": sample_room1.id, "expectedRoom": None}, headers=TEST_HEADERS
    )
    assert response.status_code == 200


@pytest.mark.parametrize("body", [{"room": 1}, {"room": 0, "expectedRoom": None}, {"room": 1, "expectedRoom": 0}])
def test_assignment_requires_valid_target_and_expected_room(client, sample_port1, body):
    response = client.patch(f"{base_url}{sample_port1.id}/room", json=body, headers=TEST_HEADERS)
    assert response.status_code == 400


async def test_transfer_conflict_then_confirmed_transfer(client, sample_port1, sample_room1):
    from adh6.room.storage.models import Chambre

    from .conftest import add_test_fixtures

    await add_test_fixtures([Chambre(id=900, numero=5900)])
    url = f"{base_url}{sample_port1.id}/room"
    stale = client.patch(url, json={"room": 900, "expectedRoom": None}, headers=TEST_HEADERS)
    assert stale.status_code == 409
    assert client.get(f"{base_url}{sample_port1.id}", headers=TEST_HEADERS).json()["room"] == sample_room1.id
    transfer = client.patch(url, json={"room": 900, "expectedRoom": sample_room1.id}, headers=TEST_HEADERS)
    assert transfer.status_code == 200
    assert transfer.json()["room"] == 900
    assert transfer.json()["roomObj"]["roomNumber"] == 5900
    assert transfer.json()["oid"] == sample_port1.oid
    assert transfer.json()["portNumber"] == sample_port1.numero


def test_detach_preserves_port_and_does_not_require_snmp(client, sample_port1, sample_room1, discovered_ports):
    from adh6.exceptions import NetworkManagerReadError

    discovered_ports.side_effect = NetworkManagerReadError("unreachable")
    response = client.patch(
        f"{base_url}{sample_port1.id}/room", json={"room": None, "expectedRoom": sample_room1.id}, headers=TEST_HEADERS
    )
    assert response.status_code == 200
    assert response.json()["room"] is None
    stored = client.get(f"{base_url}{sample_port1.id}", headers=TEST_HEADERS)
    assert stored.status_code == 200
    assert stored.json()["oid"] == sample_port1.oid
    assert stored.json()["switchObj"] == sample_port1.switch_id
    assert stored.json()["room"] is None
    discovered_ports.assert_not_awaited()
