"""Add project detail fields

Revision ID: 0004
Revises: 0003_add_project_status
Create Date: 2026-02-11 18:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('location', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('project_manager', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('estimated_budget', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('projects', 'estimated_budget')
    op.drop_column('projects', 'project_manager')
    op.drop_column('projects', 'end_date')
    op.drop_column('projects', 'start_date')
    op.drop_column('projects', 'location')