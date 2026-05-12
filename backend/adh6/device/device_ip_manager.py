import typing as t
from ipaddress import ip_network

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.entity import AbstractDevice, AbstractVlan, Device, DeviceFilter, Member
from adh6.subnet.vlan_manager import VlanManager

from .interfaces import DeviceRepository, IpAllocator, NetboxRepository
from .storage.device_repository import DeviceType


class DeviceIpManager:
    def __init__(
        self,
        ip_allocator: IpAllocator,
        device_repository: DeviceRepository,
        vlan_manager: VlanManager,
        netbox_repository: NetboxRepository | None = None,
    ) -> None:
        self.ip_allocator = ip_allocator
        self.device_repository = device_repository
        self.vlan_manager = vlan_manager
        self.netbox_repository = netbox_repository

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
            device_filter=DeviceFilter(member=member.id, connectionType=device_type if device_type else None),
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
        if vlan:
            ipv6_network = vlan.ipv6_network or ""

        if not ipv4_network:
            raise ValueError("Cannot allocate IP without network")

        await self._allocate_ip(
            device=device,
            ipv4_network=ipv4_network,
            ipv6_network=ipv6_network,
            member=member,
        )

    @log_call
    async def _allocate_ip(
        self, device: Device, ipv4_network: str = "", ipv6_network: str = "", member: Member | None = None
    ) -> None:
        ipv4 = await self.ip_allocator.available_ip(ipv4_network)
        ipv6 = await self.ip_allocator.available_ip(ipv6_network) if ipv6_network else None

        await self.device_repository.update(  # type: ignore  # TODO: typing is baaaaad
            abstract_device=AbstractDevice(  # type: ignore  # TODO: typing is baaaaad
                id=device.id, ipv4Address=ipv4, ipv6Address=ipv6
            ),
        )

        if self.netbox_repository and device.mac and device.member:
            # Remove old IPs before assigning new ones (e.g. VLAN change)
            if device.ipv4_address and device.ipv4_address != "En attente":
                await self.netbox_repository.unassign_ip(device.ipv4_address)
            if device.ipv6_address and device.ipv6_address != "En attente":
                await self.netbox_repository.unassign_ip(device.ipv6_address)

            nat_ip = member.ip if member and device.connection_type == DeviceType.wireless.name else None

            if ipv4 and ipv4 != "En attente" and ipv4_network:
                prefixlen = ip_network(ipv4_network, strict=False).prefixlen
                await self.netbox_repository.assign_ip(f"{ipv4}/{prefixlen}", device.mac, device.member, nat_ip=nat_ip)
            if ipv6 and ipv6 != "En attente" and ipv6_network:
                prefixlen6 = ip_network(ipv6_network, strict=False).prefixlen
                await self.netbox_repository.assign_ip(f"{ipv6}/{prefixlen6}", device.mac, device.member)

    @log_call
    async def unallocate_ip(self, device: Device) -> None:
        if self.netbox_repository:
            if device.ipv4_address and device.ipv4_address != "En attente":
                await self.netbox_repository.unassign_ip(device.ipv4_address)
            if device.ipv6_address and device.ipv6_address != "En attente":
                await self.netbox_repository.unassign_ip(device.ipv6_address)

        await self.device_repository.update(
            abstract_device=AbstractDevice(  # type: ignore  # TODO: typing is baaaaad
                id=device.id, ipv4Address="En attente", ipv6Address="En attente"
            ),
            override=False,
        )
