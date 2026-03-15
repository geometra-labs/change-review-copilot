from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.assembly import AssemblyCreate, AssemblyResponse, AssemblyListResponse
from app.services import assembly_service

router = APIRouter()


@router.post("/{project_id}/assemblies", response_model=AssemblyResponse)
def create_assembly(project_id: str, body: AssemblyCreate, db: Session = Depends(get_db)):
    assembly = assembly_service.create(db, project_id, body)
    if not assembly:
        raise HTTPException(status_code=404, detail="Project not found")
    return _assembly_to_response(assembly)


@router.get("/{project_id}/assemblies", response_model=AssemblyListResponse)
def list_assemblies(project_id: str, db: Session = Depends(get_db)):
    assemblies = assembly_service.list_by_project(db, project_id)
    return AssemblyListResponse(assemblies=[_assembly_to_response(a) for a in assemblies])


def _assembly_to_response(assembly):
    return AssemblyResponse(
        id=assembly.id,
        name=assembly.name,
        source=assembly.source,
        project_id=assembly.project_id,
        created_at=assembly.created_at.isoformat() if assembly.created_at else "",
    )
