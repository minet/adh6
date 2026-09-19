import typing as t

from adh6.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    WIFI_IPV6_NETWORK,
    WIFI_IPV6_RESERVED_HOSTS,
)
from adh6.decorator import log_call
from adh6.entity import AbstractVlan, Device, DeviceFilter, Member
from adh6.exceptions import IPAlreadyAssignedError, NoNetworkToAllocateFromError
from adh6.subnet.vlan_manager import VlanManager

from .interfaces import DeviceRepository, IpAllocator
from .storage.device_repository import DeviceType

MAX_ALLOCATION_ATTEMPTS = 5


class DeviceIpManager:
    def __init__(
        self,
        ip_allocator: IpAllocator,
        device_repository: DeviceRepository,
        vlan_manager: VlanManager,
    ) -> None:
        self.ip_allocator = ip_allocator
        self.device_repository = device_repository

        self.vlan_manager = vlan_manager

    @log_call
    async def allocate_ips(
        self,
        member: Member,
        device_type: t.Literal["wired", "wireless"] | None = None,
        vlan_number: int | None = None,
    ) -> None:
        if not vlan_number and device_type == DeviceType.wired.name:
            raise ValueError("Cannot have both parameters: device_type to wired and vlan_number to None")

        vlan = await self.vlan_manager.get_from_number(vlan_number=vlan_number) if vlan_number else None
        devices, _ = await self.device_repository.search_by(
            limit=DEFAULT_LIMIT,
            offset=DEFAULT_OFFSET,
            device_filter=DeviceFilter(member=member.id, connectionType=device_type or None),
        )
        for d in devices:
            await self.allocate_ip_with_vlan(device=d, member=member, vlan=vlan)

    @log_call
    async def unallocate_ips(self, member: Member) -> None:
        devices, _ = await self.device_repository.search_by(
            limit=DEFAULT_LIMIT,
            offset=DEFAULT_OFFSET,
            device_filter=DeviceFilter(member=member.id),
        )
        for d in devices:
            await self.unallocate_ip(device=d)

    @log_call
    async def allocate_ip_with_vlan_number(self, device: Device, member: Member, vlan_number: int) -> None:
        vlan = await self.vlan_manager.get_from_number(vlan_number=vlan_number)
        await self.allocate_ip_with_vlan(device=device, member=member, vlan=vlan)

    @log_call
    async def allocate_ip_with_vlan(self, device: Device, member: Member, vlan: AbstractVlan | None) -> None:
        ipv4_network = ""
        if device.connection_type == DeviceType.wired.name and vlan:
            ipv4_network = vlan.ipv4_network
        elif device.connection_type == DeviceType.wireless.name:
            ipv4_network = member.subnet

        ipv6_network = ""
        ipv6_reserved_hosts = 1
        if device.connection_type == DeviceType.wireless.name:
            ipv6_network = WIFI_IPV6_NETWORK
            ipv6_reserved_hosts = WIFI_IPV6_RESERVED_HOSTS
        elif vlan:
            ipv6_network = vlan.ipv6_network or ""

        if not ipv4_network:
            missing = (
                "a VLAN (is the member's room assigned one?)"
                if device.connection_type == DeviceType.wired.name
                else "a subnet"
            )
            raise NoNetworkToAllocateFromError(
                f"Cannot allocate an IP address: a {device.connection_type} device needs {missing}"
            )

        await self._allocate_ip(
            device=device,
            ipv4_network=ipv4_network,
            ipv6_network=ipv6_network,
            ipv6_reserved_hosts=ipv6_reserved_hosts,
        )

    @log_call
    async def _allocate_ip(
        self,
        device: Device,
        ipv4_network: str = "",
        ipv6_network: str = "",
        ipv6_reserved_hosts: int = 1,
    ) -> None:
        if device.id is None:
            raise ValueError("Cannot allocate IPs to a device without an id")

        taken: set[str] = set()
        for attempt in range(1, MAX_ALLOCATION_ATTEMPTS + 1):
            ipv4 = await self.ip_allocator.available_ip(ipv4_network, excluded=taken)
            ipv6 = (
                await self.ip_allocator.available_ip(ipv6_network, reserved_hosts=ipv6_reserved_hosts, excluded=taken)
                if ipv6_network
                else None
            )
            try:
                await self.device_repository.set_ip_addresses(device.id, ipv4, ipv6)
            except IPAlreadyAssignedError:
                if attempt == MAX_ALLOCATION_ATTEMPTS:
                    raise
                taken.update(ip for ip in (ipv4, ipv6) if ip)
            else:
                return

    @log_call
    async def unallocate_ip(self, device: Device) -> None:
        if device.id is None:
            raise ValueError("Cannot unallocate IPs from a device without an id")
        await self.device_repository.set_ip_addresses(device.id, None, None)
