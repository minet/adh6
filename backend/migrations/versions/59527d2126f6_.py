"""add publicly_accessible to ports

Revision ID: 59527d2126f6
Revises: a1b2c3d4e5f6
Create Date: 2026-04-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '59527d2126f6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ports', sa.Column('publicly_accessible', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('ports', 'publicly_accessible')
