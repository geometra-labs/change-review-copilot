from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.change_event import ChangeEventCreate, ChangeEventResponse, ChangeEventListResponse
from app.services import change_event_service

router = APIRouter()


@router.post("/{project_id}/assemblies/{assembly_id}/change-events", response_model=ChangeEventResponse)
def create_change_event(
    project_id: str,
    assembly_id: str,
    body: ChangeEventCreate,
    db: Session = Depends(get_db),
):
    event = change_event_service.create(db, assembly_id, body)
    if not event:
        raise HTTPException(status_code=404, detail="Assembly not found")
    return _event_to_response(event)


@router.get("/{project_id}/assemblies/{assembly_id}/change-events", response_model=ChangeEventListResponse)
def list_change_events(
    project_id: str,
    assembly_id: str,
    db: Session = Depends(get_db),
):
    events = change_event_service.list_by_assembly(db, assembly_id)
    return ChangeEventListResponse(change_events=[_event_to_response(e) for e in events])


def _event_to_response(event):
    return ChangeEventResponse(
        id=event.id,
        change_type=event.change_type,
        component_id=event.component_id,
        description=event.description,
        created_at=event.created_at.isoformat() if event.created_at else "",
    )
