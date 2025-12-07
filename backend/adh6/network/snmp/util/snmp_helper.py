from adh6.exceptions import NetworkManagerReadError
from pysnmp.hlapi import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    getCmd,
    setCmd,
)


def get_snmp_value(community, ip, mib, obj, oid):
    """Performs an SNMP RO request and retrieves the respons"""
    error_indication, error_status, error_index, var_binds = next(
        getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(mib, obj, oid)),
        )
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP read error:" + str(error_indication))
    elif error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(), (error_index and var_binds[int(error_index) - 1][0]) or "?"
            )
        )
    else:
        if len(var_binds) > 1:
            raise NetworkManagerReadError("SNMP read error: too many values in response")

        return var_binds[0][1].prettyPrint()


def set_snmp_value(community, ip, mib, obj, oid, value):
    """Performs an SNMP RW request and sets the given oid to the given value"""
    error_indication, error_status, error_index, var_binds = next(
        setCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(mib, obj, oid), value),
        )
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP read error:" + str(error_indication))
    elif error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(), (error_index and var_binds[int(error_index) - 1][0]) or "?"
            )
        )
    else:
        if len(var_binds) > 1:
            raise NetworkManagerReadError("SNMP read error: too many values in response")

        return var_binds[0][1].prettyPrint()
