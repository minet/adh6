"""
Read-only access to the IPv6 traceability database (trace).

The trace collector (iproutix repository, trace/) records every IPv6 address the router
sees, SLAAC and temporary addresses included, with the MAC that used it. The table lives in
its own database on the same MariaDB server: ADH6 never writes to it, and alembic does not
manage it (separate MetaData).
"""

import datetime as dt
import logging
import re
from collections.abc import Iterable
from ipaddress import IPv6Address

from sqlalchemy import Column, Date, DateTime, LargeBinary, MetaData, String, Table, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.config.configuration import settings

logger = logging.getLogger(__name__)

metadata = MetaData()

# One row per (day, address, MAC, interface), first and last time seen (UTC).
# Tests run on SQLite, without the separate database: the table is then in the main one.
ipv6_neighbors = Table(
    "ipv6_neighbors",
    metadata,
    Column("day", Date, primary_key=True),
    Column("ipv6", LargeBinary(16), primary_key=True),
    Column("mac", LargeBinary(6), primary_key=True),
    Column("interface", String(32), primary_key=True),
    Column("first_seen", DateTime, nullable=False),
    Column("last_seen", DateTime, nullable=False),
    schema=None if settings.testing else settings.trace_db_name,
)


def mac_to_bytes(mac: str | None) -> bytes | None:
    """The 6 bytes of a MAC, whatever its separators (01-23-45-67-89-AB, 0123.4567.89ab...)"""
    if not mac:
        return None
    digits = re.sub(r"[^0-9a-fA-F]", "", mac)
    if len(digits) != 12:
        return None
    return bytes.fromhex(digits)


async def recent_ipv6_by_mac(
    session: AsyncSession, macs: Iterable[bytes], since: dt.datetime
) -> dict[bytes, list[str]]:
    """IPv6 addresses seen since `since` for each MAC, most recent first.

    The trace database is an extra: if it cannot be read (missing grant, database down),
    devices are returned without IPv6 addresses rather than failing the request.
    """
    wanted = set(macs)
    if not wanted:
        return {}
    last_seen = func.max(ipv6_neighbors.c.last_seen).label("last_seen")
    stmt = (
        select(ipv6_neighbors.c.mac, ipv6_neighbors.c.ipv6, last_seen)
        .where(
            ipv6_neighbors.c.mac.in_(wanted),
            ipv6_neighbors.c.day >= since.date(),
            ipv6_neighbors.c.last_seen >= since,
        )
        .group_by(ipv6_neighbors.c.mac, ipv6_neighbors.c.ipv6)
    )
    try:
        async with session.begin_nested():
            rows = (await session.execute(stmt)).all()
    except SQLAlchemyError as exc:
        _log_unavailable(exc)
        return {}

    found: dict[bytes, list[tuple[dt.datetime, IPv6Address]]] = {}
    for mac, address, seen in rows:
        found.setdefault(bytes(mac), []).append((seen, IPv6Address(bytes(address))))
    return {
        mac: [str(address) for _, address in sorted(entries, key=lambda e: (e[0], e[1]), reverse=True)]
        for mac, entries in found.items()
    }


async def macs_for_ipv6(session: AsyncSession, address: IPv6Address) -> set[bytes]:
    """MACs that used this address over the whole retention period (6 months)"""
    stmt = select(ipv6_neighbors.c.mac).where(ipv6_neighbors.c.ipv6 == address.packed).distinct()
    try:
        async with session.begin_nested():
            return {bytes(mac) for mac in (await session.execute(stmt)).scalars()}
    except SQLAlchemyError as exc:
        _log_unavailable(exc)
        return set()


def _log_unavailable(exc: SQLAlchemyError) -> None:
    # Only the database error: the statement's parameters are MAC addresses (personal data)
    logger.warning("IPv6 traceability database unavailable: %s", getattr(exc, "orig", None) or type(exc).__name__)
