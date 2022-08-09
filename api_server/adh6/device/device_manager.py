# coding=utf-8
from typing import List, Literal, Tuple, Union
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.device.storage.device_repository import DeviceType
from adh6.entity import AbstractDevice, DeviceFilter, Device, DeviceBody
from adh6.exceptions import DeviceNotFoundError, InvalidMACAddress, InvalidIPv6, InvalidIPv4, DeviceAlreadyExists, DevicesLimitReached, MemberNotFoundError, VLANNotFoundError
from adh6.default.decorator.log_call import log_call
from adh6.default.crud_manager import CRUDManager
from adh6.default.decorator.auto_raise import auto_raise
from adh6.device.interfaces.device_repository import DeviceRepository
from adh6.device.interfaces.ip_allocator import IpAllocator
from adh6.subnet.interfaces.vlan_repository import VlanRepository
from adh6.misc.validator import is_mac_address
from adh6.member.interfaces.member_repository import MemberRepository


class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(self,
                 device_repository: DeviceRepository,
                 ip_allocator: IpAllocator,
                 vlan_repository: VlanRepository,
                 member_repository: MemberRepository
                 ):
        super().__init__(device_repository, DeviceNotFoundError)
        self.device_repository = device_repository
        self.ip_allocator = ip_allocator
        self.vlan_repository = vlan_repository
        self.member_repository = member_repository
        self.oui_repository = {}
        self.load_mac_oui_dict()

    def load_mac_oui_dict(self):
        with open('OUIs.txt', 'r', encoding='utf-8') as f:
            line = f.readline()
            while line != "":
                oui, company = line.split('\t')
                self.oui_repository[oui] = company
                line = f.readline()

    @log_call
    @auto_raise
    def search(self, ctx, limit: int, offset: int, device_filter: DeviceFilter) -> Tuple[List[int], int]:
        result, count = self.device_repository.search_by(
            ctx, 
            limit=limit,
            offset=offset,
            device_filter=device_filter
        )
        return [r.id for r in result], count

    @log_call
    @auto_raise
    def put_mab(self, ctx, id: int) -> bool:
        device = self.device_repository.get_by_id(ctx, id)
        if not device:
            raise DeviceNotFoundError(id)
        mab = self.device_repository.get_mab(ctx, id)
        return self.device_repository.put_mab(ctx, id, not mab)

    @log_call
    @auto_raise
    def get_mab(self, ctx, id: int) -> bool:
        device = self.device_repository.get_by_id(ctx, id)
        if not device:
            raise DeviceNotFoundError(id)
        return self.device_repository.get_mab(ctx, id)


    @log_call
    @auto_raise
    def get_mac_vendor(self, ctx, id: int) -> str:
        device = self.device_repository.get_by_id(ctx, id)
        if not device:
            raise DeviceNotFoundError(id)

        if not device.mac:
            return "-"

        mac_address = device.mac[:8].replace(":", "-")
        if mac_address not in self.oui_repository:
            vendor = "-"
        else:
            vendor = self.oui_repository[mac_address]

        return vendor


    @log_call
    @auto_raise
    def create(self, ctx, body: DeviceBody) -> Device:
        if body.mac is None or not is_mac_address(body.mac):
            raise InvalidMACAddress(body.mac)

        if body.member is None:
            raise MemberNotFoundError(None)
        member = self.member_repository.get_by_id(ctx, body.member)
        if not member:
            raise MemberNotFoundError(body.member)

        if not body.connection_type:
            raise ValueError()
        body.mac = str(body.mac).upper().replace(':', '-')

        d = self.device_repository.get_by_mac(ctx, body.mac)
        _, count = self.device_repository.search_by(ctx, limit=DEFAULT_LIMIT, offset=0, device_filter=DeviceFilter(member=body.member))
        if d:
            raise DeviceAlreadyExists()
        elif count >= 20:
            raise DevicesLimitReached()

        device = self.device_repository.create(ctx, body)
        self._allocate_or_unallocate_ip(ctx, device, member.subnet if member.subnet else "")
        return device

    @log_call
    @auto_raise
    def allocate_wired_ips(self, ctx, member_id: int, vlan_number: int) -> None:
        vlan = self.vlan_repository.get_vlan(ctx, vlan_number=vlan_number)
        if vlan is None:
            raise VLANNotFoundError(vlan_number)
        self._allocate_or_unallocate_ips(ctx=ctx, member_id=member_id, device_type=DeviceType.wired.name, subnet_v4=vlan.ipv4_network if vlan.ipv4_network else "", subnet_v6=vlan.ipv6_network if vlan.ipv6_network else "")

    @log_call
    @auto_raise
    def allocate_wireless_ips(self, ctx, member_id: int, subnet: str) -> None:
        self._allocate_or_unallocate_ips(ctx=ctx, member_id=member_id, device_type=DeviceType.wireless.name, subnet_v4=subnet)

    @log_call
    @auto_raise
    def _allocate_or_unallocate_ips(self, ctx, member_id: int, device_type: Union[Literal["wired", "wireless"], None] = None, subnet_v4: str = "", subnet_v6: str = "") -> None:
        devices, _ = self.device_repository.search_by(ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, device_filter=DeviceFilter(member=member_id, connection_type=device_type))
        for d in devices:
            self._allocate_or_unallocate_ip(
                ctx=ctx,
                device=d,
                subnet_v4=subnet_v4,
                subnet_v6=subnet_v6
            )

    @log_call
    @auto_raise
    def _allocate_or_unallocate_ip(self, ctx, device: Device, subnet_v4: str = "", subnet_v6: str = "") -> None:
        self.partially_update(
            ctx, 
            AbstractDevice(
                ipv4_address=self.ip_allocator.available_ip(ctx, subnet_v4),
                ipv6_address=self.ip_allocator.available_ip(ctx, subnet_v6)
            ), 
            device.id
        )

    @log_call
    @auto_raise
    def unallocate_ip_addresses(self, ctx, member_id: int):
        self._allocate_or_unallocate_ips(ctx, member_id)

    @log_call
    def get_owner(self, ctx, device_id: int) -> Union[int, None]:
        d = self.device_repository.get_by_id(ctx, object_id=device_id)
        if not d:
            raise DeviceNotFoundError(device_id)
        return self.device_repository.owner(ctx, id=device_id)

