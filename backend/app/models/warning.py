import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Warning(Base):
    __tablename__ = "warnings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String(16), nullable=False)  # high | medium | low
    category = Column(String(64), nullable=False)
    message = Column(String(512), nullable=False)
    component_id = Column(String(36), nullable=True)
    interface_id = Column(String(36), nullable=True)
    impact_report_id = Column(String(36), ForeignKey("impact_reports.id"), nullable=False)

    impact_report = relationship("ImpactReport", back_populates="warnings")
