"""
Implements everything related to SNMP-related actions
"""

from adh6.authentication import Roles
from adh6.decorator import log_call
from typing import Callable

from adh6.exceptions import (
    NetworkManagerReadError,
    SwitchNotFoundError,
    UnauthorizedError,
)

from ..interfaces import PortRepository, SwitchNetworkManager, SwitchRepository
from .util.snmp_helper import get_snmp_value, set_snmp_value


class SwitchSNMPNetworkManager(SwitchNetworkManager):
    def __init__(
        self, port_repository: PortRepository, switch_repository: SwitchRepository
    ) -> None:
        self.switch_repository = switch_repository
        self.port_repository = port_repository

    @log_call
    async def get_port_status(self, port_id: int) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(community, ip, "IF-MIB", "ifAdminStatus", oid)

    @log_call
    async def update_port_status(self, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        port_state = await get_snmp_value(community, ip, "IF-MIB", "ifAdminStatus", oid)
        if port_state == "up":
            return await set_snmp_value(
                community, ip, "IF-MIB", "ifAdminStatus", oid, 2
            )
        else:
            return await set_snmp_value(
                community, ip, "IF-MIB", "ifAdminStatus", oid, 1
            )

    @log_call
    async def get_port_vlan(self, port_id: int) -> int:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(
            community, ip, "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", oid
        )

    @log_call
    async def update_port_vlan(
        self, port_id: int, elevated: Callable, vlan: int = 1
    ) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )

        vlan = int(vlan)
        if vlan in (2, 102, 104, 100, 11):
            elevated()

        return await set_snmp_value(
            community, ip, "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", oid, vlan
        )

    @log_call
    async def get_port_mab(self, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(
            community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid
        )

    @log_call
    async def update_port_mab(self, port_id: int) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        mab_state = await get_snmp_value(
            community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid
        )
        if mab_state == "false":
            return await set_snmp_value(
                community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid, 1
            )
        else:
            return await set_snmp_value(
                community, ip, "CISCO-MAC-AUTH-BYPASS-MIB", "cmabIfAuthEnabled", oid, 2
            )

    @log_call
    async def get_port_auth(self, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(
            community, ip, "IEEE8021-PAE-MIB", "dot1xAuthAuthControlledPortControl", oid
        )

    @log_call
    async def update_port_auth(self, port_id: int) -> None:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        auth_state = await get_snmp_value(
            community, ip, "IEEE8021-PAE-MIB", "dot1xAuthAuthControlledPortControl", oid
        )
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
            await set_snmp_value(
                community, ip, "CISCO-VLAN-MEMBERSHIP-MIB", "vmVlan", oid, 1
            )
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
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(
            community, ip, "IEEE8021-PAE-MIB", "dot1xAuthAuthControlledPortStatus", oid
        )

    @log_call
    async def get_port_speed(self, port_id: int) -> int:
        """
        Retrieve speed of a port.

        :raise PortNotFound
        """
        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(community, ip, "IF-MIB", "ifSpeed", oid)

    @log_call
    async def get_port_alias(self, port_id: int) -> str:
        """
        Retrieve alias of a port.

        :raise PortNotFound
        """

        oid, ip, community = await self.get_oid_switch_ipand_community_from_port_id(
            port_id
        )
        return await get_snmp_value(community, ip, "IF-MIB", "ifAlias", oid)

    @log_call
    async def get_oid_switch_ipand_community_from_port_id(
        self, port_id
    ) -> tuple[str, str, str]:
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
