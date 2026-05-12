import logging
from dataclasses import dataclass, field
from ipaddress import ip_network

from adh6.constants import DEFAULT_OFFSET
from adh6.decorator import log_call
from adh6.entity import DeviceFilter, MemberFilter
from adh6.member.interfaces import MemberRepository
from adh6.room.interfaces import RoomRepository
from adh6.subnet.vlan_manager import VlanManager
from adh6.utils.validators.member_validators import is_member_active

from .interfaces import DeviceRepository, NetboxRepository
from .storage.device_repository import DeviceType

logger = logging.getLogger(__name__)

_BATCH = 1000


@dataclass
class NetboxSyncResult:
    ips_created: int = 0
    ips_deleted: int = 0
    prefixes_created: int = 0
    prefixes_deleted: int = 0
    errors: list[str] = field(default_factory=list)


class NetboxSyncManager:
    def __init__(
        self,
        netbox_repository: NetboxRepository,
        device_repository: DeviceRepository,
        member_repository: MemberRepository,
        room_repository: RoomRepository,
        vlan_manager: VlanManager,
    ) -> None:
        self.netbox = netbox_repository
        self.device_repository = device_repository
        self.member_repository = member_repository
        self.room_repository = room_repository
        self.vlan_manager = vlan_manager

    @log_call
    async def sync(self) -> NetboxSyncResult:
        result = NetboxSyncResult()

        # Build expected state from DB
        # expected_ips: bare_ip -> (ip_with_prefix, mac, member_id, nat_ip)
        expected_ips: dict[str, tuple[str, str, int, str | None]] = {}
        # expected_prefixes: prefix_str -> (member_id, nat_ip)
        expected_prefixes: dict[str, tuple[int, str | None]] = {}

        await self._collect_device_ips(expected_ips, result)
        await self._collect_wifi_prefixes(expected_prefixes)

        # Fetch current Netbox state
        current_ips = set(await self.netbox.list_ips())
        current_prefixes = set(await self.netbox.list_prefixes())

        # Sync IPs
        for bare_ip, (ip_with_prefix, mac, member_id, nat_ip) in expected_ips.items():
            if bare_ip not in current_ips:
                try:
                    await self.netbox.assign_ip(ip_with_prefix, mac, member_id, nat_ip=nat_ip)
                    result.ips_created += 1
                except Exception as e:
                    result.errors.append(f"create IP {ip_with_prefix}: {e}")

        for bare_ip in current_ips:
            if bare_ip not in expected_ips:
                try:
                    await self.netbox.unassign_ip(bare_ip)
                    result.ips_deleted += 1
                except Exception as e:
                    result.errors.append(f"delete IP {bare_ip}: {e}")

        # Sync wifi prefixes
        for prefix_str, (member_id, nat_ip) in expected_prefixes.items():
            if prefix_str not in current_prefixes:
                try:
                    await self.netbox.create_wifi_prefix(prefix_str, member_id, nat_ip=nat_ip)
                    result.prefixes_created += 1
                except Exception as e:
                    result.errors.append(f"create prefix {prefix_str}: {e}")

        for prefix_str in current_prefixes:
            if prefix_str not in expected_prefixes:
                try:
                    await self.netbox.delete_wifi_prefix(prefix_str)
                    result.prefixes_deleted += 1
                except Exception as e:
                    result.errors.append(f"delete prefix {prefix_str}: {e}")

        return result

    async def _collect_device_ips(
        self,
        expected_ips: dict[str, tuple[str, str, int, str | None]],
        result: NetboxSyncResult,
    ) -> None:
        devices, _ = await self.device_repository.search_by(
            limit=_BATCH,
            offset=DEFAULT_OFFSET,
            device_filter=DeviceFilter(),
        )
        for device in devices:
            if not device.mac or not device.member:
                continue

            if device.connection_type == DeviceType.wired.name:
                await self._add_wired_ips(device, expected_ips, result)
            elif device.connection_type == DeviceType.wireless.name:
                await self._add_wireless_ips(device, expected_ips)

    async def _add_wired_ips(self, device, expected_ips, result) -> None:
        member = await self.member_repository.get_by_id(device.member)
        if not member or not is_member_active(member):
            return

        room = await self.room_repository.get_from_member(device.member)
        if not room or not room.vlan:
            return
        try:
            vlan = await self.vlan_manager.get_from_number(vlan_number=room.vlan)
        except Exception as e:
            result.errors.append(f"vlan lookup for device {device.id}: {e}")
            return

        if device.ipv4_address and device.ipv4_address != "En attente" and vlan.ipv4_network:
            prefixlen = ip_network(vlan.ipv4_network, strict=False).prefixlen
            ip_with_prefix = f"{device.ipv4_address}/{prefixlen}"
            expected_ips[device.ipv4_address] = (ip_with_prefix, device.mac, device.member, None)

        if device.ipv6_address and device.ipv6_address != "En attente" and vlan.ipv6_network:
            prefixlen6 = ip_network(vlan.ipv6_network, strict=False).prefixlen
            ip6_with_prefix = f"{device.ipv6_address}/{prefixlen6}"
            expected_ips[device.ipv6_address] = (ip6_with_prefix, device.mac, device.member, None)

    async def _add_wireless_ips(self, device, expected_ips) -> None:
        member = await self.member_repository.get_by_id(device.member)
        if not member or not member.subnet or not is_member_active(member):
            return
        prefixlen = ip_network(member.subnet, strict=False).prefixlen

        if device.ipv4_address and device.ipv4_address != "En attente":
            ip_with_prefix = f"{device.ipv4_address}/{prefixlen}"
            expected_ips[device.ipv4_address] = (ip_with_prefix, device.mac, device.member, member.ip)

    async def _collect_wifi_prefixes(
        self,
        expected_prefixes: dict[str, tuple[int, str | None]],
    ) -> None:
        members, _ = await self.member_repository.search_by(
            limit=_BATCH,
            offset=DEFAULT_OFFSET,
            filter_=MemberFilter(),
        )
        for member in members:
            if not member.subnet or not member.id or not is_member_active(member):
                continue
            expected_prefixes[member.subnet] = (member.id, member.ip)
