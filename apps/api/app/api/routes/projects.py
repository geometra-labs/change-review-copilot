from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models.core import ComparisonRun, ModelVersion, Project, User
from app.db.session import get_db
from app.schemas.project import ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("")
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    project = Project(owner_id=user.id, name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat(),
    }


@router.get("")
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    projects = db.scalars(
        select(Project).where(Project.owner_id == user.id).order_by(Project.created_at.desc())
    ).all()

    return {
        "items": [
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
            }
            for project in projects
        ]
    }


@router.get("/{project_id}")
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    model_versions = db.scalars(
        select(ModelVersion)
        .where(ModelVersion.project_id == project.id)
        .order_by(ModelVersion.created_at.desc())
    ).all()
    comparisons = db.scalars(
        select(ComparisonRun)
        .where(ComparisonRun.project_id == project.id)
        .order_by(ComparisonRun.created_at.desc())
    ).all()

    return {
        "id": str(project.id),
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat(),
        "model_versions": [
            {
                "id": str(model_version.id),
                "label": model_version.label,
                "source_type": model_version.source_type,
                "parse_status": model_version.parse_status,
                "parse_error": model_version.parse_error,
                "created_at": model_version.created_at.isoformat(),
            }
            for model_version in model_versions
        ],
        "comparisons": [
            {
                "id": str(comparison.id),
                "before_model_version_id": str(comparison.before_model_version_id),
                "after_model_version_id": str(comparison.after_model_version_id),
                "status": comparison.status,
                "summary_json": comparison.summary_json,
                "created_at": comparison.created_at.isoformat(),
            }
            for comparison in comparisons
        ],
    }


@router.delete("/{project_id}")
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from app.services.cleanup_service import CleanupService

    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    CleanupService().delete_project(db, project)
    return {"deleted": True}
