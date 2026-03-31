from __future__ import annotations

import pathlib

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.db.models.core import (
    ComparisonRun,
    ImpactFinding,
    JobRun,
    ModelVersion,
    Part,
    PartMatch,
    Project,
    Relationship,
    ReportArtifact,
)


class CleanupService:
    def delete_project(self, db: Session, project: Project) -> None:
        model_versions = db.scalars(
            select(ModelVersion).where(ModelVersion.project_id == project.id)
        ).all()

        for model_version in model_versions:
            self._delete_model_version_related_rows(db, model_version)

        db.execute(delete(Project).where(Project.id == project.id))
        db.commit()

    def delete_model_version(self, db: Session, model_version: ModelVersion) -> None:
        self._delete_model_version_related_rows(db, model_version)
        db.commit()

    def delete_comparison(self, db: Session, comparison: ComparisonRun) -> None:
        self._delete_comparison_related_rows(db, comparison)
        db.commit()

    def delete_artifact(self, db: Session, artifact: ReportArtifact) -> None:
        self._delete_artifact_storage(artifact.uri)
        db.execute(delete(ReportArtifact).where(ReportArtifact.id == artifact.id))
        db.commit()

    def _delete_model_version_related_rows(self, db: Session, model_version: ModelVersion) -> None:
        comparisons = db.scalars(
            select(ComparisonRun).where(
                or_(
                    ComparisonRun.before_model_version_id == model_version.id,
                    ComparisonRun.after_model_version_id == model_version.id,
                )
            )
        ).all()

        for comparison in comparisons:
            self._delete_comparison_related_rows(db, comparison)

        part_ids = db.scalars(
            select(Part.id).where(Part.model_version_id == model_version.id)
        ).all()

        if part_ids:
            db.execute(delete(Relationship).where(Relationship.source_part_id.in_(part_ids)))
            db.execute(delete(Relationship).where(Relationship.target_part_id.in_(part_ids)))
            db.execute(delete(Part).where(Part.id.in_(part_ids)))

        db.execute(
            delete(JobRun).where(
                JobRun.resource_type == "model_version",
                JobRun.resource_id == model_version.id,
            )
        )
        self._delete_model_version_storage(model_version.file_uri)
        db.execute(delete(ModelVersion).where(ModelVersion.id == model_version.id))

    def _delete_comparison_related_rows(self, db: Session, comparison: ComparisonRun) -> None:
        artifacts = db.scalars(
            select(ReportArtifact).where(ReportArtifact.comparison_run_id == comparison.id)
        ).all()
        for artifact in artifacts:
            self._delete_artifact_storage(artifact.uri)

        db.execute(delete(ReportArtifact).where(ReportArtifact.comparison_run_id == comparison.id))
        db.execute(delete(ImpactFinding).where(ImpactFinding.comparison_run_id == comparison.id))
        db.execute(delete(PartMatch).where(PartMatch.comparison_run_id == comparison.id))
        db.execute(
            delete(JobRun).where(
                JobRun.resource_type == "comparison",
                JobRun.resource_id == comparison.id,
            )
        )
        db.execute(delete(ComparisonRun).where(ComparisonRun.id == comparison.id))

    def _delete_model_version_storage(self, uri: str) -> None:
        self._safe_unlink(uri)

    def _delete_artifact_storage(self, uri: str) -> None:
        self._safe_unlink(uri)

    def _safe_unlink(self, uri: str) -> None:
        try:
            path = pathlib.Path(uri)
            if path.exists() and path.is_file():
                path.unlink()
        except Exception:
            pass
