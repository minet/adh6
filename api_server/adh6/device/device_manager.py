# coding=utf-8
import typing as t
from adh6.constants import DEFAULT_LIMIT
from adh6.entity import DeviceFilter, Device, DeviceBody
from adh6.exceptions import DeviceNotFoundError, InvalidMACAddress, DeviceAlreadyExists, DevicesLimitReached
from adh6.decorator import log_call
from adh6.default import CRUDManager

if t.TYPE_CHECKING:
    from adh6.member import MemberManager
    from adh6.room import RoomManager

from .interfaces import DeviceRepository
from .utils import is_mac_address
from . import DeviceIpManager


class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(self,
                 device_repository: DeviceRepository,
                 device_ip_manager: DeviceIpManager,
                 member_manager: 'MemberManager',
                 room_manager: 'RoomManager'):
        super().__init__(device_repository, DeviceNotFoundError)
        self.device_repository = device_repository
        self.device_ip_manager = device_ip_manager
        self.member_manager = member_manager
        self.room_manager = room_manager
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
    def search(self, limit: int, offset: int, device_filter: DeviceFilter) -> t.Tuple[t.List[int], int]:
        result, count = self.device_repository.search_by(
            limit=limit,
            offset=offset,
            device_filter=device_filter
        )
        return [r.id for r in result], count

    @log_call
    def get_by_user_login(self, login: str, device_type: str) -> t.List[int]:
        member = self.member_manager.get_by_login(login=login)
        result, _ = self.device_repository.search_by(
            limit=25,
            offset=0,
            device_filter=DeviceFilter(member=member.id, connection_type=device_type)
        )
        return [r.id for r in result]

    @log_call
    def put_mab(self, id: int) -> bool:
        _ = self.get_by_id(id)
        mab = self.device_repository.get_mab(id)
        return self.device_repository.put_mab(id, not mab)

    @log_call
    def get_mab(self, id: int) -> bool:
        _ = self.get_by_id(id)
        return self.device_repository.get_mab(id)

    @log_call
    def get_mac_vendor(self, id: int) -> str:
        device = self.get_by_id(id)
        if not device.mac:
            return "-"
        mac_address = device.mac[:8].replace(":", "-")
        return "-" if mac_address not in self.oui_repository else self.oui_repository[mac_address]


    @log_call
    def create(self, body: DeviceBody) -> Device:
        if body.mac is None or not is_mac_address(body.mac):
            raise InvalidMACAddress(body.mac)

        member = self.member_manager.get_by_id(body.member)
        room = self.room_manager.room_from_member(body.member)

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
