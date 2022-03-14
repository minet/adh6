# coding=utf-8
"""
Implements everything related to SNMP-related actions
"""
from src.constants import CTX_ROLES
from src.entity.roles import Roles
from src.entity.port import Port
from src.entity.switch import Switch
from src.exceptions import NetworkManagerReadError, UnauthorizedError
from src.interface_adapter.snmp.util.snmp_helper import get_SNMP_value, set_SNMP_value
from src.use_case.decorator.auto_raise import auto_raise
from src.use_case.decorator.security import defines_security, uses_security, SecurityDefinition
from src.use_case.interface.switch_network_manager import SwitchNetworkManager

@defines_security(SecurityDefinition(
    item={
        "network": Roles.SUPERADMIN | Roles.ADMIN | Roles.NETWORK,
    },
))
class SwitchSNMPNetworkManager(SwitchNetworkManager):
    @uses_security("network")
    @auto_raise
    def get_port_status(self, ctx, switch: Switch, port: Port) -> bool:
        """
        Retrieve the status of a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_status_called", extra=log_extra(ctx, port=port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'IF-MIB', 'ifAdminStatus', port.oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def update_port_status(self, ctx, switch: Switch = None, port: Port = None) -> str:
        """
        Update the status of a port.

        :raise PortNotFound
        """
        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            port_state =  get_SNMP_value(switch.community, switch.ip, 'IF-MIB', 'ifAdminStatus', port.oid)
            if port_state == "up" :
                return set_SNMP_value(switch.community, switch.ip, 'IF-MIB', 'ifAdminStatus', port.oid, 2)
            else :
                return set_SNMP_value(switch.community, switch.ip, 'IF-MIB', 'ifAdminStatus', port.oid, 1)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_vlan(self, ctx, switch: Switch = None, port: Port = None) -> int:
        """
        Get the VLAN assigned to a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_vlan_called", extra=log_extra(ctx, port=port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan',
                                  port.oid)
        except NetworkManagerReadError:
            raise

    
    @uses_security("network")
    @auto_raise
    def update_port_vlan(self, ctx, switch: Switch = None, port: Port = None, vlan=None) -> str:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            roles = ctx.get(CTX_ROLES)
            vlan = int(vlan)
            if (
                ((vlan == 3 or vlan == 103) and Roles.VLAN_DEV.value not in roles)
                or ((vlan == 2 or vlan == 102) and Roles.VLAN_PROD.value not in roles)
                or ((vlan == 104) and Roles.VLAN_HOSTING.value not in roles)
            ):
                raise UnauthorizedError()

            return set_SNMP_value(switch.community, switch.ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', port.oid, vlan)
        except Exception as e:
            raise e

    @uses_security("network")
    @auto_raise
    def get_port_mab(self, ctx, switch: Switch = None, port: Port = None) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_mab_called", extra=log_extra(port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                  port.oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def update_port_mab(self, ctx, switch: Switch = None, port: Port = None) -> str:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        #pass  # pragma: no cover
        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            mab_state = get_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                  port.oid)
            if mab_state == "false" :
                return set_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                      port.oid, 1)
            else :
                return set_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                  port.oid, 2)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_auth(self, ctx, switch: Switch = None, port: Port = None) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_mab_called", extra=log_extra(port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def update_port_auth(self, ctx, switch: Switch = None, port: Port = None) -> None:
        """
        Update whether MAB should be active on a port.

        :raise PortNotFound
        """
        #pass  # pragma: no cover
        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            auth_state = get_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid)
            if auth_state == "auto" : #auth activée
                return set_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                      port.oid, 3)
            else :
                set_SNMP_value(switch.community, switch.ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', port.oid, 1)
                return set_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid, 2)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_use(self, ctx, switch: Switch = None, port: Port = None) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_mab_called", extra=log_extra(port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortStatus',
                                  port.oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_speed(self, ctx, switch: Switch = None, port: Port = None) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_mab_called", extra=log_extra(port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'IF-MIB', 'ifSpeed',
                                  port.oid)
        except NetworkManagerReadError:
            raise

    @uses_security("network")
    @auto_raise
    def get_port_alias(self, ctx, switch: Switch = None, port: Port = None) -> bool:
        """
        Retrieve whether MAB is active on a port.

        :raise PortNotFound
        """

        #LOG.debug("switch_network_manager_get_port_mab_called", extra=log_extra(port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return get_SNMP_value(switch.community, switch.ip, 'IF-MIB', 'ifAlias',
                                  port.oid)
        except NetworkManagerReadError:
            raise
