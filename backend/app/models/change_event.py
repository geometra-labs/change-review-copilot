import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db import Base


class ChangeEvent(Base):
    __tablename__ = "change_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    change_type = Column(String(64), nullable=False)
    component_id = Column(String(36), ForeignKey("components.id"), nullable=True)
    description = Column(Text, nullable=True)
    assembly_id = Column(String(36), ForeignKey("assemblies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assembly = relationship("Assembly", back_populates="change_events")
    impact_reports = relationship("ImpactReport", back_populates="change_event")
