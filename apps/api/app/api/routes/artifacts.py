from __future__ import annotations

import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models.core import ComparisonRun, Project, ReportArtifact, User
from app.db.session import get_db

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("/{artifact_id}/download")
def download_artifact(
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    artifact = db.get(ReportArtifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    comparison = db.get(ComparisonRun, artifact.comparison_run_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Linked comparison not found")

    project = db.get(Project, comparison.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    path = pathlib.Path(artifact.uri)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Artifact file missing")

    return FileResponse(path=path, filename=path.name, media_type="application/json")


@router.delete("/{artifact_id}")
def delete_artifact(
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from app.services.cleanup_service import CleanupService

    artifact = db.get(ReportArtifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    comparison = db.get(ComparisonRun, artifact.comparison_run_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Linked comparison not found")

    project = db.get(Project, comparison.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    CleanupService().delete_artifact(db, artifact)
    return {"deleted": True}
