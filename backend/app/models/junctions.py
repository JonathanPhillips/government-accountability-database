"""Junction tables for many-to-many relationships."""
from sqlalchemy import Column, String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from .base import (
    generate_uuid,
    TimestampMixin,
    ActorRoleEnum,
    PersonRoleEnum,
    ViolationTypeEnum,
    RelationshipTypeEnum
)


class IncidentActor(Base, TimestampMixin):
    """Junction table linking incidents to actors with roles."""

    __tablename__ = "incident_actors"
    __table_args__ = (
        UniqueConstraint('incident_id', 'actor_id', name='uix_incident_actor'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(String, ForeignKey("actors.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(ActorRoleEnum), nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="actors")
    actor = relationship("Actor", back_populates="incidents")

    def __repr__(self):
        return f"<IncidentActor(incident_id='{self.incident_id}', actor_id='{self.actor_id}', role='{self.role}')>"


class IncidentPerson(Base, TimestampMixin):
    """Junction table linking incidents to persons with roles."""

    __tablename__ = "incident_persons"
    __table_args__ = (
        UniqueConstraint('incident_id', 'person_id', name='uix_incident_person'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id = Column(String, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(PersonRoleEnum), nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="persons")
    person = relationship("Person", back_populates="incidents")

    def __repr__(self):
        return f"<IncidentPerson(incident_id='{self.incident_id}', person_id='{self.person_id}', role='{self.role}')>"


class IncidentTarget(Base, TimestampMixin):
    """Junction table linking incidents to targeted groups."""

    __tablename__ = "incident_targets"
    __table_args__ = (
        UniqueConstraint('incident_id', 'target_id', name='uix_incident_target'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String, ForeignKey("targets.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    incident = relationship("Incident", back_populates="targets")
    target = relationship("Target", back_populates="incidents")

    def __repr__(self):
        return f"<IncidentTarget(incident_id='{self.incident_id}', target_id='{self.target_id}')>"


class IncidentLegalFramework(Base, TimestampMixin):
    """Junction table linking incidents to legal frameworks."""

    __tablename__ = "incident_legal_frameworks"
    __table_args__ = (
        UniqueConstraint('incident_id', 'legal_framework_id', name='uix_incident_legal_framework'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    legal_framework_id = Column(String, ForeignKey("legal_frameworks.id", ondelete="CASCADE"), nullable=False, index=True)
    violation_type = Column(Enum(ViolationTypeEnum), nullable=False, default=ViolationTypeEnum.ALLEGED)

    # Relationships
    incident = relationship("Incident", back_populates="legal_frameworks")
    legal_framework = relationship("LegalFramework", back_populates="incidents")

    def __repr__(self):
        return f"<IncidentLegalFramework(incident_id='{self.incident_id}', legal_framework_id='{self.legal_framework_id}')>"


class IncidentPattern(Base, TimestampMixin):
    """Junction table linking incidents to patterns."""

    __tablename__ = "incident_patterns"
    __table_args__ = (
        UniqueConstraint('incident_id', 'pattern_id', name='uix_incident_pattern'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_id = Column(String, ForeignKey("patterns.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    incident = relationship("Incident", back_populates="patterns")
    pattern = relationship("Pattern", back_populates="incidents")

    def __repr__(self):
        return f"<IncidentPattern(incident_id='{self.incident_id}', pattern_id='{self.pattern_id}')>"


class RelatedIncidents(Base, TimestampMixin):
    """Junction table for relationships between incidents."""

    __tablename__ = "related_incidents"
    __table_args__ = (
        UniqueConstraint('incident_id', 'related_incident_id', name='uix_related_incidents'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    related_incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(Enum(RelationshipTypeEnum), nullable=False)

    def __repr__(self):
        return f"<RelatedIncidents(incident_id='{self.incident_id}', related_id='{self.related_incident_id}', type='{self.relationship_type}')>"
