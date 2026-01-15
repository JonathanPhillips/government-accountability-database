"""Pattern model - named patterns that incidents can be part of."""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin


class Pattern(Base, TimestampMixin):
    """Named patterns that multiple incidents can be part of."""

    __tablename__ = "patterns"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(300), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    historical_precedent = Column(Text, nullable=True)  # Link to historical examples

    # Relationships
    incidents = relationship("IncidentPattern", back_populates="pattern")

    def __repr__(self):
        return f"<Pattern(id='{self.id}', name='{self.name}')>"
