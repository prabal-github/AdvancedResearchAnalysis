"""Augment InvestorAccount with login/usage fields

Revision ID: d3f1a2b4c6e7
Revises: c7d8e2f4a9b1
Create Date: 2025-09-04 02:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd3f1a2b4c6e7'
down_revision = 'c7d8e2f4a9b1'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('investor_account') as batch:
        batch.add_column(sa.Column('login_count', sa.Integer(), nullable=True, server_default='0'))
        batch.add_column(sa.Column('daily_usage_date', sa.Date(), nullable=True))
        batch.add_column(sa.Column('daily_usage_count', sa.Integer(), nullable=True, server_default='0'))
        batch.add_column(sa.Column('plan_notes', sa.Text(), nullable=True))
        batch.add_column(sa.Column('pan_number', sa.String(length=10), nullable=True))
        batch.add_column(sa.Column('pan_verified', sa.Boolean(), nullable=True))
        batch.add_column(sa.Column('admin_notes', sa.Text(), nullable=True))
        batch.add_column(sa.Column('approval_date', sa.DateTime(), nullable=True))
        batch.add_column(sa.Column('approved_by', sa.String(length=100), nullable=True))

def downgrade():
    with op.batch_alter_table('investor_account') as batch:
        batch.drop_column('approved_by')
        batch.drop_column('approval_date')
        batch.drop_column('admin_notes')
        batch.drop_column('pan_verified')
        batch.drop_column('pan_number')
        batch.drop_column('plan_notes')
        batch.drop_column('daily_usage_count')
        batch.drop_column('daily_usage_date')
        batch.drop_column('login_count')
