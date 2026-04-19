"""Add permanent and wifi_only flags to adherents

Revision ID: a1b2c3d4e5f6
Revises: 3de898713a29
Create Date: 2026-04-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('adherents', sa.Column('permanent', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('adherents', sa.Column('wifi_only', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('adherents', 'wifi_only')
    op.drop_column('adherents', 'permanent')
