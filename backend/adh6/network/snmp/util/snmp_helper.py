# pyright: reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

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
    next_cmd,
    set_cmd,
)


async def get_snmp_value(community: str, ip: str, mib: str, obj: str, oid: str) -> str:
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
    if error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    if len(var_binds) > 1:
        raise NetworkManagerReadError("SNMP read error: too many values in response")

    return var_binds[0][1].prettyPrint()  # type: ignore[index]


async def walk_snmp(community: str, ip: str, mib: str, obj: str) -> list[tuple[str, str]]:
    """Performs an SNMP WALK (NEXT) and returns a list of (oid_suffix, value)."""
    transport_target = await UdpTransportTarget.create((ip, 161))
    results: list[tuple[str, str]] = []
    engine = SnmpEngine()
    context = ContextData()
    auth = CommunityData(community)

    initial_oid = ObjectIdentity(mib, obj)
    # Load MIB to resolve the initial OID
    current_object_type = ObjectType(initial_oid)

    while True:
        error_indication, error_status, _error_index, var_binds = await next_cmd(
            engine,
            auth,
            transport_target,
            context,
            current_object_type,
            lexicographicMode=False,
        )

        if error_indication:
            raise NetworkManagerReadError(f"SNMP walk error: {error_indication}")
        if error_status:
            raise NetworkManagerReadError(f"SNMP walk error: {error_status}")

        if not var_binds:
            break

        # next_cmd returns a list of var_binds (one per requested OID)
        var_bind = var_binds[0]
        oid, val = var_bind

        # Check if we are still within the requested MIB object
        # lexicographicMode=False handles this mostly, but safety check is good
        if not initial_oid.isPrefixOf(oid):
            break

        full_oid = oid.prettyPrint()
        suffix = full_oid.split(".")[-1]
        results.append((suffix, val.prettyPrint()))

        # Prepare next iteration
        current_object_type = ObjectType(oid)

    return results


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
    if error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    return var_binds[0][1].prettyPrint()  # type: ignore[index]


async def get_snmp_values_raw(community: str, ip: str, oids: list[str]) -> list[str]:
    """Multi-varbind GET using raw numeric OID strings, without MIB lookup (single round trip)."""
    transport_target = await UdpTransportTarget.create((ip, 161))
    error_indication, error_status, error_index, var_binds = await get_cmd(
        SnmpEngine(),
        CommunityData(community),
        transport_target,
        ContextData(),
        *[ObjectType(ObjectIdentity(oid)) for oid in oids],
        lookupMib=False,
    )
    if error_indication:
        raise NetworkManagerReadError("SNMP read error:" + str(error_indication))
    if error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    return [value.prettyPrint() for _, value in var_binds]  # type: ignore[misc]


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
    if error_status:
        raise NetworkManagerReadError(
            "SNMP write error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )


async def set_snmp_value(community: str, ip: str, mib: str, obj: str, oid: str, value: Any) -> str:
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
    if error_status:
        raise NetworkManagerReadError(
            "SNMP read error: {} at {}".format(
                error_status.prettyPrint(),  # type: ignore[union-attr]
                (error_index and var_binds[int(error_index) - 1][0]) or "?",  # type: ignore[index]
            )
        )
    if len(var_binds) > 1:
        raise NetworkManagerReadError("SNMP read error: too many values in response")

    return var_binds[0][1].prettyPrint()  # type: ignore[index]
