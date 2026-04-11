"""
Implements everything related to SNMP-related actions
"""

import contextlib
from collections.abc import Callable

from adh6.decorator import log_call
from adh6.exceptions import (
    NetworkManagerReadError,
    SwitchNotFoundError,
)

from ..interfaces import PortRepository, SwitchNetworkManager, SwitchRepository
from .util.snmp_helper import (
    get_snmp_value,
    get_snmp_value_raw,
    set_snmp_value,
    set_snmp_values_raw,
)


class SwitchSNMPNetworkManager(SwitchNetworkManager):
    def __init__(self, port_repository: PortRepository, switch_repository: SwitchRepository) -> None:
        self.switch_repository = switch_repository
        self.port_repository = port_repository

    @log_call
    async def get_port_status(self, port_id: int) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "IF-MIB", "ifAdminStatus", oid)

    @log_call
    async def update_port_status(self, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        port_state = await get_snmp_value(community, ip, "IF-MIB", "ifAdminStatus", oid)
        if port_state == "up":
            return await set_snmp_value(community, ip, "IF-MIB", "ifAdminStatus", oid, 2)
        else:
            return await set_snmp_value(community, ip, "IF-MIB", "ifAdminStatus", oid, 1)

    @log_call
    async def get_port_vlan(self, port_id: int) -> int:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", oid)

    @log_call
    async def update_port_vlan(self, port_id: int, elevated: Callable, vlan: int = 1) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)

        vlan = int(vlan)
        if vlan in (2, 102, 104, 100, 11):
            elevated()

        return await set_snmp_value(community, ip, "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", oid, vlan)

    @log_call
    async def get_port_mab(self, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid)

    @log_call
    async def update_port_mab(self, port_id: int) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        mab_state = await get_snmp_value(community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid)
        if mab_state == "false":
            return await set_snmp_value(community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid, 1)
        else:
            return await set_snmp_value(community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid, 2)

    @log_call
    async def get_port_auth(self, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "IEEE8021-PAE-MIB", "dot1xAuthAuthControlledPortControl", oid)

    @log_call
    async def update_port_auth(self, port_id: int) -> None:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        auth_state = await get_snmp_value(community, ip, "IEEE8021-PAE-MIB", "dot1xAuthAuthControlledPortControl", oid)
        if auth_state == "auto":  # auth activée
            return await set_snmp_value(
                community,
                ip,
                "IEEE8021-PAE-MIB",
                "dot1xAuthAuthControlledPortControl",
                oid,
                3,
            )
        else:
            await set_snmp_value(community, ip, "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", oid, 1)
            return await set_snmp_value(
                community,
                ip,
                "IEEE8021-PAE-MIB",
                "dot1xAuthAuthControlledPortControl",
                oid,
                2,
            )

    @log_call
    async def get_port_use(self, port_id: int) -> bool:
        """
        Retrieve usage of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "IEEE8021-PAE-MIB", "dot1xAuthAuthControlledPortStatus", oid)

    @log_call
    async def get_port_speed(self, port_id: int) -> int:
        """
        Retrieve speed of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "IF-MIB", "ifSpeed", oid)

    @log_call
    async def get_port_alias(self, port_id: int) -> str:
        """
        Retrieve alias of a port.

        :raise PortNotFound
        """

        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await get_snmp_value(community, ip, "IF-MIB", "ifAlias", oid)

    @log_call
    async def update_port_alias(self, port_id: int, alias: str) -> str:
        """
        Set the description/alias of a port via IF-MIB::ifAlias.
        """
        from pysnmp.proto.rfc1902 import OctetString

        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(port_id)
        return await set_snmp_value(community, ip, "IF-MIB", "ifAlias", oid, OctetString(alias))

    async def ping_from_switch(
        self,
        switch_id: int,
        address: str,
        count: int = 5,
        timeout_ms: int = 2000,
        size: int = 100,
    ) -> dict:
        """
        Run an ICMP ping from the switch using Cisco SNMP Ping MIB (1.3.6.1.4.1.9.9.16).

        Creates a row in ciscoPingTable, waits for completion, reads results, then destroys the row.
        """
        import asyncio
        import random
        import socket

        from pysnmp.proto.rfc1902 import Integer, OctetString

        switch = await self.switch_repository.get_by_id(object_id=switch_id)
        community = await self.switch_repository.get_community(switch_id=switch_id)
        if switch is None or switch.ip is None or not isinstance(switch.ip, str):
            raise NetworkManagerReadError(f"ip for switch {switch_id} is unknown")

        ip: str = switch.ip  # type: ignore[assignment]
        # We don't need a secure random here, and this is just to avoid collisions in the unlikely event of multiple concurrent pings.
        serial = random.randint(1000, 65535)  # noqa: S311
        base_oid = "1.3.6.1.4.1.9.9.16.1.1.1"

        # Encode destination as 4-byte octet string (InetAddress for IPv4)
        addr_bytes = OctetString(socket.inet_aton(address))

        # Create the ping row and activate it in one atomic SET (createAndGo = 4)
        await set_snmp_values_raw(
            community,
            ip,
            [
                (f"{base_oid}.2.{serial}", Integer(1)),  # ciscoPingProtocol = ip(1)
                (f"{base_oid}.3.{serial}", addr_bytes),  # ciscoPingAddress
                (f"{base_oid}.4.{serial}", Integer(count)),  # ciscoPingPacketCount
                (f"{base_oid}.5.{serial}", Integer(size)),  # ciscoPingPacketSize
                (
                    f"{base_oid}.6.{serial}",
                    Integer(timeout_ms),
                ),  # ciscoPingPacketTimeout (ms)
                (f"{base_oid}.15.{serial}", OctetString("adh6")),  # ciscoPingEntryOwner
                (
                    f"{base_oid}.16.{serial}",
                    Integer(4),
                ),  # ciscoPingEntryStatus = createAndGo
            ],
        )

        # Poll ciscoPingCompleted (.14) until true; budget = count*timeout + 5s safety margin
        max_polls = max(10, int((count * timeout_ms / 1000 + 5) * 2))
        for _ in range(max_polls):
            await asyncio.sleep(0.5)
            try:
                completed = await get_snmp_value_raw(community, ip, f"{base_oid}.14.{serial}")
                if completed in ("true", "1"):
                    break
            except Exception:
                break

        # Read result columns; fall back to -1 on any error
        result: dict = {
            "sent": count,
            "received": -1,
            "minRtt": -1,
            "avgRtt": -1,
            "maxRtt": -1,
        }
        with contextlib.suppress(Exception):
            sent = int(await get_snmp_value_raw(community, ip, f"{base_oid}.9.{serial}"))
            received = int(await get_snmp_value_raw(community, ip, f"{base_oid}.10.{serial}"))
            min_rtt = int(await get_snmp_value_raw(community, ip, f"{base_oid}.11.{serial}"))
            avg_rtt = int(await get_snmp_value_raw(community, ip, f"{base_oid}.12.{serial}"))
            max_rtt = int(await get_snmp_value_raw(community, ip, f"{base_oid}.13.{serial}"))
            result = {
                "sent": sent,
                "received": received,
                "minRtt": min_rtt if received > 0 else 0,
                "avgRtt": avg_rtt if received > 0 else 0,
                "maxRtt": max_rtt if received > 0 else 0,
            }

        # Destroy the row regardless of outcome
        with contextlib.suppress(Exception):
            await set_snmp_values_raw(community, ip, [(f"{base_oid}.16.{serial}", Integer(6))])

        return result

    @log_call
    async def get_oid_switch_ipand_community_from_port_id(self, port_id) -> tuple[str, str, str]:
        port = await self.port_repository.get_by_id(object_id=port_id)
        if port.oid is None or not isinstance(port.oid, str):  # type: ignore  # TODO: typing
            raise NetworkManagerReadError(f"oidc for port {port_id} is unknown")
        if port.switch_obj is None:  # type: ignore  # TODO: typing
            raise SwitchNotFoundError(port.switch_obj)  # type: ignore  # TODO: typing
        switch = await self.switch_repository.get_by_id(object_id=port.switch_obj)  # type: ignore  # TODO: typing
        community = await self.switch_repository.get_community(switch_id=port.switch_obj)  # type: ignore  # TODO: typing
        if switch.ip is None or not isinstance(switch.ip, str):  # type: ignore  # TODO: typing
            raise NetworkManagerReadError(f"ip for switch {port.switch_obj} is unknown")  # type: ignore  # TODO: typing
        rcom = await self.port_repository.get_rcom(id=port_id)
        if rcom is not None and rcom != 0:
            community += str(rcom)
        return port.oid, switch.ip, community  # type: ignore  # TODO: typing
