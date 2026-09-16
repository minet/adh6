"""Add mini_routers and mini_router_loans tables.

Revision ID: 5a7c1e9d2b4f
Revises: c6de8b7a41f2
Create Date: 2026-09-16 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "5a7c1e9d2b4f"
down_revision = "c6de8b7a41f2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mini_routers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hardware_mac", sa.String(length=17), nullable=False),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("model", sa.String(length=20), nullable=False),
        sa.Column("config_state", sa.String(length=20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hardware_mac"),
        sa.UniqueConstraint("number"),
    )
    op.create_table(
        "mini_router_loans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mini_router_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("returned_at", sa.Date(), nullable=True),
        sa.Column("deposit_amount", sa.DECIMAL(precision=8, scale=2), nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=True),
        sa.Column("deposit_status", sa.String(length=20), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["mini_router_id"], ["mini_routers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mini_router_loans_mini_router_id", "mini_router_loans", ["mini_router_id"])
    op.create_index("ix_mini_router_loans_member_id", "mini_router_loans", ["member_id"])


def downgrade():
    op.drop_table("mini_router_loans")
    op.drop_table("mini_routers")
