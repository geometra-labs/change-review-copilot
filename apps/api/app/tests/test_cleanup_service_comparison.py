from __future__ import annotations

import uuid

from app.core.security import hash_password
from app.db.models.core import ComparisonRun, ImpactFinding, JobRun, Project, ReportArtifact, User
from app.services.cleanup_service import CleanupService
from app.tests.helpers import temporary_workspace_dir


def test_delete_comparison_removes_artifacts_findings_and_jobs(db_session) -> None:
    user = User(email="cleanup-comparison@test.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    project = Project(owner_id=user.id, name="Cleanup Comparison", description=None)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    comparison = ComparisonRun(
        project_id=project.id,
        before_model_version_id=uuid.uuid4(),
        after_model_version_id=uuid.uuid4(),
        status="completed",
        summary_json={},
    )
    db_session.add(comparison)
    db_session.commit()
    db_session.refresh(comparison)

    with temporary_workspace_dir("cleanup_delete_comparison") as tmp_dir:
        artifact_path = tmp_dir / "artifact.json"
        artifact_path.write_text("{}")

        artifact = ReportArtifact(
            comparison_run_id=comparison.id,
            artifact_type="json",
            uri=str(artifact_path),
        )
        db_session.add(artifact)
        db_session.commit()
        db_session.refresh(artifact)

        finding = ImpactFinding(
            comparison_run_id=comparison.id,
            part_id=uuid.uuid4(),
            severity="low",
            risk_type="dependency_review",
            evidence_json={},
            reason_text="reason",
            recommended_check="check",
            rank_score=0.1,
        )
        job = JobRun(
            job_type="create_comparison",
            resource_type="comparison",
            resource_id=comparison.id,
            status="completed",
            metadata_json={},
        )
        db_session.add(finding)
        db_session.add(job)
        db_session.commit()
        artifact_id = artifact.id
        job_id = job.id
        finding_id = finding.id

        CleanupService().delete_comparison(db_session, comparison)

        assert not artifact_path.exists()
        assert db_session.get(ComparisonRun, comparison.id) is None
        assert db_session.get(ReportArtifact, artifact_id) is None
        assert db_session.get(JobRun, job_id) is None
        assert db_session.get(ImpactFinding, finding_id) is None
