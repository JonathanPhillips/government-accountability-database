"""IngestionQueue model for automated ingestion review."""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, DateTime, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin, IngestionStatusEnum


class IngestionQueue(Base, TimestampMixin):
    """Track automated ingestion items awaiting human review."""

    __tablename__ = "ingestion_queue"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Source information
    source_url = Column(String(1000), nullable=False)
    source_type = Column(String(100), nullable=False)  # rss, youtube, pdf, etc.
    raw_content = Column(Text, nullable=True)

    # AI-extracted structured data
    extracted_data = Column(JSON, nullable=True)

    # Review status
    status = Column(Enum(IngestionStatusEnum), nullable=False, default=IngestionStatusEnum.PENDING, index=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Link to created incident (if approved)
    created_incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)
    created_incident = relationship("Incident", backref="ingestion_source")

    # Auto-processing fields
    auto_processed = Column(Boolean, default=False, nullable=False, index=True)
    auto_confidence = Column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    auto_reason = Column(Text, nullable=True)
    keyword_score = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<IngestionQueue(id='{self.id}', status='{self.status}', source='{self.source_url[:50]}...')>"
