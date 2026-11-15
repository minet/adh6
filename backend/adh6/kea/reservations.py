"""Reservations Kea should hold, computed from ADH6, and the changes to get there.

This replaces the `hosts` view of the old `dhcp2` database, with the same rules:
- a device is reserved only if its member is in a room whose room has a VLAN, and it has an IPv4;
- a wired device goes in the subnet whose id is the VLAN number;
- a wireless device goes in the subnet of the member's /28 in 10.42.0.0/16: id 1000 for
  10.42.0.16/28, then +1 per /28 (the ids of nat-wifi.conf in the kea-dhcp repository);
- a router (table `routeurs`, never written by ADH6) goes in subnet 4242.

Changes are keyed on (subnet id, MAC): Kea refuses two reservations for the same MAC in one
subnet. A reservation whose IP differs is deleted, then added again.
"""

from __future__ import annotations

import logging
from collections.abc import Collection, Iterable
from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network, ip_address
from typing import Any

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adh6.device.storage.models import Device
from adh6.kea.client import KeaClient, KeaError, KeaReservation, KeaUnavailableError
from adh6.kea.tracker import normalize_mac
from adh6.member.storage.models import Adherent
from adh6.room.storage.models import Chambre
from adh6.storage.sql.models import Routeur
from adh6.subnet.storage.models import Vlan

logger = logging.getLogger(__name__)

WIRELESS_DEVICE_TYPE = 1
ROUTER_SUBNET_ID = 4242
WIRELESS_NETWORK = IPv4Network("10.42.0.0/16")
WIRELESS_FIRST_SUBNET_ID = 1000


@dataclass(frozen=True)
class DesiredReservation:
    reservation: KeaReservation
    user_context: dict[str, Any]


@dataclass
class SyncReport:
    deleted: int = 0
    added: int = 0
    failed: int = 0
    duplicates: list[KeaReservation] = field(default_factory=list[KeaReservation])

    @property
    def changes(self) -> int:
        return self.deleted + self.added


def wireless_subnet_id(subnet: str | None) -> int | None:
    """Kea subnet id of a member's wireless /28 (10.42.0.16/28 -> 1000, 10.42.47.176/28 -> 1762).

    Same rule as the old `hosts` view: only the address counts, whatever follows it (`/28`,
    another prefix, or nothing, as some old rows have). Its /28 in 10.42.0.0/16 gives the id.
    """
    if not subnet:
        return None
    address = subnet.strip().split("/", 1)[0]
    try:
        parsed = ip_address(address)
    except ValueError:
        return None
    if not isinstance(parsed, IPv4Address) or parsed not in WIRELESS_NETWORK:
        return None
    rank = (int(parsed) - int(WIRELESS_NETWORK.network_address)) // 16
    return WIRELESS_FIRST_SUBNET_ID + rank - 1


def _ipv4(value: str | None) -> str | None:
    if not value:
        return None
    try:
        address = ip_address(value.strip())
    except ValueError:
        return None
    return str(address) if isinstance(address, IPv4Address) else None


def _mac_digits(column: Any) -> ColumnElement[str]:
    """SQL expression of a stored MAC reduced to 12 lowercase hex digits (MariaDB and SQLite)."""
    return func.lower(func.replace(func.replace(func.replace(column, "-", ""), ":", ""), ".", ""))


async def desired_reservations(session: AsyncSession, macs: Collection[str] | None = None) -> list[DesiredReservation]:
    """Every reservation Kea should hold, or only those of `macs` (normalized aa:bb:... form)."""
    digits = [mac.replace(":", "") for mac in macs] if macs is not None else None

    devices = (
        select(Device.id, Device.mac, Device.ip, Device.type, Adherent.subnet, Vlan.numero)
        .join(Adherent, Adherent.id == Device.adherent_id)
        .join(Chambre, Chambre.id == Adherent.chambre_id)
        .join(Vlan, Vlan.id == Chambre.vlan_id)
    )
    routers = (
        select(Routeur.id, Routeur.mac, Routeur.ip)
        .join(Adherent, Adherent.id == Routeur.adherent_id)
        .join(Chambre, Chambre.id == Adherent.chambre_id)
    )
    if digits is not None:
        if not digits:
            return []
        devices = devices.where(_mac_digits(Device.mac).in_(digits))
        routers = routers.where(_mac_digits(Routeur.mac).in_(digits))

    desired: list[DesiredReservation] = []
    for device_id, raw_mac, raw_ip, device_type, member_subnet, vlan_number in (await session.execute(devices)).all():
        mac, ip = normalize_mac(raw_mac), _ipv4(raw_ip)
        subnet_id = wireless_subnet_id(member_subnet) if device_type == WIRELESS_DEVICE_TYPE else vlan_number
        if mac is None or ip is None or subnet_id is None:
            continue
        desired.append(DesiredReservation(KeaReservation(subnet_id, mac, ip), {"adh6_device": device_id}))
    for router_id, raw_mac, raw_ip in (await session.execute(routers)).all():
        mac, ip = normalize_mac(raw_mac), _ipv4(raw_ip)
        if mac is None or ip is None:
            continue
        desired.append(DesiredReservation(KeaReservation(ROUTER_SUBNET_ID, mac, ip), {"adh6_router": router_id}))
    return desired


async def macs_of_members(session: AsyncSession, member_ids: Collection[int]) -> set[str]:
    """MACs of the devices and routers of these members, deleted members included."""
    if not member_ids:
        return set()
    macs: set[str] = set()
    for model in (Device, Routeur):
        stmt = select(model.mac).where(model.adherent_id.in_(member_ids))
        for raw in (await session.scalars(stmt)).all():
            mac = normalize_mac(raw)
            if mac is not None:
                macs.add(mac)
    return macs


@dataclass
class Plan:
    deletions: list[KeaReservation]
    additions: list[DesiredReservation]
    duplicates: list[KeaReservation]


def plan_changes(current: Iterable[KeaReservation], desired: Iterable[DesiredReservation]) -> Plan:
    wanted: dict[tuple[int, str], DesiredReservation] = {}
    duplicates: list[KeaReservation] = []
    for item in desired:
        key = (item.reservation.subnet_id, item.reservation.mac)
        if key in wanted:
            # Two ADH6 devices with the same MAC in one subnet: Kea can only hold one of them.
            duplicates.append(item.reservation)
            continue
        wanted[key] = item

    present: dict[tuple[int, str], KeaReservation] = {(r.subnet_id, r.mac): r for r in current}
    deletions = [r for key, r in present.items() if key not in wanted or wanted[key].reservation.ip != r.ip]
    additions = [d for key, d in wanted.items() if key not in present or present[key].ip != d.reservation.ip]
    return Plan(deletions=deletions, additions=additions, duplicates=duplicates)


async def apply_plan(client: KeaClient, plan: Plan, dry_run: bool = False) -> SyncReport:
    """Delete first, then add: an IP freed by one device can be given to another in the same run.

    A refused command is logged and counted, and the others go on. If no Kea server answers,
    KeaUnavailableError stops everything: the nightly reconciliation will catch up.
    """
    report = SyncReport(duplicates=plan.duplicates)
    for reservation in plan.deletions:
        if dry_run:
            logger.info("kea_reservation_delete subnet=%s mac=%s ip=%s (dry run)", *_fields(reservation))
            report.deleted += 1
            continue
        try:
            await client.delete(reservation.subnet_id, reservation.mac)
            report.deleted += 1
        except KeaUnavailableError:
            raise
        except KeaError:
            logger.warning("kea_reservation_delete_failed subnet=%s mac=%s ip=%s", *_fields(reservation), exc_info=True)
            report.failed += 1
    for item in plan.additions:
        if dry_run:
            logger.info("kea_reservation_add subnet=%s mac=%s ip=%s (dry run)", *_fields(item.reservation))
            report.added += 1
            continue
        try:
            await client.add(item.reservation, item.user_context)
            report.added += 1
        except KeaUnavailableError:
            raise
        except KeaError:
            logger.warning(
                "kea_reservation_add_failed subnet=%s mac=%s ip=%s", *_fields(item.reservation), exc_info=True
            )
            report.failed += 1
    for reservation in plan.duplicates:
        logger.warning("kea_reservation_duplicate subnet=%s mac=%s ip=%s", *_fields(reservation))
    return report


def _fields(reservation: KeaReservation) -> tuple[int, str, str]:
    return reservation.subnet_id, reservation.mac, reservation.ip


async def sync_macs(
    client: KeaClient, session: AsyncSession, macs: Collection[str], dry_run: bool = False
) -> SyncReport:
    """Bring Kea in line with ADH6 for these MACs only."""
    if not macs:
        return SyncReport()
    desired = await desired_reservations(session, macs)
    current: list[KeaReservation] = []
    for mac in sorted(macs):
        current.extend(await client.reservations_for_mac(mac))
    return await apply_plan(client, plan_changes(current, desired), dry_run)


async def reconcile(client: KeaClient, session: AsyncSession, dry_run: bool = False) -> SyncReport:
    """Bring Kea in line with ADH6 for every reservation.

    Kea then holds exactly what ADH6 computes: a reservation added to Kea by hand is deleted.
    """
    current = await client.all_reservations()
    desired = await desired_reservations(session)
    return await apply_plan(client, plan_changes(current, desired), dry_run)
