"""Add accuracy column to reports table

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-31 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [col["name"] for col in inspector.get_columns("reports")]
    if "accuracy" not in columns:
        op.add_column("reports", sa.Column("accuracy", sa.Float(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [col["name"] for col in inspector.get_columns("reports")]
    if "accuracy" in columns:
        op.drop_column("reports", "accuracy")
