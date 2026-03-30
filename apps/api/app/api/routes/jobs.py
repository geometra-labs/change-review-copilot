from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models.core import ComparisonRun, JobRun, ModelVersion, Project, User
from app.db.session import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    job = db.get(JobRun, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.resource_type == "model_version":
        model_version = db.get(ModelVersion, job.resource_id)
        if not model_version:
            raise HTTPException(status_code=404, detail="Linked model version not found")
        project = db.get(Project, model_version.project_id)
    elif job.resource_type == "comparison":
        comparison = db.get(ComparisonRun, job.resource_id)
        if not comparison:
            raise HTTPException(status_code=404, detail="Linked comparison not found")
        project = db.get(Project, comparison.project_id)
    else:
        raise HTTPException(status_code=400, detail="Unknown resource type")

    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "id": str(job.id),
        "job_type": job.job_type,
        "resource_type": job.resource_type,
        "resource_id": str(job.resource_id),
        "status": job.status,
        "error_message": job.error_message,
        "metadata_json": job.metadata_json,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }
