"""create_initial_schema

Revision ID: 0001_create_initial_schema
Revises: 
Create Date: 2026-02-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_create_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Create placement_method_enum type
    placement_method_enum = postgresql.ENUM('manual', 'gps_suggested', name='placement_method_enum')
    placement_method_enum.create(op.get_bind(), checkfirst=True)
    
    # Create tables only if they don't exist
    tables = inspector.get_table_names()
    
    # Create users table
    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('auth_uid', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('auth_uid')
        )
        op.create_index('ix_users_auth_uid', 'users', ['auth_uid'], unique=True)
    
    # Create projects table
    if 'projects' not in tables:
        op.create_table(
            'projects',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('owner_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create plans table
    if 'plans' not in tables:
        op.create_table(
            'plans',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('file_url', sa.String(), nullable=False),
            sa.Column('width', sa.Integer(), nullable=False),
            sa.Column('height', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create photos table
    if 'photos' not in tables:
        op.create_table(
            'photos',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('file_url', sa.String(), nullable=False),
            sa.Column('exif_lat', sa.Float(), nullable=True),
            sa.Column('exif_lng', sa.Float(), nullable=True),
            sa.Column('exif_timestamp', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create photo_placements table
    if 'photo_placements' not in tables:
        op.create_table(
            'photo_placements',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('photo_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('plan_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('x', sa.Float(), nullable=False),
            sa.Column('y', sa.Float(), nullable=False),
            sa.Column('placement_method', placement_method_enum, nullable=False, server_default='manual'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create reports table
    if 'reports' not in tables:
        op.create_table(
            'reports',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('project_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('file_url', sa.String(), nullable=False),
            sa.Column('file_type', sa.String(), nullable=False, server_default='html'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('reports')
    op.drop_table('photo_placements')
    op.drop_table('photos')
    op.drop_table('plans')
    op.drop_table('projects')
    op.drop_index('ix_users_auth_uid', table_name='users')
    op.drop_table('users')
    
    # Drop enum type
    sa.Enum(name='placement_method_enum').drop(op.get_bind(), checkfirst=True)
