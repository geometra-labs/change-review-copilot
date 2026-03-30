"""add job_runs

Revision ID: 0002_job_runs
Revises: 0001_initial
Create Date: 2026-03-15 01:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_job_runs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_job_runs_job_type", "job_runs", ["job_type"], unique=False)
    op.create_index("ix_job_runs_resource_type", "job_runs", ["resource_type"], unique=False)
    op.create_index("ix_job_runs_resource_id", "job_runs", ["resource_id"], unique=False)
    op.create_index("ix_job_runs_status", "job_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_job_runs_status", table_name="job_runs")
    op.drop_index("ix_job_runs_resource_id", table_name="job_runs")
    op.drop_index("ix_job_runs_resource_type", table_name="job_runs")
    op.drop_index("ix_job_runs_job_type", table_name="job_runs")
    op.drop_table("job_runs")
