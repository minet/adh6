"""Drop pending_validation column from transactions

Revision ID: 1c0427688704
Revises: 7985290c2545
Create Date: 2026-04-26 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '1c0427688704'
down_revision = '7985290c2545'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('transactions', 'pending_validation')


def downgrade():
    op.add_column('transactions', sa.Column('pending_validation', sa.Boolean(), nullable=False, server_default=sa.text('0')))
