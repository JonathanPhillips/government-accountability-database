"""Source model - documentation and evidence for incidents."""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin, SourceTypeEnum, ReliabilityEnum


class Source(Base, TimestampMixin):
    """Documentation and evidence supporting incidents."""

    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=generate_uuid)

    # Incident relationship
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    incident = relationship("Incident", back_populates="sources")

    # Source details
    source_type = Column(Enum(SourceTypeEnum), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    publication_date = Column(Date, nullable=True)
    publisher = Column(String(300), nullable=True)
    author = Column(String(300), nullable=True)

    # Reliability
    reliability = Column(Enum(ReliabilityEnum), nullable=False, default=ReliabilityEnum.SECONDARY)

    # Archival
    archived_url = Column(String(1000), nullable=True)  # Wayback Machine
    archived_locally = Column(Boolean, default=False, nullable=False)
    local_file_path = Column(String(1000), nullable=True)

    # Content
    excerpt = Column(Text, nullable=True)  # Relevant quote or summary

    def __repr__(self):
        return f"<Source(id='{self.id}', type='{self.source_type}', title='{self.title[:50]}...')>"
