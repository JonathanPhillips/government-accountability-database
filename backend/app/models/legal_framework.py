"""LegalFramework model - laws, constitutional provisions, treaties."""
from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin, LegalFrameworkTypeEnum


class LegalFramework(Base, TimestampMixin):
    """Laws, constitutional provisions, treaties potentially violated."""

    __tablename__ = "legal_frameworks"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(300), nullable=False, unique=True, index=True)
    framework_type = Column(Enum(LegalFrameworkTypeEnum), nullable=False, index=True)
    citation = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)

    # Relationships
    incidents = relationship("IncidentLegalFramework", back_populates="legal_framework")

    def __repr__(self):
        return f"<LegalFramework(id='{self.id}', name='{self.name}')>"
