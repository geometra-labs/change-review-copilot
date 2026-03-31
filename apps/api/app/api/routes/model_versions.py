from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models.core import ModelVersion, Project, User
from app.db.session import get_db
from app.services.storage_service import StorageService

router = APIRouter(tags=["model_versions"])


@router.post("/projects/{project_id}/model-versions")
async def upload_model_version(
    project_id: uuid.UUID,
    label: str = Form(...),
    source_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    storage = StorageService()
    try:
        stored = await storage.save_upload(file, str(project_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    mv = ModelVersion(
        project_id=project_id,
        label=label,
        source_type=source_type,
        file_uri=stored.uri,
        parse_status="uploaded",
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)

    return {
        "id": str(mv.id),
        "project_id": str(mv.project_id),
        "label": mv.label,
        "source_type": mv.source_type,
        "file_uri": mv.file_uri,
        "parse_status": mv.parse_status,
        "created_at": mv.created_at.isoformat(),
    }


@router.get("/model-versions/{model_version_id}")
def get_model_version(
    model_version_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    mv = db.get(ModelVersion, model_version_id)
    if not mv:
        raise HTTPException(status_code=404, detail="Model version not found")

    project = db.get(Project, mv.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "id": str(mv.id),
        "project_id": str(mv.project_id),
        "label": mv.label,
        "source_type": mv.source_type,
        "file_uri": mv.file_uri,
        "parse_status": mv.parse_status,
        "parse_error": mv.parse_error,
        "created_at": mv.created_at.isoformat(),
    }


@router.delete("/model-versions/{model_version_id}")
def delete_model_version(
    model_version_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from app.services.cleanup_service import CleanupService

    model_version = db.get(ModelVersion, model_version_id)
    if not model_version:
        raise HTTPException(status_code=404, detail="Model version not found")

    project = db.get(Project, model_version.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    CleanupService().delete_model_version(db, model_version)
    return {"deleted": True}
