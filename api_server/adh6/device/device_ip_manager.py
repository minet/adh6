import typing as t

from adh6.entity import AbstractDevice, Device, DeviceFilter, Member, Vlan
from adh6.decorator import log_call
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

from adh6.subnet.vlan_manager import VlanManager

from .interfaces import IpAllocator, DeviceRepository
from .enums import DeviceType

class DeviceIpManager:
    def __init__(self, ip_allocator: IpAllocator, device_repository: DeviceRepository, vlan_manager: VlanManager) -> None:
        self.ip_allocator = ip_allocator
        self.device_repository = device_repository
        
        self.vlan_manager = vlan_manager

    @log_call
    def allocate_ips(self, member: Member, device_type: t.Union[t.Literal["wired", "wireless"], None] = None, vlan_number: t.Union[int, None] = None) -> None:
        if not vlan_number and device_type == DeviceType.wired.name:
            raise ValueError("Cannot have both parameters: device_type to wired and vlan_number to None")

        vlan = self.vlan_manager.get_from_number(vlan_number=vlan_number) if vlan_number else None
        devices, _ = self.device_repository.search_by(limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, device_filter=DeviceFilter(member=member.id, connection_type=device_type if device_type else None))
        for d in devices:
            self.allocate_ip_with_vlan(
                device=d,
                member=member,
                vlan=vlan
            )

    @log_call
    def unallocate_ips(self, member: Member) -> None:
        devices, _ = self.device_repository.search_by(limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, device_filter=DeviceFilter(member=member.id))
        for d in devices:
            self.unallocate_ip(device=d)

    @log_call
    def allocate_ip_with_vlan_number(self, device: Device, member: Member, vlan_number: int) -> None:
        vlan = self.vlan_manager.get_from_number(vlan_number=vlan_number)
        self.allocate_ip_with_vlan(
            device=device,
            member=member,
            vlan=vlan
        )

    @log_call
    def allocate_ip_with_vlan(self, device: Device, member: Member, vlan: Vlan) -> None:
        ipv4_network = ""
        if device.connection_type == DeviceType.wired.name and vlan:
            ipv4_network = vlan.ipv4_network
        elif device.connection_type == DeviceType.wireless.name:
            ipv4_network = member.subnet

        ipv6_network = ""
        if vlan:
            ipv6_network = vlan.ipv6_network

        self._allocate_ip(
            device=device, 
            ipv4_network=ipv4_network, 
            ipv6_network=ipv6_network
        )

    @log_call
    def _allocate_ip(self, device: Device, ipv4_network: str = "", ipv6_network: str = "") -> None:
        self.device_repository.update(
            abstract_device=AbstractDevice(
                id=device.id,
                ipv4_address=self.ip_allocator.available_ip(ipv4_network),
                ipv6_address=self.ip_allocator.available_ip(ipv6_network)
            )
        )

    @log_call
    def unallocate_ip(self, device: Device) -> None:
        self.device_repository.update(abstract_device=AbstractDevice(
            id=device.id,
            ipv4_address='En attente',
            ipv6_address='En attente'
        ), override=True)