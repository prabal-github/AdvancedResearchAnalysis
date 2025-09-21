"""alter ai_user_keys investor_id to string

Revision ID: f5a6b7c8d9e0
Revises: e4f7a9b1c2d3
Create Date: 2025-09-04 04:15:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f5a6b7c8d9e0'
down_revision = 'e4f7a9b1c2d3'
branch_labels = None
depends_on = None

def upgrade():
    # SQLite note: batch_alter_table for type change; Postgres direct alter works.
    with op.batch_alter_table('ai_user_keys') as batch:
        batch.alter_column('investor_id', type_=sa.String(length=60), existing_type=sa.Integer(), existing_nullable=True)


def downgrade():
    # Attempt reverse (may fail if non-numeric data present)
    with op.batch_alter_table('ai_user_keys') as batch:
        batch.alter_column('investor_id', type_=sa.Integer(), existing_type=sa.String(length=60), existing_nullable=True)
