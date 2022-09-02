"""empty message

Revision ID: b6b736a5f62e
Revises: 396dbdf48d9f
Create Date: 2022-05-30 19:25:33.632547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6b736a5f62e'
down_revision = '396dbdf48d9f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('adherents', sa.Column('mail_membership', sa.Integer(), server_default='1', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('adherents', 'mail_membership')
    # ### end Alembic commands ###