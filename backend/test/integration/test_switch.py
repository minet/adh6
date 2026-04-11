import json
from unittest.mock import AsyncMock, patch

import pytest
from adh6.network.storage.models import Port, Switch
from adh6.room.storage.models import Chambre
from adh6.storage import db
from adh6.subnet.storage.models import Vlan

from test.integration.resource import INVALID_IP, TEST_HEADERS, base_url as host_url

base_url = f"{host_url}/switch/"


@pytest.fixture
def sample_switch():
    yield Switch(
        id=1,
        description="Switch",
        ip="192.168.102.2",
        communaute="communaute",
    )


@pytest.fixture
async def client(_test_client, sample_switch1):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures([sample_switch1])

    yield _test_client

    await cleanup_test_data()


def assert_switch_in_db(body):
    with db.sessionmaker.begin() as s:
        q = s.query(Switch)
        q = q.filter(Switch.ip == body["ip"])
        sw = q.one()
        assert sw.ip == body["ip"]
        assert sw.communaute == body["community"]
        assert sw.description == body["description"]


@pytest.mark.parametrize("test_ip", INVALID_IP)
def test_switch_post_invalid_ip(client, test_ip):
    sample_switch1 = {
        "description": "Test Switch",
        "ip": test_ip,
        "community": "myGreatCommunity",
    }
    r = client.post(
        f"{base_url}",
        data=json.dumps(sample_switch1),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_switch_post_valid(client):
    sample_switch1 = {
        "description": "Test Switch",
        "ip": "192.168.103.128",
        "community": "myGreatCommunity",
    }

    # Insert data to the database
    r = client.post(
        f"{base_url}",
        data=json.dumps(sample_switch1),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 201
    assert_switch_in_db(sample_switch1)


@pytest.mark.parametrize(
    "sample_only",
    [
        ("id"),
        ("ip"),
        ("description"),
    ],
)
def test_switch_search_with_only(client, sample_only: str):
    r = client.get(
        f"{base_url}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1
    assert len({*sample_only.split(","), "id"}) == len(set(response[0].keys()))


def test_switch_search_with_unknown_only(client):
    sample_only = "azerty"
    r = client.get(
        f"{base_url}?only={sample_only}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_switch_get_all_invalid_limit(client):
    r = client.get(
        f"{base_url}?limit={-1}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_switch_get_all_limit(client):
    r = client.get(
        f"{base_url}?limit={0}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert len(t) == 0


def test_switch_get_all(client):
    r = client.get(
        f"{base_url}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    t = json.loads(r.content.decode("utf-8"))
    assert t
    assert len(t) == 1


def test_switch_get_existant_switch(client, sample_switch1):
    r = client.get(
        f"{base_url}{sample_switch1.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8"))


def test_switch_get_non_existant_switch(client):
    r = client.get(
        f"{base_url}{100000}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_switch_filter_by_term_ip(client):
    terms = "102.51"
    r = client.get(
        f"{base_url}?terms={terms}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result
    assert len(result) == 1


def test_switch_filter_by_term_desc(client):
    terms = "Switch"
    r = client.get(
        f"{base_url}?terms={terms}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result
    assert len(result) == 1


def test_switch_filter_by_term_nonexistant(client):
    terms = "HEYO"
    r = client.get(
        f"{base_url}?terms={terms}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert not result


def test_member_filter_by_switch_id(client, sample_switch1: Switch):
    r = client.get(
        f"{base_url}?filter[id]={sample_switch1.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_by_unknown_switch_id(client):
    r = client.get(
        f"{base_url}?filter[id]={100000}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 0


def test_member_filter_by_switch_ip(client, sample_switch1: Switch):
    r = client.get(
        f"{base_url}?filter[ip]={sample_switch1.ip}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_by_unknown_switch_ip(client):
    r = client.get(
        f"{base_url}?filter[ip]={'192.168.102.1'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 0


def test_member_filter_by_switch_description(client, sample_switch1: Switch):
    r = client.get(
        f"{base_url}?filter[description]={sample_switch1.description}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 1


def test_member_filter_by_unknown_switch_description(client):
    r = client.get(
        f"{base_url}?filter[description]={'192.168.102.1'}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200

    response = json.loads(r.content.decode("utf-8"))
    assert len(response) == 0


@pytest.mark.parametrize("test_ip", INVALID_IP)
def test_switch_update_switch_invalid_ip(client, test_ip):
    sample_switch1 = {
        "description": "Modified switch",
        "ip": test_ip,
        "community": "communityModified",
    }

    r = client.put(
        f"{base_url}{1}",
        data=json.dumps(sample_switch1),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_switch_update_existant_switch(client, sample_switch1: Switch):
    sample_switch1_changed = {
        "description": "Modified switch",
        "ip": "192.168.103.132",
        "community": "communityModified",
    }

    r = client.put(
        f"{base_url}{sample_switch1.id}",
        data=json.dumps(sample_switch1_changed),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204
    assert_switch_in_db(sample_switch1_changed)


def test_switch_update_non_existant_switch(client):
    sample_switch1 = {
        "description": "Modified switch",
        "ip": "192.168.103.132",
        "community": "communityModified",
    }

    r = client.put(
        f"{base_url}{100000}",
        data=json.dumps(sample_switch1),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_switch_delete_existant_switch(client, sample_switch1: Switch):
    r = client.delete(f"{base_url}{sample_switch1.id}", headers=TEST_HEADERS)
    assert r.status_code == 204
    s = db.session
    q = s.query(Switch)
    q = q.filter(Switch.id == sample_switch1.id)

    assert not s.query(q.exists()).scalar()


def test_switch_delete_non_existant_switch(client):
    r = client.delete(f"{base_url}{10000}", headers=TEST_HEADERS)
    assert r.status_code == 404


# ============================================================================
# Bulk Action Endpoint Tests
# ============================================================================


def test_switch_apply_descriptions_non_existent(client):
    """apply-descriptions returns 404 when switch does not exist."""
    r = client.post(f"{base_url}{100000}/apply-descriptions", headers=TEST_HEADERS)
    assert r.status_code == 404


def test_switch_apply_vlans_non_existent(client):
    """apply-vlans returns 404 when switch does not exist."""
    r = client.post(
        f"{base_url}{100000}/apply-vlans",
        data=json.dumps(42),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


def test_switch_apply_descriptions_no_ports(client, sample_switch1):
    """apply-descriptions returns success/failed counts when switch has no room-linked ports."""
    r = client.post(f"{base_url}{sample_switch1.id}/apply-descriptions", headers=TEST_HEADERS)
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["success"] == 0
    assert result["failed"] == 0
    assert result["errors"] == []


def test_switch_apply_vlans_no_ports(client, sample_switch1):
    """apply-vlans returns success/failed counts when switch has no room-linked ports."""
    r = client.post(
        f"{base_url}{sample_switch1.id}/apply-vlans",
        data=json.dumps(42),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["success"] == 0
    assert result["failed"] == 0
    assert result["errors"] == []


@pytest.fixture
async def client_with_port_no_room(_test_client, sample_switch1):
    """Client fixture with a switch that has a port with no room assigned."""
    from adh6.network.storage.models import Port

    from .conftest import add_test_fixtures, cleanup_test_data

    port_no_room = Port(
        rcom=None,
        numero="0/1/1",
        oid="2.2.2",
        switch_id=sample_switch1.id,
        chambre_id=None,
    )
    await add_test_fixtures([sample_switch1, port_no_room])
    yield _test_client
    await cleanup_test_data()


def test_switch_apply_descriptions_port_without_room(client_with_port_no_room, sample_switch1):
    """apply-descriptions skips ports with no room assigned."""
    r = client_with_port_no_room.post(
        f"{base_url}{sample_switch1.id}/apply-descriptions",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["success"] == 0
    assert result["failed"] == 0
    assert result["errors"] == []


def test_switch_apply_vlans_port_without_room(client_with_port_no_room, sample_switch1):
    """apply-vlans skips ports with no room assigned."""
    r = client_with_port_no_room.post(
        f"{base_url}{sample_switch1.id}/apply-vlans",
        data=json.dumps(42),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["success"] == 0
    assert result["failed"] == 0
    assert result["errors"] == []


@pytest.fixture
async def client_with_port_and_room(_test_client, sample_switch1):
    """Client fixture with a switch that has a port linked to a room (SNMP will fail, caught by handler)."""
    from .conftest import add_test_fixtures, cleanup_test_data

    vlan = Vlan(id=42, numero=42, adresses="192.168.42.0/24", adressesv6="fe80:42::0/64")
    room = Chambre(id=420, numero=5110, description="Chambre test", vlan_id=vlan.id)
    port = Port(rcom=1, numero="0/1/2", oid="3.3.3", switch_id=sample_switch1.id, chambre_id=room.id)
    await add_test_fixtures([vlan, room, sample_switch1, port])
    yield _test_client
    await cleanup_test_data()


def test_switch_apply_descriptions_snmp_failure_counted(client_with_port_and_room, sample_switch1):
    """apply-descriptions counts SNMP failures when ports have rooms but switch is unreachable."""
    r = client_with_port_and_room.post(
        f"{base_url}{sample_switch1.id}/apply-descriptions",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    # SNMP will fail in test env — reported as failure, not a 500
    assert result["success"] == 0
    assert result["failed"] == 1
    assert len(result["errors"]) == 1


def test_switch_apply_vlans_updates_room_in_db(client_with_port_and_room, sample_switch1):
    """apply-vlans updates the room's VLAN in the database (vlan numero=42 exists in fixture)."""
    r = client_with_port_and_room.post(
        f"{base_url}{sample_switch1.id}/apply-vlans",
        data=json.dumps(42),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["success"] == 1
    assert result["failed"] == 0
    assert result["errors"] == []


def test_switch_apply_vlans_unknown_vlan_counted_as_failure(client_with_port_and_room, sample_switch1):
    """apply-vlans counts rooms as failed when the requested VLAN does not exist in DB."""
    r = client_with_port_and_room.post(
        f"{base_url}{sample_switch1.id}/apply-vlans",
        data=json.dumps(9999),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["success"] == 0
    assert result["failed"] == 1
    assert len(result["errors"]) == 1


# ============================================================================
# Ping Endpoint Tests
# ============================================================================


def test_switch_ping_non_existent(client):
    """ping returns 404 when switch does not exist."""
    r = client.post(
        f"{base_url}{100000}/ping",
        data=json.dumps({"address": "192.168.1.1"}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 404


@pytest.mark.parametrize("test_ip", ["not-an-ip", "999.999.999.999", "192.168.0.0/24"])
def test_switch_ping_invalid_ip(client, test_ip):
    """ping returns 400 for an invalid IP address."""
    r = client.post(
        f"{base_url}{1}/ping",
        data=json.dumps({"address": test_ip}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_switch_ping_snmp_failure(client, sample_switch1):
    """ping returns 502 when the switch is unreachable via SNMP."""
    r = client.post(
        f"{base_url}{sample_switch1.id}/ping",
        data=json.dumps({"address": "192.168.1.1", "count": 1, "timeoutMs": 100}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 502


def test_switch_ping_success_mocked(client, sample_switch1):
    """ping returns 200 with correct RTT stats when SNMP succeeds (mocked)."""
    # get_snmp_value_raw call order: 1x poll-completed, then sent/received/min/avg/max
    snmp_get_responses = ["true", "5", "4", "10", "15", "20"]
    with (
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_values_raw",
            AsyncMock(return_value=None),
        ),
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value_raw",
            AsyncMock(side_effect=snmp_get_responses),
        ),
        patch("asyncio.sleep", AsyncMock(return_value=None)),
    ):
        r = client.post(
            f"{base_url}{sample_switch1.id}/ping",
            data=json.dumps({"address": "192.168.1.1", "count": 5, "timeoutMs": 100}),
            headers={"Content-Type": "application/json", **TEST_HEADERS},
        )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["sent"] == 5
    assert result["received"] == 4
    assert result["minRtt"] == 10
    assert result["avgRtt"] == 15
    assert result["maxRtt"] == 20


def test_switch_ping_zero_received_mocked(client, sample_switch1):
    """ping returns 200 with zero RTT stats when no packets are received."""
    # Simulate: completed=true, sent=5, received=0, rtt columns all 0
    snmp_get_responses = ["true", "5", "0", "0", "0", "0"]
    with (
        patch(
            "adh6.network.snmp.switch_network_manager.set_snmp_values_raw",
            AsyncMock(return_value=None),
        ),
        patch(
            "adh6.network.snmp.switch_network_manager.get_snmp_value_raw",
            AsyncMock(side_effect=snmp_get_responses),
        ),
        patch("asyncio.sleep", AsyncMock(return_value=None)),
    ):
        r = client.post(
            f"{base_url}{sample_switch1.id}/ping",
            data=json.dumps({"address": "192.168.1.1", "count": 5, "timeoutMs": 100}),
            headers={"Content-Type": "application/json", **TEST_HEADERS},
        )
    assert r.status_code == 200
    result = json.loads(r.content.decode("utf-8"))
    assert result["sent"] == 5
    assert result["received"] == 0
    assert result["minRtt"] == 0
    assert result["avgRtt"] == 0
    assert result["maxRtt"] == 0
