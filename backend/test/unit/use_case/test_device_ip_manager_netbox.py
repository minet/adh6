from unittest.mock import AsyncMock, MagicMock

from adh6.device.device_ip_manager import DeviceIpManager
from adh6.device.interfaces import DeviceRepository, IpAllocator, NetboxRepository
from adh6.entity import Device
from adh6.subnet.vlan_manager import VlanManager
from pytest import fixture


@fixture
def mock_ip_allocator():
    m = MagicMock(spec=IpAllocator)
    m.available_ip = AsyncMock(return_value="10.0.0.5")
    return m


@fixture
def mock_device_repository():
    m = MagicMock(spec=DeviceRepository)
    m.update = AsyncMock(return_value=None)
    return m


@fixture
def mock_vlan_manager():
    return MagicMock(spec=VlanManager)


@fixture
def mock_netbox():
    m = AsyncMock(spec=NetboxRepository)
    return m


@fixture
def sample_device(faker):
    return Device(
        id=faker.random_digit_not_null(),
        mac="AA-BB-CC-DD-EE-FF",
        member=42,
        connectionType="wired",
        ipv4Address="10.0.0.5",
        ipv6Address=None,
    )


@fixture
def sample_device_en_attente(faker):
    return Device(
        id=faker.random_digit_not_null(),
        mac="AA-BB-CC-DD-EE-FF",
        member=42,
        connectionType="wired",
        ipv4Address="En attente",
        ipv6Address="En attente",
    )


@fixture
def ip_manager_with_netbox(mock_ip_allocator, mock_device_repository, mock_vlan_manager, mock_netbox):
    return DeviceIpManager(
        ip_allocator=mock_ip_allocator,
        device_repository=mock_device_repository,
        vlan_manager=mock_vlan_manager,
        netbox_repository=mock_netbox,
    )


@fixture
def ip_manager_no_netbox(mock_ip_allocator, mock_device_repository, mock_vlan_manager):
    return DeviceIpManager(
        ip_allocator=mock_ip_allocator,
        device_repository=mock_device_repository,
        vlan_manager=mock_vlan_manager,
        netbox_repository=None,
    )


class TestAllocateIpNetbox:
    async def test_assign_ip_calls_netbox_with_ipv4(
        self,
        ip_manager_with_netbox: DeviceIpManager,
        mock_netbox: AsyncMock,
        sample_device: Device,
    ):
        mock_netbox.assign_ip = AsyncMock()
        await ip_manager_with_netbox._allocate_ip(sample_device, ipv4_network="10.0.0.0/24")

        mock_netbox.assign_ip.assert_called_once_with("10.0.0.5/24", "AA-BB-CC-DD-EE-FF", 42, nat_ip=None)

    async def test_assign_ip_calls_netbox_with_ipv4_and_ipv6(
        self,
        mock_ip_allocator: MagicMock,
        ip_manager_with_netbox: DeviceIpManager,
        mock_netbox: AsyncMock,
        sample_device: Device,
    ):
        mock_ip_allocator.available_ip = AsyncMock(side_effect=["10.0.0.5", "fe80::5"])
        mock_netbox.assign_ip = AsyncMock()

        await ip_manager_with_netbox._allocate_ip(sample_device, ipv4_network="10.0.0.0/24", ipv6_network="fe80::/64")

        assert mock_netbox.assign_ip.call_count == 2
        calls = [c.kwargs for c in mock_netbox.assign_ip.call_args_list]
        args = [c.args for c in mock_netbox.assign_ip.call_args_list]
        assert ("10.0.0.5/24", "AA-BB-CC-DD-EE-FF", 42) in args
        assert ("fe80::5/64", "AA-BB-CC-DD-EE-FF", 42) in args
        assert all(c.get("nat_ip") is None for c in calls if c)

    async def test_assign_ip_skips_netbox_when_none(
        self,
        ip_manager_no_netbox: DeviceIpManager,
        sample_device: Device,
    ):
        # Should not raise
        await ip_manager_no_netbox._allocate_ip(sample_device, ipv4_network="10.0.0.0/24")

    async def test_assign_ip_skips_netbox_when_en_attente(
        self,
        mock_ip_allocator: MagicMock,
        ip_manager_with_netbox: DeviceIpManager,
        mock_netbox: AsyncMock,
        sample_device: Device,
    ):
        mock_ip_allocator.available_ip = AsyncMock(return_value="En attente")
        mock_netbox.assign_ip = AsyncMock()

        await ip_manager_with_netbox._allocate_ip(sample_device, ipv4_network="10.0.0.0/24")

        mock_netbox.assign_ip.assert_not_called()

    async def test_reallocate_unassigns_old_ip_before_assigning_new(
        self,
        mock_ip_allocator: MagicMock,
        ip_manager_with_netbox: DeviceIpManager,
        mock_netbox: AsyncMock,
        faker,
    ):
        """VLAN change: device already has an IP — old must be removed before new is created."""
        device_with_ip = Device(
            id=faker.random_digit_not_null(),
            mac="AA-BB-CC-DD-EE-FF",
            member=42,
            connectionType="wired",
            ipv4Address="10.0.0.5",
            ipv6Address=None,
        )
        mock_ip_allocator.available_ip = AsyncMock(return_value="10.1.0.5")
        mock_netbox.unassign_ip = AsyncMock()
        mock_netbox.assign_ip = AsyncMock()

        await ip_manager_with_netbox._allocate_ip(device_with_ip, ipv4_network="10.1.0.0/24")


class TestUnallocateIpNetbox:
    async def test_unallocate_calls_netbox_unassign(
        self,
        ip_manager_with_netbox: DeviceIpManager,
        mock_netbox: AsyncMock,
        sample_device: Device,
    ):
        mock_netbox.unassign_ip = AsyncMock()
        await ip_manager_with_netbox.unallocate_ip(sample_device)

        mock_netbox.unassign_ip.assert_called_once_with("10.0.0.5")

    async def test_unallocate_skips_en_attente(
        self,
        ip_manager_with_netbox: DeviceIpManager,
        mock_netbox: AsyncMock,
        sample_device_en_attente: Device,
    ):
        mock_netbox.unassign_ip = AsyncMock()
        await ip_manager_with_netbox.unallocate_ip(sample_device_en_attente)

        mock_netbox.unassign_ip.assert_not_called()

    async def test_unallocate_skips_netbox_when_none(
        self,
        ip_manager_no_netbox: DeviceIpManager,
        sample_device: Device,
    ):
        # Should not raise
        await ip_manager_no_netbox.unallocate_ip(sample_device)
