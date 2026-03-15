import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Component(Base):
    __tablename__ = "components"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    assembly_id = Column(String(36), ForeignKey("assemblies.id"), nullable=False)

    assembly = relationship("Assembly", back_populates="components")
