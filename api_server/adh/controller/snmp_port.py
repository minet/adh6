import time

from connexion import NoContent
from flask import g
from pysnmp.hlapi import *

from adh.auth import auth_regular_admin
from adh.exceptions import PortNotFound
from adh.model.models import Port
from adh.util.session_decorator import require_sql


@auth_regular_admin
def get_port_status(switchID, port_id):
    return NoContent, 200, True


@auth_regular_admin
def set_port_status(switchID, port_id, state):
    return NoContent, 200

@require_sql
@auth_regular_admin
def get_port_vlan(port_id):
    """ [API] Get the VLAN of the specified port_id on the specified switchID """
    s = g.session

    try:
        port = Port.find(s, port_id)
    except PortNotFound:
        return NoContent, 404

    errorIndication, errorStatus, errorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData(port.switch.communaute),
           UdpTransportTarget((port.switch.ip, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', port.oid)))
    )

    if errorIndication:
        return errorIndication, 500
    elif errorStatus:
        return '%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 500
    else:
    	if len(varBinds) > 1:
    		return "Too many values in SNMP response", 500

    	return varBinds[0][1].prettyPrint(), 200


@auth_regular_admin
def set_port_vlan(switchID, port_id, vlan):
    return NoContent, 204

@auth_regular_admin
def get_port_mab(port_id):
    return False, 200

@auth_regular_admin
def set_port_mab(port_id, mab):
    return NoContent, 204