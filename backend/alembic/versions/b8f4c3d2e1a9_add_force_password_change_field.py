"""Add force_password_change field to users table

Revision ID: b8f4c3d2e1a9
Revises: a7968f79e45e
Create Date: 2026-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8f4c3d2e1a9'
down_revision = 'a7968f79e45e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add force_password_change column to users table
    op.add_column('users', sa.Column('force_password_change', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove force_password_change column from users table
    op.drop_column('users', 'force_password_change')
