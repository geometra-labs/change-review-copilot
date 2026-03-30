from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models.core import ModelVersion, Part, Project, User
from app.db.session import get_db
from app.services.job_service import JobService
from app.services.parse_service import ParseError, ParseService
from app.services.persistence_service import PersistenceService

router = APIRouter(tags=["parse"])


@router.post("/model-versions/{model_version_id}/parse")
def parse_model_version(
    model_version_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    model_version = db.get(ModelVersion, model_version_id)
    if not model_version:
        raise HTTPException(status_code=404, detail="Model version not found")

    project = db.get(Project, model_version.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    job_service = JobService()
    job = job_service.create_job(
        db,
        job_type="parse_model_version",
        resource_type="model_version",
        resource_id=model_version.id,
    )
    job_service.mark_running(db, job)

    model_version.parse_status = "running"
    model_version.parse_error = None
    db.commit()

    parser = ParseService()
    persistence = PersistenceService()

    try:
        normalized = parser.parse_model(model_version.file_uri)
        persistence.replace_model_contents(db, model_version, normalized)
        db.commit()
        job_service.mark_completed(
            db,
            job,
            metadata_json={
                "model_version_id": str(model_version.id),
                "parse_status": model_version.parse_status,
            },
        )
    except ParseError as exc:
        model_version.parse_status = "failed"
        model_version.parse_error = str(exc)
        db.commit()
        job_service.mark_failed(db, job, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        model_version.parse_status = "failed"
        model_version.parse_error = "Unexpected parse failure"
        db.commit()
        job_service.mark_failed(db, job, "Unexpected parse failure")
        raise HTTPException(status_code=500, detail="Unexpected parse failure") from exc

    return {
        "job_id": str(job.id),
        "status": job.status,
    }


@router.get("/model-versions/{model_version_id}/parts")
def list_model_parts(
    model_version_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    model_version = db.get(ModelVersion, model_version_id)
    if not model_version:
        raise HTTPException(status_code=404, detail="Model version not found")

    project = db.get(Project, model_version.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    parts = db.scalars(
        select(Part).where(Part.model_version_id == model_version_id).order_by(Part.name.asc())
    ).all()

    return {
        "items": [
            {
                "id": str(part.id),
                "part_key": part.part_key,
                "name": part.name,
                "parent_part_key": part.parent_part_key,
                "bbox_json": part.bbox_json,
                "centroid_json": part.centroid_json,
                "geometry_signature": part.geometry_signature,
            }
            for part in parts
        ]
    }
