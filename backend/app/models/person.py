"""Person model - specific individuals (officials, not victims)."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin


class Person(Base, TimestampMixin):
    """Specific individuals (government officials, not victims)."""

    __tablename__ = "persons"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False, index=True)
    current_title = Column(String(200), nullable=True)

    # Agency affiliation
    agency_id = Column(String, ForeignKey("actors.id"), nullable=True)
    agency = relationship("Actor", backref="personnel")

    biography_summary = Column(Text, nullable=True)

    # Relationships
    incidents = relationship("IncidentPerson", back_populates="person")

    def __repr__(self):
        return f"<Person(id='{self.id}', name='{self.name}')>"
