"""default ports.rcom to 0

adh6 no longer reads nor writes rcom, but other tools still read it from the shared database and
expect 0 rather than NULL. The database now fills it in for ports created by adh6.

Revision ID: 5e7c1b0a9d42
Revises: f2b91d47c3ae
Create Date: 2026-09-13 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = '5e7c1b0a9d42'
down_revision = 'f2b91d47c3ae'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE ports SET rcom = 0 WHERE rcom IS NULL')
    with op.batch_alter_table('ports') as batch_op:
        batch_op.alter_column('rcom', existing_type=sa.Integer(), existing_nullable=True, server_default='0')


def downgrade():
    with op.batch_alter_table('ports') as batch_op:
        batch_op.alter_column('rcom', existing_type=sa.Integer(), existing_nullable=True, server_default=None)
