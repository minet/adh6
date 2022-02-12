"""empty message

Revision ID: edd3aa89b387
Revises: 619c05692de3
Create Date: 2022-02-12 18:42:56.868945

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'edd3aa89b387'
down_revision = '619c05692de3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('adherents', sa.Column('mailinglist', sa.Boolean(), nullable=False))
    op.drop_column('adherents', 'signedhosting')
    op.drop_column('adherents', 'signedminet')
    op.create_index(op.f('ix_transactions_author_id'), 'transactions', ['author_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_author_id'), table_name='transactions')
    op.add_column('adherents', sa.Column('signedminet', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('adherents', sa.Column('signedhosting', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_column('adherents', 'mailinglist')
    # ### end Alembic commands ###
