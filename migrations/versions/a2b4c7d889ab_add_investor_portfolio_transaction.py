"""Add investor_portfolio_transaction table

Revision ID: a2b4c7d889ab
Revises: c1a321a85727
Create Date: 2025-09-04 00:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a2b4c7d889ab'
down_revision = 'c1a321a85727'
branch_labels = None
depends_on = None

def upgrade():
    # --- Create investor_portfolio_transaction table ---
    op.create_table(
        'investor_portfolio_transaction',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('investor_id', sa.String(length=32), nullable=False, index=True),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('action', sa.String(length=4), nullable=False),  # BUY / SELL
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, index=False),
    )
    # Explicit indexes (Alembic won't automatically add from Column(index=True) in create_table)
    op.create_index('ix_inv_tx_investor_id', 'investor_portfolio_transaction', ['investor_id'])
    op.create_index('ix_inv_tx_executed_at', 'investor_portfolio_transaction', ['executed_at'])
    op.create_index('ix_inv_tx_ticker', 'investor_portfolio_transaction', ['ticker'])


def downgrade():
    op.drop_index('ix_inv_tx_ticker', table_name='investor_portfolio_transaction')
    op.drop_index('ix_inv_tx_executed_at', table_name='investor_portfolio_transaction')
    op.drop_index('ix_inv_tx_investor_id', table_name='investor_portfolio_transaction')
    op.drop_table('investor_portfolio_transaction')
