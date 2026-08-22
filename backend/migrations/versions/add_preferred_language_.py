"""add preferred_language to adherents

Revision ID: d7e1a4b93c62
Revises: a3f8c2d19e05
Create Date: 2026-08-22 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = 'd7e1a4b93c62'
down_revision = 'a3f8c2d19e05'
branch_labels = None
depends_on = None


def upgrade():
    # server_default indispensable : la colonne est NOT NULL et la table contient deja des lignes.
    # Les valeurs ainsi ecrites deviennent des preferences explicites, que MAIL_DEFAULT_LANGUAGE
    # ne modifiera pas retroactivement.
    op.add_column(
        'adherents',
        sa.Column('preferred_language', sa.String(length=2), nullable=False, server_default='fr'),
    )


def downgrade():
    op.drop_column('adherents', 'preferred_language')
