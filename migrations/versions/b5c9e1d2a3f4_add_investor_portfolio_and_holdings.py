"""Add investor_portfolio and investor_portfolio_holding tables

Revision ID: b5c9e1d2a3f4
Revises: a2b4c7d889ab
Create Date: 2025-09-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b5c9e1d2a3f4'
down_revision = 'a2b4c7d889ab'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'investor_portfolio',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('investor_id', sa.String(length=32), nullable=False, index=True),
        sa.Column('name', sa.String(length=200), nullable=False, default='My Portfolio'),
        sa.Column('description', sa.Text()),
        sa.Column('total_invested', sa.Float(), default=0.0),
        sa.Column('total_value', sa.Float(), default=0.0),
        sa.Column('profit_loss', sa.Float(), default=0.0),
        sa.Column('profit_loss_percentage', sa.Float(), default=0.0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_investor_portfolio_investor_id', 'investor_portfolio', ['investor_id'])

    op.create_table(
        'investor_portfolio_holding',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('portfolio_id', sa.Integer(), sa.ForeignKey('investor_portfolio.id'), nullable=False, index=True),
        sa.Column('symbol', sa.String(length=20), nullable=False, index=True),
        sa.Column('company_name', sa.String(length=200)),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('average_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), default=0.0),
        sa.Column('total_invested', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), default=0.0),
        sa.Column('profit_loss', sa.Float(), default=0.0),
        sa.Column('profit_loss_percentage', sa.Float(), default=0.0),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_investor_portfolio_holding_portfolio_id', 'investor_portfolio_holding', ['portfolio_id'])
    op.create_index('ix_investor_portfolio_holding_symbol', 'investor_portfolio_holding', ['symbol'])

def downgrade():
    op.drop_index('ix_investor_portfolio_holding_symbol', table_name='investor_portfolio_holding')
    op.drop_index('ix_investor_portfolio_holding_portfolio_id', table_name='investor_portfolio_holding')
    op.drop_table('investor_portfolio_holding')
    op.drop_index('ix_investor_portfolio_investor_id', table_name='investor_portfolio')
    op.drop_table('investor_portfolio')
