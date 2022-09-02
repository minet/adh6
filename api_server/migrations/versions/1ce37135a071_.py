"""empty message

Revision ID: 1ce37135a071
Revises: 98c09e9578c6
Create Date: 2022-07-24 23:30:32.882983

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1ce37135a071'
down_revision = '98c09e9578c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role_mappings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('authentication', sa.Enum('NONE', 'API_KEY', 'OIDC', 'USER', name='authenticationmethod'), nullable=False),
    sa.Column('identifier', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('USER', 'ADMIN_READ', 'ADMIN_WRITE', 'ADMIN_PROD', 'TRESO_READ', 'TRESO_WRITE', 'NETWORK_READ', 'NETWORK_WRITE', 'NETWORK_PROD', 'NETWORK_DEV', 'NETWORK_HOSTING', name='roles'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('api_keys')
    op.create_table('api_keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=128), nullable=False),
    sa.Column('user_login', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('api_keys')
    op.create_table('api_keys',
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.drop_table('role_mappings')
    # ### end Alembic commands ###