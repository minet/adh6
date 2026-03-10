import secrets
from pathlib import Path

from adh6.constants import DEFAULT_LIMIT
from adh6.decorator import log_call
from adh6.default import CRUDManager
from adh6.entity import Device, DeviceBody, DeviceFilter
from adh6.exceptions import (
    DeviceAlreadyExists,
    DeviceNotFoundError,
    DevicesLimitReached,
    InvalidMACAddress,
    MemberNotFoundError,
    RoomNotFoundError,
)
from adh6.member.interfaces import MemberRepository
from adh6.misc import is_mac_address
from adh6.room.interfaces import RoomRepository

from .device_ip_manager import DeviceIpManager
from .interfaces import DeviceRepository


class DeviceManager(CRUDManager):
    """
    Implements all the use cases related to device management.
    """

    def __init__(
        self,
        device_repository: DeviceRepository,
        device_ip_manager: DeviceIpManager,
        member_repository: MemberRepository,
        room_repository: RoomRepository,
    ):
        super().__init__(device_repository, DeviceNotFoundError)
        self.device_repository = device_repository
        self.device_ip_manager = device_ip_manager
        self.member_repository = member_repository
        self.room_repository = room_repository
        self.oui_repository = {}
        self.load_mac_oui_dict()

    def load_mac_oui_dict(self):
        file = Path("OUIs.txt")
        if not file.exists():
            print("OUIs.txt not found, skipping loading MAC OUI dictionary.")
            return
        with open(file, encoding="utf-8") as f:
            line = f.readline()
            while line != "":
                oui, company = line.split("\t")
                self.oui_repository[oui] = company
                line = f.readline()

    @log_call
    async def search(self, limit: int, offset: int, device_filter: DeviceFilter) -> tuple[list[Device], int]:
        result, count = await self.device_repository.search_by(limit=limit, offset=offset, device_filter=device_filter)
        return result, count

    @log_call
    async def put_mab(self, id: int) -> bool:
        device = await self.device_repository.get_by_id(id)
        if not device:
            raise DeviceNotFoundError(id)
        mab = await self.device_repository.get_mab(id)
        return await self.device_repository.put_mab(id, not mab)

    @log_call
    async def get_mab(self, id: int) -> bool:
        device = await self.device_repository.get_by_id(id)
        if not device:
            raise DeviceNotFoundError(id)
        return await self.device_repository.get_mab(id)

    @log_call
    async def get_mac_vendor(self, id: int) -> str:
        device = await self.device_repository.get_by_id(id)
        if not device:
            raise DeviceNotFoundError(id)

        if not device.mac:
            return "-"

        mac_address = device.mac[:8].replace(":", "-")
        vendor = self.oui_repository.get(mac_address, "-")

        return vendor

    @log_call
    async def create(self, body: DeviceBody) -> Device:
        if body.mac is None or not is_mac_address(body.mac):
            raise InvalidMACAddress(body.mac)

        if body.member is None:
            raise MemberNotFoundError(None)
        member = await self.member_repository.get_by_id(body.member)
        if not member:
            raise MemberNotFoundError(body.member)
        room = await self.room_repository.get_from_member(body.member)
        if not room:
            raise RoomNotFoundError(f"for member {member.username}")

        if not body.connection_type:
            raise ValueError
        body.mac = str(body.mac).upper().replace(":", "-")

        d = await self.device_repository.get_by_mac(body.mac)
        _, count = await self.device_repository.search_by(
            limit=DEFAULT_LIMIT,
            offset=0,
            device_filter=DeviceFilter(member=body.member),
        )
        if d:
            raise DeviceAlreadyExists
        elif count >= 20:
            raise DevicesLimitReached

        device = await self.device_repository.create(body)

        await self.device_ip_manager.allocate_ip_with_vlan_number(device=device, member=member, vlan_number=room.vlan)

        return device

    @log_call
    async def get_owner(self, device_id: int) -> int | None:
        d = await self.device_repository.get_by_id(object_id=device_id)
        if not d:
            raise DeviceNotFoundError(device_id)
        return await self.device_repository.owner(id=device_id)

    @log_call
    async def rename(self, device_id: int, name: str) -> None:
        d = await self.device_repository.get_by_id(object_id=device_id)
        if not d:
            raise DeviceNotFoundError(device_id)
        await self.device_repository.set_name(device_id, name)

    @log_call
    async def generate_wifi_password(self, device_id: int) -> str:
        easy_chars = "BCDEFHKLMNPQRSTUVWXYZabcdefhikmnopqrstuvwxyz2356789"
        d = await self.device_repository.get_by_id(object_id=device_id)
        if not d:
            raise DeviceNotFoundError(device_id)
        # Generate a random WPA2-compatible password (printable ASCII, max 63 chars)
        password = "".join(secrets.choice(easy_chars) for _ in range(12))
        await self.device_repository.set_wifi_password(device_id, password)
        return password

    @log_call
    async def clear_wifi_password(self, device_id: int) -> None:
        d = await self.device_repository.get_by_id(object_id=device_id)
        if not d:
            raise DeviceNotFoundError(device_id)
        await self.device_repository.set_wifi_password(device_id, None)
