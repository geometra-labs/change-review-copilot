from __future__ import annotations

import uuid

from app.core.security import hash_password
from app.db.models.core import ComparisonRun, Project, ReportArtifact, User
from app.services.cleanup_service import CleanupService
from app.tests.helpers import temporary_workspace_dir


def test_cleanup_service_safe_unlink(db_session) -> None:
    with temporary_workspace_dir("cleanup_safe_unlink") as tmp_dir:
        target = tmp_dir / "artifact.json"
        target.write_text('{"ok":true}')
        assert target.exists()

        CleanupService()._safe_unlink(str(target))

        assert not target.exists()


def test_delete_artifact_removes_file_and_row(db_session) -> None:
    user = User(email="cleanup@test.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    project = Project(owner_id=user.id, name="Cleanup", description=None)
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

    with temporary_workspace_dir("cleanup_delete_artifact") as tmp_dir:
        fake_path = tmp_dir / "artifact.json"
        fake_path.write_text("{}")

        artifact = ReportArtifact(
            comparison_run_id=comparison.id,
            artifact_type="json",
            uri=str(fake_path),
        )
        db_session.add(artifact)
        db_session.commit()
        db_session.refresh(artifact)

        CleanupService().delete_artifact(db_session, artifact)

        assert not fake_path.exists()
        assert db_session.get(ReportArtifact, artifact.id) is None
