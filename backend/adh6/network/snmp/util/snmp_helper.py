from typing import Any

from adh6.exceptions import NetworkManagerReadError
from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
    set_cmd,
)


async def get_snmp_value(community, ip, mib, obj, oid):
    """Performs an SNMP RO request and retrieves the respons"""
    transport_target = await UdpTransportTarget.create((ip, 161))
    error_indication, error_status, error_index, var_binds = await get_cmd(
        SnmpEngine(),
        CommunityData(community),
        transport_target,
        ContextData(),
        ObjectType(ObjectIdentity(mib, obj, oid)),
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP read error:" + str(error_indication))
    elif error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    else:
        if len(var_binds) > 1:
            raise NetworkManagerReadError("SNMP read error: too many values in response")

        return var_binds[0][1].prettyPrint()  # type: ignore[index]


async def get_snmp_value_raw(community: str, ip: str, oid: str) -> str:
    """GET a single OID by raw numeric string."""
    transport_target = await UdpTransportTarget.create((ip, 161))
    error_indication, error_status, error_index, var_binds = await get_cmd(
        SnmpEngine(),
        CommunityData(community),
        transport_target,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP read error:" + str(error_indication))
    elif error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    return var_binds[0][1].prettyPrint()  # type: ignore[index]


async def set_snmp_values_raw(community: str, ip: str, oid_values: list[tuple[str, Any]]) -> None:
    """Multi-varbind SET using raw numeric OID strings."""
    transport_target = await UdpTransportTarget.create((ip, 161))
    objects = [ObjectType(ObjectIdentity(oid), value) for oid, value in oid_values]
    error_indication, error_status, error_index, var_binds = await set_cmd(
        SnmpEngine(),
        CommunityData(community),
        transport_target,
        ContextData(),
        *objects,
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP write error:" + str(error_indication))
    elif error_status:
        raise NetworkManagerReadError(
            "SNMP write error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )


async def set_snmp_value(community, ip, mib, obj, oid, value):
    """Performs an SNMP RW request and sets the given oid to the given value"""
    transport_target = await UdpTransportTarget.create((ip, 161))
    error_indication, error_status, error_index, var_binds = await set_cmd(
        SnmpEngine(),
        CommunityData(community),
        transport_target,
        ContextData(),
        ObjectType(ObjectIdentity(mib, obj, oid), value),
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP read error:" + str(error_indication))
    elif error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    else:
        if len(var_binds) > 1:
            raise NetworkManagerReadError("SNMP read error: too many values in response")

        return var_binds[0][1].prettyPrint()  # type: ignore[index]
