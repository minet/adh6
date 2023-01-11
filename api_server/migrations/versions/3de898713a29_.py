"""empty message

Revision ID: 3de898713a29
Revises: d86cfea89f3e
Create Date: 2022-09-05 23:06:02.338713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3de898713a29'
down_revision = 'd86cfea89f3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification_templates',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('template', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification_templates')
    # ### end Alembic commands ###