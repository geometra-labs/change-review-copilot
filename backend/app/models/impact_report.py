import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db import Base


class ImpactReport(Base):
    __tablename__ = "impact_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    change_event_id = Column(String(36), ForeignKey("change_events.id"), nullable=False)
    assembly_id = Column(String(36), ForeignKey("assemblies.id"), nullable=False)
    affected_component_ids = Column(Text, nullable=True)  # JSON array string
    inspect_next = Column(Text, nullable=True)  # JSON array string
    created_at = Column(DateTime, default=datetime.utcnow)

    change_event = relationship("ChangeEvent", back_populates="impact_reports")
    assembly = relationship("Assembly", back_populates="impact_reports")
    warnings = relationship("Warning", back_populates="impact_report")
