from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from adh6.device.interfaces import DeviceRepository, NetboxRepository
from adh6.device.netbox_sync_manager import NetboxSyncManager
from adh6.entity import Device, Member
from adh6.member.interfaces import MemberRepository
from adh6.room.interfaces import RoomRepository
from adh6.subnet.vlan_manager import VlanManager


@pytest.fixture
def mock_netbox():
    return AsyncMock(spec=NetboxRepository)


@pytest.fixture
def mock_device_repo():
    return AsyncMock(spec=DeviceRepository)


@pytest.fixture
def mock_member_repo():
    return AsyncMock(spec=MemberRepository)


@pytest.fixture
def mock_room_repo():
    return AsyncMock(spec=RoomRepository)


@pytest.fixture
def mock_vlan_manager():
    return AsyncMock(spec=VlanManager)


@pytest.fixture
def sync_manager(mock_netbox, mock_device_repo, mock_member_repo, mock_room_repo, mock_vlan_manager):
    return NetboxSyncManager(
        netbox_repository=mock_netbox,
        device_repository=mock_device_repo,
        member_repository=mock_member_repo,
        room_repository=mock_room_repo,
        vlan_manager=mock_vlan_manager,
    )


@pytest.mark.asyncio
async def test_sync_skips_inactive_members(sync_manager, mock_netbox, mock_device_repo, mock_member_repo):
    # Setup: 1 active member, 1 inactive member
    active_member = Member(
        id=1,
        username="active",
        firstName="A",
        lastName="C",
        email="a@c.com",
        departureDate=datetime.now() + timedelta(days=30),
        subnet="10.42.0.0/28",
        ip="1.2.3.4",
    )
    inactive_member = Member(
        id=2,
        username="inactive",
        firstName="I",
        lastName="N",
        email="i@n.com",
        departureDate=datetime.now() - timedelta(days=1),
        subnet="10.42.0.16/28",
        ip="1.2.3.5",
    )

    mock_member_repo.search_by.return_value = ([active_member, inactive_member], 2)
    mock_member_repo.get_by_id.side_effect = lambda id: {1: active_member, 2: inactive_member}.get(id)

    # 1 device for each
    dev1 = Device(id=1, member=1, connectionType="wireless", mac="AA:BB:CC:DD:EE:01", ipv4Address="10.42.0.2")
    dev2 = Device(id=2, member=2, connectionType="wireless", mac="AA:BB:CC:DD:EE:02", ipv4Address="10.42.0.18")

    mock_device_repo.search_by.return_value = ([dev1, dev2], 2)

    mock_netbox.list_ips.return_value = []
    mock_netbox.list_prefixes.return_value = []

    await sync_manager.sync()

    # Verify ONLY active member IPs/prefixes were created
    # Prefix for member 1
    mock_netbox.create_wifi_prefix.assert_any_call("10.42.0.0/28", 1, nat_ip="1.2.3.4")
    # IP for dev 1
    mock_netbox.assign_ip.assert_any_call("10.42.0.2/28", "AA:BB:CC:DD:EE:01", 1, nat_ip="1.2.3.4")

    # Verify NO calls for inactive member
    with pytest.raises(AssertionError):
        mock_netbox.create_wifi_prefix.assert_any_call("10.42.0.16/28", 2, nat_ip="1.2.3.5")
    with pytest.raises(AssertionError):
        mock_netbox.assign_ip.assert_any_call("10.42.0.18/28", "AA:BB:CC:DD:EE:02", 2, nat_ip="1.2.3.5")


@pytest.mark.asyncio
async def test_sync_deletes_stale_entries(sync_manager, mock_netbox, mock_device_repo, mock_member_repo):
    # Setup: No members in DB, but entries in NetBox
    mock_member_repo.search_by.return_value = ([], 0)
    mock_device_repo.search_by.return_value = ([], 0)

    mock_netbox.list_ips.return_value = ["10.42.0.2"]
    mock_netbox.list_prefixes.return_value = ["10.42.0.0/28"]

    await sync_manager.sync()

    mock_netbox.unassign_ip.assert_called_once_with("10.42.0.2")
    mock_netbox.delete_wifi_prefix.assert_called_once_with("10.42.0.0/28")
