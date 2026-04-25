import pytest
from adh6.device.storage.device_repository import DeviceType
from adh6.device.storage.models import Device

from test.integration.resource import (
    TEST_HEADERS_API_KEY_ADMIN,
    TEST_HEADERS_API_KEY_NETWORK,
    base_url as host_url,
)

base_url = f"{host_url}"


@pytest.fixture
async def client(
    _test_client,
    sample_vlan,
    sample_vlan69,
    sample_room1,
    sample_room2,
    sample_member,
    wired_device,
    wireless_device,
):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            *api_key_fixtures(),
            sample_vlan,
            sample_vlan69,
            sample_room1,
            sample_room2,
            sample_member,
            wired_device,
            wireless_device,
        ]
    )

    yield _test_client

    await cleanup_test_data()


@pytest.fixture
async def client_with_over_limit(
    _test_client,
    sample_vlan,
    sample_room1,
    sample_member,
    device_no_ip,
):
    from .conftest import add_test_fixtures, api_key_fixtures, cleanup_test_data

    await add_test_fixtures(
        [
            *api_key_fixtures(),
            sample_vlan,
            sample_room1,
            sample_member,
            device_no_ip,
        ]
    )

    yield _test_client

    await cleanup_test_data()


@pytest.fixture
def device_no_ip(faker, sample_member):
    """A device with no IP assigned (over-limit candidate)."""
    yield Device(
        id=faker.random_digit_not_null() + 9000,
        mac=faker.mac_address(),
        adherent_id=sample_member.id,
        type=DeviceType.wired.value,
        ip=None,
    )


# ─── GET /vlans ──────────────────────────────────────────────────────────────


def test_vlans_get_returns_list(client):
    r = client.get(f"{base_url}/vlans", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 2
    numbers = [v["number"] for v in body]
    assert 42 in numbers
    assert 69 in numbers


def test_vlans_get_sorted_by_number(client):
    r = client.get(f"{base_url}/vlans", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    numbers = [v["number"] for v in r.json()]
    assert numbers == sorted(numbers)


def test_vlans_get_contains_network_fields(client, sample_vlan):
    r = client.get(f"{base_url}/vlans", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    vlan42 = next(v for v in r.json() if v["number"] == sample_vlan.numero)
    assert vlan42["ipv4Network"] == sample_vlan.adresses
    assert vlan42["ipv6Network"] == sample_vlan.adressesv6


def test_vlans_get_requires_admin(client):
    # API key with network scope but not admin scope → 401 (wrong scope)
    r = client.get(f"{base_url}/vlans", headers=TEST_HEADERS_API_KEY_NETWORK)
    assert r.status_code == 401


def test_vlans_get_unauthenticated(client):
    # No credentials → auth middleware returns 403
    r = client.get(f"{base_url}/vlans")
    assert r.status_code == 403


# ─── GET /vlans/stats ────────────────────────────────────────────────────────


def test_vlans_stats_get_returns_list(client):
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 2


def test_vlans_stats_sorted_by_number(client):
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    numbers = [v["number"] for v in r.json()]
    assert numbers == sorted(numbers)


def test_vlans_stats_device_count_counts_wired_with_ip(client, sample_vlan, wired_device):
    """Wired device with IP should be counted; wireless should not."""
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    vlan42 = next(v for v in r.json() if v["number"] == sample_vlan.numero)
    # wired_device has IP and is in sample_room1 (vlan 42)
    assert vlan42["deviceCount"] >= 1


def test_vlans_stats_wireless_device_not_counted(client, sample_vlan):
    """Wireless devices must not be counted as using VLAN IPs."""
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    vlan42 = next(v for v in r.json() if v["number"] == sample_vlan.numero)
    # Only wired_device counts; wireless_device must be excluded
    assert vlan42["deviceCount"] == 1


def test_vlans_stats_capacity_from_cidr(client, sample_vlan):
    """/24 subnet → 254 usable IPs."""
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    vlan42 = next(v for v in r.json() if v["number"] == sample_vlan.numero)
    assert vlan42["capacity"] == 254


def test_vlans_stats_no_over_limit_devices_when_under_capacity(client, sample_vlan):
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    vlan42 = next(v for v in r.json() if v["number"] == sample_vlan.numero)
    assert vlan42["overLimitDevices"] == []


def test_vlans_stats_over_limit_device_appears(client_with_over_limit, sample_vlan, device_no_ip):
    """Device with no IP should appear in overLimitDevices."""
    r = client_with_over_limit.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_ADMIN)
    assert r.status_code == 200
    vlan42 = next(v for v in r.json() if v["number"] == sample_vlan.numero)
    assert len(vlan42["overLimitDevices"]) == 1
    assert vlan42["overLimitDevices"][0]["mac"] == device_no_ip.mac


def test_vlans_stats_requires_admin(client):
    # API key with network scope but not admin scope → 401 (wrong scope)
    r = client.get(f"{base_url}/vlans/stats", headers=TEST_HEADERS_API_KEY_NETWORK)
    assert r.status_code == 401


def test_vlans_stats_unauthenticated(client):
    # No credentials → auth middleware returns 403
    r = client.get(f"{base_url}/vlans/stats")
    assert r.status_code == 403
