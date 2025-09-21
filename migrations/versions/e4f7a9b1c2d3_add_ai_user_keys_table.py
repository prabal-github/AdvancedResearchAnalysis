"""add ai_user_keys table

Revision ID: e4f7a9b1c2d3
Revises: d3f1a2b4c6e7
Create Date: 2025-09-04 04:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e4f7a9b1c2d3'
down_revision = 'd3f1a2b4c6e7'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'ai_user_keys',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('investor_id', sa.Integer(), nullable=True),
        sa.Column('analyst_name', sa.String(length=120), nullable=True),
        sa.Column('admin_name', sa.String(length=120), nullable=True),
        sa.Column('provider', sa.String(length=40), nullable=False),
        sa.Column('model', sa.String(length=120), nullable=True),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('masked_key', sa.String(length=80), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_ai_user_keys_investor_id', 'ai_user_keys', ['investor_id'])
    op.create_index('ix_ai_user_keys_analyst_name', 'ai_user_keys', ['analyst_name'])
    op.create_index('ix_ai_user_keys_admin_name', 'ai_user_keys', ['admin_name'])
    op.create_index('ix_ai_user_keys_provider', 'ai_user_keys', ['provider'])

def downgrade():
    op.drop_index('ix_ai_user_keys_provider', table_name='ai_user_keys')
    op.drop_index('ix_ai_user_keys_admin_name', table_name='ai_user_keys')
    op.drop_index('ix_ai_user_keys_analyst_name', table_name='ai_user_keys')
    op.drop_index('ix_ai_user_keys_investor_id', table_name='ai_user_keys')
    op.drop_table('ai_user_keys')
