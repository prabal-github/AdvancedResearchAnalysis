"""Add investor_terminal_session and investor_watchlist tables

Revision ID: c7d8e2f4a9b1
Revises: b5c9e1d2a3f4
Create Date: 2025-09-04 01:55:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c7d8e2f4a9b1'
down_revision = 'b5c9e1d2a3f4'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'investor_terminal_session',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('investor_id', sa.String(length=32), nullable=False),
        sa.Column('session_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(), nullable=False),
        sa.Column('watchlist_symbols', sa.Text()),
        sa.Column('preferred_timeframes', sa.Text()),
        sa.Column('risk_settings', sa.Text()),
    )
    op.create_index('ix_inv_term_session_investor', 'investor_terminal_session', ['investor_id'])

    op.create_table(
        'investor_watchlist',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('investor_id', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('symbols', sa.Text()),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_inv_watchlist_investor', 'investor_watchlist', ['investor_id'])

def downgrade():
    op.drop_index('ix_inv_watchlist_investor', table_name='investor_watchlist')
    op.drop_table('investor_watchlist')
    op.drop_index('ix_inv_term_session_investor', table_name='investor_terminal_session')
    op.drop_table('investor_terminal_session')
