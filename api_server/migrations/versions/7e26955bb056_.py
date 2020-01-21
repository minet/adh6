"""empty message

Revision ID: 7e26955bb056
Revises: c32e77911bc8
Create Date: 2020-01-21 18:59:30.306041

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7e26955bb056'
down_revision = 'c32e77911bc8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mac', sa.String(length=255), nullable=True),
    sa.Column('ip', sa.String(length=255), nullable=True),
    sa.Column('adherent_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('ipv6', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['adherent_id'], ['adherents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('portables')
    op.drop_table('ordinateurs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ordinateurs',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('mac', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('ip', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('dns', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('adherent_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('last_seen', mysql.DATETIME(), nullable=True),
    sa.Column('ipv6', mysql.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['adherent_id'], ['adherents.id'], name='ordinateurs_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('portables',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('mac', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('adherent_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('last_seen', mysql.DATETIME(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['adherent_id'], ['adherents.id'], name='portables_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('devices')
    # ### end Alembic commands ###