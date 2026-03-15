from sqlalchemy.orm import Session

from app.models import ChangeEvent, Assembly
from app.schemas.change_event import ChangeEventCreate


def create(db: Session, assembly_id: str, body: ChangeEventCreate) -> ChangeEvent | None:
    assembly = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not assembly:
        return None
    event = ChangeEvent(
        change_type=body.change_type,
        component_id=body.component_id,
        description=body.description,
        assembly_id=assembly_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_by_assembly(db: Session, assembly_id: str) -> list[ChangeEvent]:
    return db.query(ChangeEvent).filter(ChangeEvent.assembly_id == assembly_id).all()
