from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse, AssemblyRef
from app.services import project_service

router = APIRouter()


@router.post("", response_model=ProjectResponse)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    project = project_service.create(db, body.name)
    return _project_to_response(project)


@router.get("", response_model=ProjectListResponse)
def list_projects(db: Session = Depends(get_db)):
    projects = project_service.list_all(db)
    return ProjectListResponse(projects=[_project_to_response(p) for p in projects])


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_response(project, include_assemblies=True)


def _project_to_response(project, include_assemblies: bool = False):
    data = {
        "id": project.id,
        "name": project.name,
        "created_at": project.created_at.isoformat() if project.created_at else "",
    }
    if include_assemblies:
        data["assemblies"] = [
            AssemblyRef(id=a.id, name=a.name, source=a.source) for a in project.assemblies
        ]
    return ProjectResponse(**data)
