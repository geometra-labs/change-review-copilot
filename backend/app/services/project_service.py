from sqlalchemy.orm import Session

from app.models import Project


def create(db: Session, name: str) -> Project:
    project = Project(name=name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_all(db: Session) -> list[Project]:
    return db.query(Project).all()


def get_by_id(db: Session, project_id: str) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()
