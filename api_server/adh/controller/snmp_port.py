import time
import logging

from connexion import NoContent
from flask import g
from pysnmp.hlapi import *

from adh.auth import auth_regular_admin
from adh.exceptions import PortNotFound
from adh.model.models import Port
from adh.util.session_decorator import require_sql


@require_sql
@auth_regular_admin
def get_port_status(port_id):
    """ [API] Get the status of the specified port_id """
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
           ObjectType(ObjectIdentity('IF-MIB', 'ifAdminStatus', port.oid)))
    )

    if errorIndication:
        return errorIndication, 500
    elif errorStatus:
        return '%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 500
    else:
        if len(varBinds) > 1:
            return "Too many values in SNMP response", 500

        logging.info("%s fetched the status of port %s", g.admin.login, str(port_id))

        status = varBinds[0][1].prettyPrint()
        if status == "up":
            return True, 200
        elif status == "down" or status == "testing":
            return False, 200
        else:
            return "Port is in unknown state, this shouldn't happen", 500

@require_sql
@auth_regular_admin
def set_port_status(port_id, state):
    """ [API] Set the status of the specified port_id to status """
    s = g.session

    try:
        port = Port.find(s, port_id)
    except PortNotFound:
        return NoContent, 404

    status = "down" if state == b'false' else "up"

    errorIndication, errorStatus, errorIndex, varBinds = next(
    setCmd(SnmpEngine(),
           CommunityData(port.switch.communaute),
           UdpTransportTarget((port.switch.ip, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('IF-MIB', 'ifAdminStatus', port.oid), status))
    )

    if errorIndication:
        return errorIndication, 500
    elif errorStatus:
        return '%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 500
    else:
        if len(varBinds) > 1:
            return "Too many values in SNMP response", 500

        logging.info("%s changed the status of port %s to %s", g.admin.login, str(port_id), status)

        status = varBinds[0][1].prettyPrint()
        if status == "up":
            return True, 200
        elif status == "down" or status == "testing":
            return False, 200
        else:
            return "Port is in unknown state, this shouldn't happen", 500

@require_sql
@auth_regular_admin
def get_port_vlan(port_id):
    """ [API] Get the VLAN of the specified port_id """
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

        logging.info("%s fetched the vlan of port %s", g.admin.login, str(port_id))

        return int(varBinds[0][1].prettyPrint()), 200

@require_sql
@auth_regular_admin
def set_port_vlan(port_id, vlan):
    """ [API] Set the VLAN of the specified port_id to vlan """
    s = g.session

    try:
        port = Port.find(s, port_id)
    except PortNotFound:
        return NoContent, 404

    errorIndication, errorStatus, errorIndex, varBinds = next(
    setCmd(SnmpEngine(),
           CommunityData(port.switch.communaute),
           UdpTransportTarget((port.switch.ip, 161)),
           ContextData(),
           ObjectType(ObjectIdentity('CISCO-VLAN-MEMBERSHIP-MIB', 'vmVlan', port.oid), int(vlan)))
    )

    if errorIndication:
        return errorIndication, 500
    elif errorStatus:
        return '%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'), 500
    else:
        if len(varBinds) > 1:
            return "Too many values in SNMP response", 500

        logging.info("%s changed the vlan of port %s to %s", g.admin.login, str(port_id), str(vlan))

        return int(varBinds[0][1].prettyPrint()), 200

@auth_regular_admin
def get_port_mab(port_id):
    return False, 200

@auth_regular_admin
def set_port_mab(port_id, mab):
    return NoContent, 204