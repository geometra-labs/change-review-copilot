from sqlalchemy.orm import Session

from app.models import Assembly, Project
from app.schemas.assembly import AssemblyCreate


def create(db: Session, project_id: str, body: AssemblyCreate) -> Assembly | None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    assembly = Assembly(
        name=body.name,
        source=body.source,
        external_id=body.external_id,
        project_id=project_id,
    )
    db.add(assembly)
    db.commit()
    db.refresh(assembly)
    return assembly


def list_by_project(db: Session, project_id: str) -> list[Assembly]:
    return db.query(Assembly).filter(Assembly.project_id == project_id).all()
