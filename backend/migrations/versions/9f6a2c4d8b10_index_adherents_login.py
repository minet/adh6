"""index adherents login columns

Every OIDC request without an adh6_id claim, and every API key request, resolves the member
with `login = ? OR ldap_login = ?`. Without these indexes that is a full scan of adherents.

Revision ID: 9f6a2c4d8b10
Revises: f2b91d47c3ae
Create Date: 2026-09-14 01:30:00.000000

"""

from alembic import op

revision = "9f6a2c4d8b10"
down_revision = "f2b91d47c3ae"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_adherents_login", "adherents", ["login"], unique=False)
    op.create_index("ix_adherents_ldap_login", "adherents", ["ldap_login"], unique=False)


def downgrade():
    op.drop_index("ix_adherents_ldap_login", table_name="adherents")
    op.drop_index("ix_adherents_login", table_name="adherents")
