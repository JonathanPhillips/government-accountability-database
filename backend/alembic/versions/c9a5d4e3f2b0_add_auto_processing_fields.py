"""add auto processing fields

Revision ID: c9a5d4e3f2b0
Revises: b8f4c3d2e1a9
Create Date: 2026-01-19 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9a5d4e3f2b0'
down_revision = 'a7968f79e45e'
branch_labels = None
depends_on = None


def upgrade():
    # Add auto-processing fields to ingestion_queue table
    op.add_column('ingestion_queue', sa.Column('auto_processed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('ingestion_queue', sa.Column('auto_confidence', sa.String(length=20), nullable=True))
    op.add_column('ingestion_queue', sa.Column('auto_reason', sa.Text(), nullable=True))
    op.add_column('ingestion_queue', sa.Column('keyword_score', sa.Integer(), nullable=True))

    # Add indexes for better query performance
    op.create_index('ix_ingestion_queue_auto_processed', 'ingestion_queue', ['auto_processed'])


def downgrade():
    # Remove indexes
    op.drop_index('ix_ingestion_queue_auto_processed', table_name='ingestion_queue')

    # Remove columns
    op.drop_column('ingestion_queue', 'keyword_score')
    op.drop_column('ingestion_queue', 'auto_reason')
    op.drop_column('ingestion_queue', 'auto_confidence')
    op.drop_column('ingestion_queue', 'auto_processed')
