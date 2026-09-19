"""Replace legacy device IP sentinels with NULL and enforce uniqueness.

Revision ID: 6e4d2b8a1f30
Revises: 5a7c1e9d2b4f
Create Date: 2026-09-19 00:00:00.000000

"""

from ipaddress import ip_address

import sqlalchemy as sa
from alembic import op

revision = "6e4d2b8a1f30"
down_revision = "5a7c1e9d2b4f"
branch_labels = None
depends_on = None


def _normalize_address(raw_address: str | None, version: int, device_id: int) -> str | None:
    if raw_address is None or raw_address.strip() == "En attente":
        return None

    try:
        address = ip_address(raw_address.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"Cannot migrate devices: device {device_id} contains invalid IPv{version} address {raw_address!r}"
        ) from exc

    if address.version != version:
        raise RuntimeError(
            f"Cannot migrate devices: device {device_id} contains IPv{address.version} address "
            f"{raw_address!r} in the IPv{version} column"
        )
    return str(address)


def upgrade() -> None:
    devices = sa.table(
        "devices",
        sa.column("id", sa.Integer()),
        sa.column("ip", sa.String()),
        sa.column("ipv6", sa.String()),
    )
    rows = op.get_bind().execute(sa.select(devices.c.id, devices.c.ip, devices.c.ipv6)).mappings()

    normalized_rows: list[tuple[int, str | None, str | None]] = []
    owners: dict[tuple[int, str], int] = {}
    for row in rows:
        device_id = row["id"]
        ipv4 = _normalize_address(row["ip"], 4, device_id)
        ipv6 = _normalize_address(row["ipv6"], 6, device_id)
        normalized_rows.append((device_id, ipv4, ipv6))

        for version, address in ((4, ipv4), (6, ipv6)):
            if address is None:
                continue
            key = (version, address)
            if key in owners:
                raise RuntimeError(
                    f"Cannot migrate devices: devices {owners[key]} and {device_id} share IPv{version} address {address}"
                )
            owners[key] = device_id

    for device_id, ipv4, ipv6 in normalized_rows:
        op.execute(devices.update().where(devices.c.id == device_id).values(ip=ipv4, ipv6=ipv6))

    with op.batch_alter_table("devices") as batch_op:
        batch_op.create_unique_constraint("uq_devices_ip", ["ip"])
        batch_op.create_unique_constraint("uq_devices_ipv6", ["ipv6"])


def downgrade() -> None:
    with op.batch_alter_table("devices") as batch_op:
        batch_op.drop_constraint("uq_devices_ipv6", type_="unique")
        batch_op.drop_constraint("uq_devices_ip", type_="unique")
