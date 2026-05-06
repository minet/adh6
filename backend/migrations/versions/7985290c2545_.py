"""Drop accounts/account_types/caisse tables; refactor transactions and membership

Revision ID: 7985290c2545
Revises: edd3aa89b387
Create Date: 2026-04-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '7985290c2545'
down_revision = '59527d2126f6'
branch_labels = None
depends_on = None


def upgrade():
    # Drop membership.account_id
    op.drop_index('ix_membership_account_id', table_name='membership', if_exists=True)
    op.drop_column('membership', 'account_id')

    # Add new columns to transactions
    op.add_column('transactions', sa.Column('api_key_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('product_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('product_type', sa.String(20), nullable=True))

    # Drop columns from transactions
    op.drop_index('ix_transactions_src', table_name='transactions', if_exists=True)
    op.drop_index('ix_transactions_dst', table_name='transactions', if_exists=True)
    op.drop_column('transactions', 'src')
    op.drop_column('transactions', 'dst')
    op.drop_column('transactions', 'attachments')
    op.drop_column('transactions', 'is_archive')

    # Drop tables
    op.drop_table('caisse')
    op.drop_table('accounts')
    op.drop_table('account_types')


def downgrade():
    # Recreate account_types
    op.create_table(
        'account_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Recreate accounts
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('actif', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('compte_courant', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('pinned', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('adherent_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_index('ix_accounts_type', 'accounts', ['type'])
    op.create_index('ix_accounts_adherent_id', 'accounts', ['adherent_id'])

    # Recreate caisse
    op.create_table(
        'caisse',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fond', sa.Numeric(10, 2), nullable=True),
        sa.Column('coffre', sa.Numeric(10, 2), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('linked_transaction', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_caisse_linked_transaction', 'caisse', ['linked_transaction'])

    # Restore transactions columns
    op.add_column('transactions', sa.Column('src', sa.Integer(), nullable=False))
    op.add_column('transactions', sa.Column('dst', sa.Integer(), nullable=False))
    op.add_column('transactions', sa.Column('attachments', sa.TEXT(65535), nullable=False))
    op.add_column('transactions', sa.Column('is_archive', sa.Boolean(), nullable=True))
    op.create_index('ix_transactions_src', 'transactions', ['src'])
    op.create_index('ix_transactions_dst', 'transactions', ['dst'])

    # Remove new transactions columns
    op.drop_column('transactions', 'api_key_id')
    op.drop_column('transactions', 'product_id')
    op.drop_column('transactions', 'product_type')

    # Restore membership.account_id
    op.add_column('membership', sa.Column('account_id', sa.Integer(), nullable=True))
    op.create_index('ix_membership_account_id', 'membership', ['account_id'])