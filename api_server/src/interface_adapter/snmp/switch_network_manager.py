# coding=utf-8
"""
Implements everything related to SNMP-related actions
"""
from typing import Tuple
from src.constants import CTX_ROLES
from src.exceptions import NetworkManagerReadError, SwitchNotFoundError, UnauthorizedError
from src.interface_adapter.snmp.util.snmp_helper import get_SNMP_value, set_SNMP_value
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import defines_security, has_any_role, uses_security, SecurityDefinition, Roles
from src.use_case.interface.port_repository import PortRepository
from src.use_case.interface.switch_network_manager import SwitchNetworkManager
from src.use_case.interface.switch_repository import SwitchRepository

@defines_security(SecurityDefinition(
    item={
        "network": has_any_role([Roles.ADMIN, Roles.NETWORK]),
    },
))
class SwitchSNMPNetworkManager(SwitchNetworkManager):
    def __init__(self, port_repository: PortRepository, switch_repository: SwitchRepository) -> None:
        self.switch_repository = switch_repository
        self.port_repository = port_repository

    @uses_security("network")
    @auto_raise
    def get_port_status(self, ctx, port_id: int) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def update_port_status(self, ctx, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            port_state =  get_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid)
            if port_state == "up" :
                return set_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid, 2)
            else :
                return set_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid, 1)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_vlan(self, ctx, port_id: int) -> int:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', oid)
        except NetworkManagerReadError:
            raise

    
    @uses_security("network")
    @auto_raise
    def update_port_vlan(self, ctx, port_id: int, vlan: int = 1) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            roles = ctx.get(CTX_ROLES)
            vlan = int(vlan)
            if (
                Roles.NETWORK.value not in roles and
                (
                    ((vlan == 3 or vlan == 103) and Roles.VLAN_DEV.value not in roles)
                    or ((vlan == 2 or vlan == 102) and Roles.VLAN_PROD.value not in roles)
                    or ((vlan == 104) and Roles.VLAN_HOSTING.value not in roles)
                )
            ):
                raise UnauthorizedError()

            return set_SNMP_value(community, ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', oid, vlan)
        except Exception as e:
            raise e

    @uses_security("network")
    @auto_raise
    def get_port_mab(self, ctx, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def update_port_mab(self, ctx, port_id: int) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            mab_state = get_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid)
            if mab_state == "false" :
                return set_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid, 1)
            else :
                return set_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid, 2)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_auth(self, ctx, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def update_port_auth(self, ctx, port_id: int) -> None:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            auth_state = get_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid)
            if auth_state == "auto" : #auth activée
                return set_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid, 3)
            else :
                set_SNMP_value(community, ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', oid, 1)
                return set_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid, 2)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_use(self, ctx, port_id: int) -> bool:
        """
        Retrieve usage of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortStatus',oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_speed(self, ctx, port_id: int) -> int:
        """
        Retrieve speed of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'IF-MIB', 'ifSpeed', oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_alias(self, ctx, port_id: int) -> str:
        """
        Retrieve alias of a port.

        :raise PortNotFound
        """

        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(ctx, port_id)
        try:
            return get_SNMP_value(community, ip, 'IF-MIB', 'ifAlias', oid)
        except NetworkManagerReadError:
            raise

    @auto_raise
    def get_oid_switch_ipand_community_from_port_id(self, ctx, port_id) -> Tuple[str, str, str]:
        port = self.port_repository.get_by_id(ctx, object_id=port_id)
        if port.oid is None or not isinstance(port.oid, str):
            raise NetworkManagerReadError(f"oidc for port {port_id} is unknown")
        if port.switch_obj is None:
            raise SwitchNotFoundError(port.switch_obj)
        switch = self.switch_repository.get_by_id(ctx, object_id=port.switch_obj)
        community = self.switch_repository.get_community(ctx, switch_id=port.switch_obj)
        if switch.ip is None or not isinstance(switch.ip, str):
            raise NetworkManagerReadError(f"ip for switch {port.switch_obj} is unknown")
        return port.oid, switch.ip, community
