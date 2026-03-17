"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-03-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("file_uri", sa.Text(), nullable=False),
        sa.Column("parse_status", sa.String(length=50), nullable=False),
        sa.Column("parse_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "parts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("model_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_key", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_part_key", sa.String(length=255), nullable=True),
        sa.Column("transform_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("bbox_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("centroid_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("volume_estimate", sa.Float(), nullable=True),
        sa.Column("geometry_signature", sa.String(length=255), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("model_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_part_id"], ["parts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_part_id"], ["parts.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "comparison_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("before_model_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("after_model_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["before_model_version_id"], ["model_versions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["after_model_version_id"], ["model_versions.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "part_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("comparison_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("before_part_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("after_part_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("match_confidence", sa.Float(), nullable=False),
        sa.Column("match_method", sa.String(length=50), nullable=False),
        sa.Column("change_type", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["comparison_run_id"], ["comparison_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["before_part_id"], ["parts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["after_part_id"], ["parts.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "impact_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("comparison_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("risk_type", sa.String(length=50), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reason_text", sa.Text(), nullable=False),
        sa.Column("recommended_check", sa.Text(), nullable=False),
        sa.Column("rank_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["comparison_run_id"], ["comparison_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "report_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("comparison_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_type", sa.String(length=50), nullable=False),
        sa.Column("uri", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["comparison_run_id"], ["comparison_runs.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_projects_owner_id", "projects", ["owner_id"], unique=False)
    op.create_index("ix_model_versions_project_id", "model_versions", ["project_id"], unique=False)
    op.create_index("ix_parts_model_version_id", "parts", ["model_version_id"], unique=False)
    op.create_index("ix_parts_part_key", "parts", ["part_key"], unique=False)
    op.create_index("ix_relationships_model_version_id", "relationships", ["model_version_id"], unique=False)
    op.create_index("ix_relationships_source_part_id", "relationships", ["source_part_id"], unique=False)
    op.create_index("ix_relationships_target_part_id", "relationships", ["target_part_id"], unique=False)
    op.create_index("ix_comparison_runs_project_id", "comparison_runs", ["project_id"], unique=False)
    op.create_index("ix_part_matches_comparison_run_id", "part_matches", ["comparison_run_id"], unique=False)
    op.create_index("ix_impact_findings_comparison_run_id", "impact_findings", ["comparison_run_id"], unique=False)
    op.create_index("ix_impact_findings_part_id", "impact_findings", ["part_id"], unique=False)
    op.create_index("ix_report_artifacts_comparison_run_id", "report_artifacts", ["comparison_run_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_report_artifacts_comparison_run_id", table_name="report_artifacts")
    op.drop_index("ix_impact_findings_part_id", table_name="impact_findings")
    op.drop_index("ix_impact_findings_comparison_run_id", table_name="impact_findings")
    op.drop_index("ix_part_matches_comparison_run_id", table_name="part_matches")
    op.drop_index("ix_comparison_runs_project_id", table_name="comparison_runs")
    op.drop_index("ix_relationships_target_part_id", table_name="relationships")
    op.drop_index("ix_relationships_source_part_id", table_name="relationships")
    op.drop_index("ix_relationships_model_version_id", table_name="relationships")
    op.drop_index("ix_parts_part_key", table_name="parts")
    op.drop_index("ix_parts_model_version_id", table_name="parts")
    op.drop_index("ix_model_versions_project_id", table_name="model_versions")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_index("ix_users_email", table_name="users")

    op.drop_table("report_artifacts")
    op.drop_table("impact_findings")
    op.drop_table("part_matches")
    op.drop_table("comparison_runs")
    op.drop_table("relationships")
    op.drop_table("parts")
    op.drop_table("model_versions")
    op.drop_table("projects")
    op.drop_table("users")
