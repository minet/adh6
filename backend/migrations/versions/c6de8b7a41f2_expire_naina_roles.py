"""Expire temporary NainA roles at the daily cutoff and drop adherents.is_naina.

Revision ID: c6de8b7a41f2
Revises: 9f6a2c4d8b10
Create Date: 2026-09-14 16:00:00.000000

"""

from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from alembic import op

revision = "c6de8b7a41f2"
down_revision = "9f6a2c4d8b10"
branch_labels = None
depends_on = None


def _next_cutoff() -> datetime:
    paris = ZoneInfo("Europe/Paris")
    now = datetime.now(UTC).astimezone(paris)
    cutoff = datetime.combine(now.date(), time(hour=20, minute=30), tzinfo=paris)
    if now >= cutoff:
        cutoff += timedelta(days=1)
    return cutoff.astimezone(UTC).replace(tzinfo=None)


def upgrade():
    op.add_column("role_mappings", sa.Column("expires_at", sa.DateTime(), nullable=True))

    role_mappings = sa.table(
        "role_mappings",
        sa.column("authentication", sa.String()),
        sa.column("identifier", sa.String()),
        sa.column("role", sa.String()),
        sa.column("expires_at", sa.DateTime()),
    )
    adherents = sa.table(
        "adherents",
        sa.column("login", sa.String()),
        sa.column("is_naina", sa.Boolean()),
    )
    naina_logins = sa.select(adherents.c.login).where(adherents.c.is_naina.is_(True))
    naina_roles = ["ADMIN_READ", "ADMIN_WRITE", "NETWORK_READ", "NETWORK_WRITE"]
    op.execute(
        role_mappings.update()
        .where(
            role_mappings.c.authentication == "USER",
            role_mappings.c.identifier.in_(naina_logins),
            role_mappings.c.role.in_(naina_roles),
        )
        .values(expires_at=_next_cutoff())
    )

    op.drop_column("adherents", "is_naina")


def downgrade():
    op.add_column(
        "adherents",
        sa.Column("is_naina", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.drop_column("role_mappings", "expires_at")
