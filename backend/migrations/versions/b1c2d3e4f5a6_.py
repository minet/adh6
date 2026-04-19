"""Add wifi_password and name to devices

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-04-19 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5a6'
down_revision = '3de898713a29'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('devices', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('devices', sa.Column('wifi_password', sa.String(length=63), nullable=True))


def downgrade():
    op.drop_column('devices', 'wifi_password')
    op.drop_column('devices', 'name')
