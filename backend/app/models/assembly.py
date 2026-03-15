import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Assembly(Base):
    __tablename__ = "assemblies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    source = Column(String(32), nullable=False)  # upload | onshape
    external_id = Column(String(255), nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="assemblies")
    components = relationship("Component", back_populates="assembly")
    change_events = relationship("ChangeEvent", back_populates="assembly")
    impact_reports = relationship("ImpactReport", back_populates="assembly")
