from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), index=True)
    label: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[str] = mapped_column(String(50))
    file_uri: Mapped[str] = mapped_column(Text())
    parse_status: Mapped[str] = mapped_column(String(50), default="uploaded")
    parse_error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"), index=True)
    part_key: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    parent_part_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transform_json: Mapped[dict] = mapped_column(JSONB)
    bbox_json: Mapped[dict] = mapped_column(JSONB)
    centroid_json: Mapped[dict] = mapped_column(JSONB)
    volume_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry_signature: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"), index=True)
    source_part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), index=True)
    target_part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_json: Mapped[dict] = mapped_column(JSONB, default=dict)


class ComparisonRun(Base):
    __tablename__ = "comparison_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), index=True)
    before_model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"))
    after_model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.id"))
    status: Mapped[str] = mapped_column(String(50), default="queued")
    summary_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PartMatch(Base):
    __tablename__ = "part_matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comparison_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comparison_runs.id"), index=True)
    before_part_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=True)
    after_part_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=True)
    match_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    match_method: Mapped[str] = mapped_column(String(50))
    change_type: Mapped[str] = mapped_column(String(50))


class ImpactFinding(Base):
    __tablename__ = "impact_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comparison_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comparison_runs.id"), index=True)
    part_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parts.id"), index=True)
    severity: Mapped[str] = mapped_column(String(20))
    risk_type: Mapped[str] = mapped_column(String(50))
    evidence_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    reason_text: Mapped[str] = mapped_column(Text())
    recommended_check: Mapped[str] = mapped_column(Text())
    rank_score: Mapped[float] = mapped_column(Float, default=0.0)


class ReportArtifact(Base):
    __tablename__ = "report_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comparison_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comparison_runs.id"), index=True)
    artifact_type: Mapped[str] = mapped_column(String(50))
    uri: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
