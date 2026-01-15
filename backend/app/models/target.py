"""Target model - categories of people/entities targeted."""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin


class Target(Base, TimestampMixin):
    """Categories of people or entities targeted by government actions."""

    __tablename__ = "targets"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)

    # Relationships
    incidents = relationship("IncidentTarget", back_populates="target")

    def __repr__(self):
        return f"<Target(id='{self.id}', name='{self.name}')>"
