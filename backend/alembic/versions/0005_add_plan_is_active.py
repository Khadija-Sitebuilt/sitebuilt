"""Add is_active flag to plans table

Revision ID: 0005
Revises: 0004_add_project_fields
Create Date: 2026-02-28 18:30:00

This migration adds the is_active flag to track the primary/active plan for each project.
The flag is used to indicate which plan should be displayed by default.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column already exists before adding
    # This handles cases where the column was manually added to production
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    columns = [col['name'] for col in inspector.get_columns('plans')]
    if 'is_active' not in columns:
        op.add_column('plans', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Check if column exists before dropping
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    columns = [col['name'] for col in inspector.get_columns('plans')]
    if 'is_active' in columns:
        op.drop_column('plans', 'is_active')
