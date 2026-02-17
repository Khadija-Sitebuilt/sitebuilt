"""Add project status field

Revision ID: 0003
Revises: 0002_add_missing_user_columns
Create Date: 2026-02-11 18:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002_add_missing_user_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type
    sa.Enum('draft', 'processing', 'for_review', 'completed', name='project_status_enum').create(op.get_bind(), checkfirst=True)
    
    # Add the status column with default value
    op.add_column('projects', sa.Column('status', postgresql.ENUM('draft', 'processing', 'for_review', 'completed', name='project_status_enum'), nullable=False, server_default='draft'))


def downgrade() -> None:
    # Remove the status column
    op.drop_column('projects', 'status')
    
    # Drop the enum type
    sa.Enum('draft', 'processing', 'for_review', 'completed', name='project_status_enum').drop(op.get_bind(), checkfirst=True)