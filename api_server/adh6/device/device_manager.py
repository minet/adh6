# coding=utf-8
from typing import List, Literal, Tuple, Union
from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractDevice, DeviceFilter, Device, DeviceBody
from adh6.exceptions import DeviceNotFoundError, InvalidMACAddress, DeviceAlreadyExists, DevicesLimitReached, MemberNotFoundError, RoomNotFoundError, VLANNotFoundError
from adh6.decorator import log_call
from adh6.default import CRUDManager
from adh6.room.interfaces import RoomRepository
from adh6.subnet.interfaces import VlanRepository
from adh6.misc import is_mac_address
from adh6.member.interfaces import MemberRepository

from .interfaces import DeviceRepository, IpAllocator
from .device_ip_manager import DeviceIpManager
from .storage.device_repository import DeviceType


class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(self,
                 device_repository: DeviceRepository,
                 device_ip_manager: DeviceIpManager,
                 member_repository: MemberRepository,
                 room_repository: RoomRepository):
        super().__init__(device_repository, DeviceNotFoundError)
        self.device_repository = device_repository
        self.device_ip_manager = device_ip_manager
        self.member_repository = member_repository
        self.room_repository = room_repository
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
    def search(self, limit: int, offset: int, device_filter: DeviceFilter) -> Tuple[List[int], int]:
        result, count = self.device_repository.search_by(
            limit=limit,
            offset=offset,
            device_filter=device_filter
        )
        return [r.id for r in result], count

    @log_call
    def put_mab(self, id: int) -> bool:
        device = self.device_repository.get_by_id(id)
        if not device:
            raise DeviceNotFoundError(id)
        mab = self.device_repository.get_mab(id)
        return self.device_repository.put_mab(id, not mab)

    @log_call
    def get_mab(self, id: int) -> bool:
        device = self.device_repository.get_by_id(id)
        if not device:
            raise DeviceNotFoundError(id)
        return self.device_repository.get_mab(id)

    @log_call
    def get_mac_vendor(self, id: int) -> str:
        device = self.device_repository.get_by_id(id)
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
    def create(self, body: DeviceBody) -> Device:
        if body.mac is None or not is_mac_address(body.mac):
            raise InvalidMACAddress(body.mac)

        if body.member is None:
            raise MemberNotFoundError(None)
        member = self.member_repository.get_by_id(body.member)
        if not member:
            raise MemberNotFoundError(body.member)
        room = self.room_repository.get_from_member(body.member)
        if not room:
            raise RoomNotFoundError(f"for member {member.username}")

        if not body.connection_type:
            raise ValueError()
        body.mac = str(body.mac).upper().replace(':', '-')

        d = self.device_repository.get_by_mac(body.mac)
        _, count = self.device_repository.search_by(limit=DEFAULT_LIMIT, offset=0, device_filter=DeviceFilter(member=body.member))
        if d:
            raise DeviceAlreadyExists()
        elif count >= 20:
            raise DevicesLimitReached()

        device = self.device_repository.create(body)

        self.device_ip_manager.allocate_ip_with_vlan_number(
            device=device,
            member=member,
            vlan_number=room.vlan
        )

        return device

    @log_call
    def get_owner(self, device_id: int) -> Union[int, None]:
        d = self.device_repository.get_by_id(object_id=device_id)
        if not d:
            raise DeviceNotFoundError(device_id)
        return self.device_repository.owner(id=device_id)

