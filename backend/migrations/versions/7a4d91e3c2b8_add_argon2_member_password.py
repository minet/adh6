"""Add Argon2 password storage for federated members.

Revision ID: 7a4d91e3c2b8
Revises: 6e4d2b8a1f30
Create Date: 2026-09-19 16:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "7a4d91e3c2b8"
down_revision = "6e4d2b8a1f30"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("adherents")}
    if "password_argon2" not in columns:
        op.add_column("adherents", sa.Column("password_argon2", sa.String(length=255), nullable=True))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("adherents")}
    if "password_argon2" in columns:
        op.drop_column("adherents", "password_argon2")
