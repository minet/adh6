# coding=utf-8
"""
Implements everything related to SNMP-related actions
"""
from src.entity.port import Port
from src.entity.switch import Switch
from src.exceptions import NetworkManagerReadError
from src.interface_adapter.snmp.util.snmp_helper import get_SNMP_value, set_SNMP_value
from src.use_case.interface.switch_network_manager import SwitchNetworkManager
from src.util.context import log_extra
from src.util.log import LOG


class SwitchSNMPNetworkManager(SwitchNetworkManager):

    def get_port_status(self, ctx, switch: Switch = None, port: Port = None) -> bool:
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

    def update_port_status(self, ctx, switch: Switch = None, port: Port = None, status=None) -> None:
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
        pass  # pragma: no cover

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

    def update_port_vlan(self, ctx, switch: Switch = None, port: Port = None, vlan=None) -> None:
        """
        Update the VLAN assigned to a port.

        :raise PortNotFound
        """
        #pass  # pragma: no cover
        #LOG.debug("switch_network_manager_get_port_vlan_called", extra=log_extra(ctx, port=port))

        if switch is None:
            raise NetworkManagerReadError("SNMP read error: switch object was None")
        if port is None:
            raise NetworkManagerReadError("SNMP read error: port object was None")

        try:
            return set_SNMP_value(switch.community, switch.ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan',
                                  port.oid, int(vlan))
        except NetworkManagerReadError:
            raise

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

    def update_port_mab(self, ctx, switch: Switch = None, port: Port = None, mab=None) -> None:
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
            print("TENTATIVE D'UPDATE \n\n" + get_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                  port.oid))
            #return true, 200
            mab_state = get_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                  port.oid)
            print("MAB actuel : "+ mab_state)
            if mab_state == "false" :
                return set_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                      port.oid, 1)
            else :
                return set_SNMP_value(switch.community, switch.ip, 'CISCO-MAC-AUTH-BYPASS-MIB', 'cmabIfAuthEnabled',
                                  port.oid, 2)
        except NetworkManagerReadError:
            raise

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
            print(port.oid)
            return get_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid)
        except NetworkManagerReadError:
            raise

    def update_port_auth(self, ctx, switch: Switch = None, port: Port = None, auth=None) -> None:
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
            print("TENTATIVE D'UPDATE D'AUTH \n\n" + get_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid))
            #return true, 200
            auth_state = get_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid)
            print("Auth actuel : "+ auth_state)
            if auth_state == "auto" : #auth activée
                return set_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                      port.oid, 3)
            else :
                set_SNMP_value(switch.community, switch.ip, 'CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', port.oid, 1)
                return set_SNMP_value(switch.community, switch.ip, 'IEEE8021-PAE-MIB', 'dot1xAuthAuthControlledPortControl',
                                  port.oid, 2)
        except NetworkManagerReadError:
            raise

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