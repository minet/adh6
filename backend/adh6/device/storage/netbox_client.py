import asyncio
import logging
import typing as t
from functools import lru_cache
from ipaddress import ip_network

import pynetbox

from adh6.device.interfaces.netbox_repository import NetboxRepository

logger = logging.getLogger(__name__)


class PyNetboxRepository(NetboxRepository):
    def __init__(self, url: str, token: str, tag_slug: str, strict: bool) -> None:
        self._nb = pynetbox.api(url, token=token)
        self._tag_slug = tag_slug
        self._strict = strict

    async def assign_ip(self, ip_with_prefix: str, mac: str, member_id: int, nat_ip: str | None = None) -> None:
        try:
            await asyncio.to_thread(self._sync_assign_ip, ip_with_prefix, mac, member_id, nat_ip)
        except Exception as e:
            if self._strict:
                raise
            logger.warning("Netbox assign_ip error (non-fatal): %s", e)

    async def unassign_ip(self, ip_address: str) -> None:
        try:
            await asyncio.to_thread(self._sync_unassign_ip, ip_address)
        except Exception as e:
            if self._strict:
                raise
            logger.warning("Netbox unassign_ip error (non-fatal): %s", e)

    async def create_wifi_prefix(self, prefix: str, member_id: int, nat_ip: str | None = None) -> None:
        try:
            await asyncio.to_thread(self._sync_create_wifi_prefix, prefix, member_id, nat_ip)
        except Exception as e:
            if self._strict:
                raise
            logger.warning("Netbox create_wifi_prefix error (non-fatal): %s", e)

    async def delete_wifi_prefix(self, prefix: str) -> None:
        try:
            await asyncio.to_thread(self._sync_delete_wifi_prefix, prefix)
        except Exception as e:
            if self._strict:
                raise
            logger.warning("Netbox delete_wifi_prefix error (non-fatal): %s", e)

    def _get_ip_id(self, address: str) -> int | None:
        """Fetch IP ID from Netbox by address (bare or CIDR)."""
        res = self._nb.ipam.ip_addresses.get(address=address)
        return res.id if res else None

    def _sync_assign_ip(self, ip_with_prefix: str, mac: str, member_id: int, nat_ip: str | None = None) -> None:
        nat_outside = []
        if nat_ip:
            nat_id = self._get_ip_id(nat_ip)
            if nat_id:
                nat_outside = [nat_id]

        self._nb.ipam.ip_addresses.create(
            address=ip_with_prefix,
            status="active",
            tags=[{"slug": self._tag_slug}],
            custom_fields={"adh6_mac": mac, "adh6_id": member_id},
            nat_outside=nat_outside,
        )

    def _sync_unassign_ip(self, ip_address: str) -> None:
        ip = self._nb.ipam.ip_addresses.get(address=ip_address, tag=self._tag_slug)
        if ip:
            ip.delete()

    def _sync_create_wifi_prefix(self, prefix: str, member_id: int, nat_ip: str | None = None) -> None:
        net = ip_network(prefix, strict=False)
        self._nb.ipam.prefixes.create(
            prefix=prefix,
            status="active",
            tags=[{"slug": self._tag_slug}],
            custom_fields={"adh6_id": member_id},
        )
        gateway = next(net.hosts())

        nat_outside = []
        public_ip_obj = None
        if nat_ip:
            public_ip_obj = self._nb.ipam.ip_addresses.get(address=nat_ip)
            if public_ip_obj:
                nat_outside = [public_ip_obj.id]

        gateway_obj = self._nb.ipam.ip_addresses.create(
            address=f"{gateway}/{net.prefixlen}",
            description="gateway",
            status="active",
            tags=[{"slug": self._tag_slug}],
            custom_fields={"adh6_id": member_id},
            nat_outside=nat_outside,
        )

        if public_ip_obj and gateway_obj:
            public_ip_obj.update({"nat_inside": t.cast(t.Any, gateway_obj).id})

    def _sync_delete_wifi_prefix(self, prefix: str) -> None:
        for ip in self._nb.ipam.ip_addresses.filter(parent=prefix, tag=self._tag_slug):
            ip.delete()
        p = self._nb.ipam.prefixes.get(prefix=prefix, tag=self._tag_slug)
        if p:
            p.delete()

    async def list_ips(self) -> list[str]:
        try:
            return await asyncio.to_thread(self._sync_list_ips)
        except Exception as e:
            if self._strict:
                raise
            logger.warning("Netbox list_ips error (non-fatal): %s", e)
            return []

    async def list_prefixes(self) -> list[str]:
        try:
            return await asyncio.to_thread(self._sync_list_prefixes)
        except Exception as e:
            if self._strict:
                raise
            logger.warning("Netbox list_prefixes error (non-fatal): %s", e)
            return []

    def _sync_list_ips(self) -> list[str]:
        entries = self._nb.ipam.ip_addresses.filter(tag=self._tag_slug)
        # address field is "10.0.0.5/24"; strip prefix len for comparison
        return [str(entry.address).split("/")[0] for entry in entries]

    def _sync_list_prefixes(self) -> list[str]:
        entries = self._nb.ipam.prefixes.filter(tag=self._tag_slug)
        return [str(entry.prefix) for entry in entries]


@lru_cache(maxsize=1)
def get_netbox_repository() -> NetboxRepository | None:
    from adh6.config.configuration import settings

    if not settings.is_netbox_enabled:
        return None
    return PyNetboxRepository(
        url=settings.netbox_url or "",
        token=settings.netbox_token or "",
        tag_slug=settings.netbox_tag_slug,
        strict=settings.strict_netbox_check,
    )
