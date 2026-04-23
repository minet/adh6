"""Tests for permanent and wifi_only member flags."""

import json
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.member.storage.models import Adherent, Membership
from adh6.room.storage.models import RoomMemberLink

from test.integration.context import tomorrow
from test.integration.resource import TEST_HEADERS, base_url as host_url

member_url = f"{host_url}/member/"
room_url = f"{host_url}/room/"
device_url = f"{host_url}/device/"


# ── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def wifi_only_member(sample_room1):
    """Member with wifi_only=True, assigned to a room so room-check doesn't interfere with wired test."""
    yield Adherent(
        id=50,
        nom="WifiOnly",
        prenom="Test",
        mail="wifionly@test.net",
        login="wifionly_test",
        password="a",
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        mail_membership=1,
        wifi_only=True,
    )


@pytest.fixture
def wifi_only_member_no_room():
    """Member with wifi_only=True, no room."""
    yield Adherent(
        id=51,
        nom="WifiOnlyNoRoom",
        prenom="Test",
        mail="wifionly2@test.net",
        login="wifionly_noroom",
        password="a",
        date_de_depart=tomorrow,
        mail_membership=1,
        wifi_only=True,
    )


@pytest.fixture
def permanent_member():
    """Member with permanent=True, expired departure_date."""
    yield Adherent(
        id=52,
        nom="Permanent",
        prenom="Test",
        mail="permanent@test.net",
        login="permanent_test",
        password="a",
        date_de_depart=datetime.now() - timedelta(days=365),  # expired
        mail_membership=1,
        permanent=True,
    )


@pytest.fixture
def pending_membership_wifi_only(wifi_only_member: Adherent):
    yield Membership(
        uuid=str(uuid4()),
        adherent_id=wifi_only_member.id,
        duration=MembershipDuration.ONE_YEAR,
        status=MembershipStatus.PENDING_PAYMENT,
        has_room=True,
    )


# ── client fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
async def client_wifi_only(
    _test_client,
    wifi_only_member,
    wifi_only_member_no_room,
    permanent_member,
    sample_room1,
    sample_vlan,
    pending_membership_wifi_only,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_vlan,
            sample_room1,
            wifi_only_member,
            wifi_only_member_no_room,
            permanent_member,
            pending_membership_wifi_only,
        ]
    )

    yield _test_client

    await cleanup_test_data()


# ── permanent account tests ──────────────────────────────────────────────────


def test_permanent_member_get_returns_permanent_flag(client_wifi_only, permanent_member: Adherent):
    """Permanent flag visible in GET response."""
    r = client_wifi_only.get(
        f"{member_url}{permanent_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    body = json.loads(r.content.decode("utf-8"))
    assert body.get("permanent") is True


def test_permanent_member_patch_sets_flag(client_wifi_only, permanent_member: Adherent):
    """PATCH member with permanent=False clears flag."""
    r = client_wifi_only.patch(
        f"{member_url}{permanent_member.id}",
        data=json.dumps({"permanent": False}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204

    r2 = client_wifi_only.get(f"{member_url}{permanent_member.id}", headers=TEST_HEADERS)
    body = json.loads(r2.content.decode("utf-8"))
    assert body.get("permanent") is False


# ── wifi_only device restriction tests ──────────────────────────────────────


def test_wifi_only_member_cannot_add_wired_device(client_wifi_only, wifi_only_member: Adherent):
    """wifi_only member POST wired device → 400."""
    body = {
        "mac": "AA-BB-CC-DD-EE-01",
        "connectionType": "wired",
        "member": wifi_only_member.id,
    }
    r = client_wifi_only.post(
        f"{device_url}",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


def test_wifi_only_flag_visible_in_member_get(client_wifi_only, wifi_only_member: Adherent):
    """wifiOnly flag visible in GET response."""
    r = client_wifi_only.get(
        f"{member_url}{wifi_only_member.id}",
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    body = json.loads(r.content.decode("utf-8"))
    assert body.get("wifiOnly") is True


# ── wifi_only room restriction tests ────────────────────────────────────────


def test_wifi_only_member_cannot_be_assigned_to_room(
    client_wifi_only, sample_room1, wifi_only_member_no_room: Adherent
):
    """POST room member for wifi_only member → 400."""
    r = client_wifi_only.post(
        f"{room_url}{sample_room1.id}/member/",
        data=json.dumps({"id": wifi_only_member_no_room.id}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


# ── wifi_only subscription restriction tests ─────────────────────────────────


def test_wifi_only_member_cannot_patch_subscription(client_wifi_only, wifi_only_member: Adherent):
    """PATCH subscription for wifi_only member → 400."""
    body = {
        "member": wifi_only_member.id,
        "duration": MembershipDuration.ONE_YEAR.value,
    }
    r = client_wifi_only.patch(
        f"{member_url}{wifi_only_member.id}/subscription/",
        data=json.dumps(body),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 400


# ── wifi status endpoint ─────────────────────────────────────────────────────


def test_wifi_status_endpoint_returns_true_for_wifi_only(client_wifi_only, wifi_only_member: Adherent):
    """GET /member/{id}/wifi returns wifiOnly=true for wifi_only member."""
    r = client_wifi_only.get(f"{member_url}{wifi_only_member.id}/wifi", headers=TEST_HEADERS)
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8")) == {"wifiOnly": True}


def test_wifi_status_endpoint_returns_false_for_normal_member(client_wifi_only, permanent_member: Adherent):
    """GET /member/{id}/wifi returns wifiOnly=false for non-wifi-only member."""
    r = client_wifi_only.get(f"{member_url}{permanent_member.id}/wifi", headers=TEST_HEADERS)
    assert r.status_code == 200
    assert json.loads(r.content.decode("utf-8")) == {"wifiOnly": False}


def test_wifi_status_endpoint_returns_404_for_unknown_member(client_wifi_only):
    """GET /member/{id}/wifi returns 404 for nonexistent member."""
    r = client_wifi_only.get(f"{member_url}99999/wifi", headers=TEST_HEADERS)
    assert r.status_code == 404


# ── patch sets wifi_only flag ────────────────────────────────────────────────


def test_patch_member_sets_wifi_only_flag(client_wifi_only, permanent_member: Adherent):
    """PATCH member with wifiOnly=True persists."""
    r = client_wifi_only.patch(
        f"{member_url}{permanent_member.id}",
        data=json.dumps({"wifiOnly": True}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204

    r2 = client_wifi_only.get(f"{member_url}{permanent_member.id}", headers=TEST_HEADERS)
    body = json.loads(r2.content.decode("utf-8"))
    assert body.get("wifiOnly") is True


# ── wifi_only subnet preservation / allocation tests ─────────────────────────


@pytest.fixture
def member_with_subnet(sample_room1):
    """Active member already holding a wireless subnet/IP, linked to a room."""
    yield Adherent(
        id=53,
        nom="SubnetHolder",
        prenom="Test",
        mail="subnetholder@test.net",
        login="subnet_holder",
        password="a",
        chambre_id=sample_room1.id,
        date_de_depart=tomorrow,
        mail_membership=1,
        ip="157.159.192.2",
        subnet="10.42.0.16/28",
    )


@pytest.fixture
def room_link_for_member_with_subnet(sample_room1, member_with_subnet):
    yield RoomMemberLink(room_id=sample_room1.id, member_id=member_with_subnet.id)


@pytest.fixture
async def client_wifi_subnet(
    _test_client,
    member_with_subnet,
    permanent_member,
    room_link_for_member_with_subnet,
    sample_room1,
    sample_vlan,
):
    from .conftest import add_test_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            sample_vlan,
            sample_room1,
            member_with_subnet,
            permanent_member,
            room_link_for_member_with_subnet,
        ]
    )

    yield _test_client

    await cleanup_test_data()


def test_set_wifi_only_preserves_existing_subnet(client_wifi_subnet, member_with_subnet: Adherent):
    """Enabling wifiOnly for a member who already has a subnet keeps subnet and IP intact."""
    r = client_wifi_subnet.patch(
        f"{member_url}{member_with_subnet.id}",
        data=json.dumps({"wifiOnly": True}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204

    r2 = client_wifi_subnet.get(f"{member_url}{member_with_subnet.id}", headers=TEST_HEADERS)
    body = json.loads(r2.content.decode("utf-8"))
    assert body.get("ip") is not None and body.get("ip") != ""
    assert body.get("subnet") is not None and body.get("subnet") != ""


def test_set_wifi_only_allocates_subnet_when_none(client_wifi_subnet, permanent_member: Adherent):
    """Enabling wifiOnly for an active member with no subnet allocates one for wifi access."""
    r = client_wifi_subnet.patch(
        f"{member_url}{permanent_member.id}",
        data=json.dumps({"wifiOnly": True}),
        headers={"Content-Type": "application/json", **TEST_HEADERS},
    )
    assert r.status_code == 204

    r2 = client_wifi_subnet.get(f"{member_url}{permanent_member.id}", headers=TEST_HEADERS)
    body = json.loads(r2.content.decode("utf-8"))
    assert body.get("ip") is not None and body.get("ip") != ""
    assert body.get("subnet") is not None and body.get("subnet") != ""
