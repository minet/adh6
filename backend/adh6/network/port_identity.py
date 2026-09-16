import re

from adh6.exceptions import ValidationError


def normalize_port_oid(oid: str | None) -> str:
    """Ports use the positive IF-MIB ifIndex, not a name or a full OID."""
    value = (oid or "").strip()
    if not re.fullmatch(r"[0-9]{1,10}", value) or not 0 < int(value) <= 2147483647:
        raise ValidationError("Port OID must be a positive SNMP ifIndex (1-2147483647)")
    return str(int(value))
