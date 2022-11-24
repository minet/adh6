# coding=utf-8
"""
Implements everything related to SNMP-related actions
"""
import typing as t

from adh6.exceptions import NetworkManagerReadError, SwitchNotFoundError, UnauthorizedError
from .util.snmp_helper import get_SNMP_value, set_SNMP_value

from adh6.authentication import Roles
from adh6.decorator import log_call
from ..interfaces import PortRepository, SwitchRepository, SwitchNetworkManager


class SwitchSNMPNetworkManager(SwitchNetworkManager):
    def __init__(self, port_repository: PortRepository, switch_repository: SwitchRepository) -> None:
        self.switch_repository = switch_repository
        self.port_repository = port_repository

    @log_call
    def get_port_status(self, port_id: int) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid)
        except NetworkManagerReadError:
            raise

    @log_call
    def update_port_status(self, port_id: int) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            port_state =  get_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid)
            if port_state == "up" :
                return set_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid, 2)
            else :
                return set_SNMP_value(community, ip, 'IF-MIB', 'ifAdminStatus', oid, 1)
        except NetworkManagerReadError:
            raise

    @log_call
    def get_port_vlan(self, port_id: int) -> int:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', oid)
        except NetworkManagerReadError:
            raise

    
    @log_call
    def update_port_vlan(self, port_id: int, vlan: int = 1) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            from adh6.context import get_roles
            roles = get_roles()
            vlan = int(vlan)
            if (
                Roles.NETWORK_WRITE.value not in roles and
                (
                    ((vlan == 3 or vlan == 103) and Roles.NETWORK_DEV.value not in roles)
                    or ((vlan == 2 or vlan == 102) and Roles.NETWORK_PROD.value not in roles)
                    or ((vlan == 104) and Roles.NETWORK_HOSTING.value not in roles)
                )
            ):
                raise UnauthorizedError()

            return set_SNMP_value(community, ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', oid, vlan)
        except Exception as e:
            raise e

    @log_call
    def get_port_mab(self, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid)
        except NetworkManagerReadError:
            raise

    @log_call
    def update_port_mab(self, port_id: int) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            mab_state = get_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid)
            if mab_state == "false" :
                return set_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid, 1)
            else :
                return set_SNMP_value(community, ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled', oid, 2)
        except NetworkManagerReadError:
            raise

    @log_call
    def get_port_auth(self, port_id: int) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid)
        except NetworkManagerReadError:
            raise

    @log_call
    def update_port_auth(self, port_id: int) -> None:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            auth_state = get_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid)
            if auth_state == "auto" : #auth activée
                return set_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid, 3)
            else :
                set_SNMP_value(community, ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', oid, 1)
                return set_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl', oid, 2)
        except NetworkManagerReadError:
            raise

    @log_call
    def get_port_use(self, port_id: int) -> bool:
        """
        Retrieve usage of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortStatus',oid)
        except NetworkManagerReadError:
            raise

    @log_call
    def get_port_speed(self, port_id: int) -> int:
        """
        Retrieve speed of a port.

        :raise PortNotFound
        """
        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'IF-MIB', 'ifSpeed', oid)
        except NetworkManagerReadError:
            raise

    @log_call
    def get_port_alias(self, port_id: int) -> str:
        """
        Retrieve alias of a port.

        :raise PortNotFound
        """

        oid, ip, community = self.get_oid_switch_ipand_community_from_port_id(port_id)
        try:
            return get_SNMP_value(community, ip, 'IF-MIB', 'ifAlias', oid)
        except NetworkManagerReadError:
            raise

    @log_call
    def get_oid_switch_ipand_community_from_port_id(self, port_id) -> t.Tuple[str, str, str]:
        port = self.port_repository.get_by_id(object_id=port_id)
        if port.oid is None or not isinstance(port.oid, str):
            raise NetworkManagerReadError(f"oidc for port {port_id} is unknown")
        if port.switch_obj is None:
            raise SwitchNotFoundError(port.switch_obj)
        switch = self.switch_repository.get_by_id(object_id=port.switch_obj)
        community = self.switch_repository.get_community(switch_id=port.switch_obj)
        if switch.ip is None or not isinstance(switch.ip, str):
            raise NetworkManagerReadError(f"ip for switch {port.switch_obj} is unknown")
        rcom = self.port_repository.get_rcom(id=port_id)
        if rcom is not None or rcom != 0:
            community += str(rcom)
        return port.oid, switch.ip, community
