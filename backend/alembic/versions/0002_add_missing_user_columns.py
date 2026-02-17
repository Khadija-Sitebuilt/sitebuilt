"""add_missing_user_columns

Revision ID: 0002_add_missing_user_columns
Revises: 0001_create_initial_schema
Create Date: 2026-02-10 12:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002_add_missing_user_columns'
down_revision: Union[str, Sequence[str], None] = '0001_create_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # Add missing columns if they don't exist
    if 'email' not in columns:
        op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    if 'full_name' not in columns:
        op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    if 'avatar_url' not in columns:
        op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'email')
