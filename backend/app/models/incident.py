"""Incident model - primary unit of documentation."""
from sqlalchemy import Column, String, Text, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from .base import (
    generate_uuid,
    TimestampMixin,
    SeverityEnum,
    VerificationStatusEnum,
    GeographicScopeEnum
)


class Incident(Base, TimestampMixin):
    """Primary unit of documentation for government accountability events."""

    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    date_occurred = Column(Date, nullable=False, index=True)
    date_range_end = Column(Date, nullable=True)  # For ongoing incidents
    summary = Column(Text, nullable=False)
    detailed_description = Column(Text, nullable=True)

    # Category relationship
    category_id = Column(String, ForeignKey("categories.id"), nullable=False, index=True)
    category = relationship("Category", backref="incidents")

    # Subcategory (optional)
    subcategory = Column(String(200), nullable=True)

    # Severity and verification
    severity = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.MEDIUM, index=True)
    verification_status = Column(
        Enum(VerificationStatusEnum),
        nullable=False,
        default=VerificationStatusEnum.UNVERIFIED,
        index=True
    )

    # Geographic information
    geographic_scope = Column(Enum(GeographicScopeEnum), nullable=False, default=GeographicScopeEnum.FEDERAL)
    location_state = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)

    # Metadata
    created_by = Column(String(100), nullable=False, default="system")

    # Relationships
    sources = relationship("Source", back_populates="incident", cascade="all, delete-orphan")
    actors = relationship("IncidentActor", back_populates="incident")
    persons = relationship("IncidentPerson", back_populates="incident")
    targets = relationship("IncidentTarget", back_populates="incident")
    legal_frameworks = relationship("IncidentLegalFramework", back_populates="incident")
    patterns = relationship("IncidentPattern", back_populates="incident")

    def __repr__(self):
        return f"<Incident(id='{self.id}', title='{self.title[:50]}...')>"
