"""drop modifications table

Revision ID: a3f8c2d19e05
Revises: 1c0427688704
Create Date: 2026-04-26 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = 'a3f8c2d19e05'
down_revision = '1c0427688704'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_modifications_adherent_id', table_name='modifications')
    op.drop_index('ix_modifications_utilisateur_id', table_name='modifications')
    op.drop_table('modifications')


def downgrade():
    op.create_table(
        'modifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('adherent_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_modifications_adherent_id', 'modifications', ['adherent_id'])
    op.create_index('ix_modifications_utilisateur_id', 'modifications', ['utilisateur_id'])
