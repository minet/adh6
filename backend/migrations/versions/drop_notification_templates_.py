"""drop the notification_templates table

The table was created by 3de898713a29 and never held a row: nothing ever inserted into it. Its
repository's put() only ran a SELECT, and its only sender read Flask's current_app inside a FastAPI
application, so it could not have worked. Replaced by adh6/mail/, which renders Jinja files.

Revision ID: f2b91d47c3ae
Revises: d7e1a4b93c62
Create Date: 2026-08-23 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = 'f2b91d47c3ae'
down_revision = 'd7e1a4b93c62'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('notification_templates')


def downgrade():
    op.create_table(
        'notification_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('template', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title'),
    )
