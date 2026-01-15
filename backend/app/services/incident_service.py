"""Incident service for business logic."""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from typing import List, Optional, Tuple
from app.models import (
    Incident, Source, IncidentActor, IncidentPerson, IncidentTarget,
    IncidentLegalFramework, IncidentPattern, Actor, Person, Target,
    LegalFramework, Pattern
)
from app.models.base import ActorRoleEnum, PersonRoleEnum, ViolationTypeEnum
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentFilters


class IncidentService:
    """Service for incident operations."""

    @staticmethod
    def create(db: Session, incident: IncidentCreate, created_by: str = "system") -> Incident:
        """Create a new incident with optional relationships."""
        # Create incident without relationships
        incident_data = incident.model_dump(exclude={'actor_ids', 'person_ids', 'target_ids', 'legal_framework_ids', 'pattern_ids'})
        db_incident = Incident(**incident_data, created_by=created_by)
        db.add(db_incident)
        db.flush()  # Get the ID without committing

        # Add relationships if provided
        if incident.actor_ids:
            for actor_id in incident.actor_ids:
                db.add(IncidentActor(
                    incident_id=db_incident.id,
                    actor_id=actor_id,
                    role=ActorRoleEnum.PERPETRATOR
                ))

        if incident.target_ids:
            for target_id in incident.target_ids:
                db.add(IncidentTarget(incident_id=db_incident.id, target_id=target_id))

        if incident.legal_framework_ids:
            for lf_id in incident.legal_framework_ids:
                db.add(IncidentLegalFramework(
                    incident_id=db_incident.id,
                    legal_framework_id=lf_id,
                    violation_type=ViolationTypeEnum.ALLEGED
                ))

        if incident.pattern_ids:
            for pattern_id in incident.pattern_ids:
                db.add(IncidentPattern(incident_id=db_incident.id, pattern_id=pattern_id))

        db.commit()
        db.refresh(db_incident)
        return db_incident

    @staticmethod
    def get_by_id(db: Session, incident_id: str, load_relationships: bool = False) -> Optional[Incident]:
        """Get incident by ID, optionally with relationships loaded."""
        query = db.query(Incident)
        if load_relationships:
            query = query.options(
                joinedload(Incident.sources),
                joinedload(Incident.actors),
                joinedload(Incident.persons),
                joinedload(Incident.targets),
                joinedload(Incident.legal_frameworks),
                joinedload(Incident.patterns)
            )
        return query.filter(Incident.id == incident_id).first()

    @staticmethod
    def get_list(db: Session, filters: IncidentFilters) -> Tuple[List[Incident], int]:
        """Get incidents with filtering and pagination."""
        query = db.query(Incident)

        # Apply filters
        if filters.category_id:
            query = query.filter(Incident.category_id == filters.category_id)

        if filters.severity:
            query = query.filter(Incident.severity == filters.severity)

        if filters.verification_status:
            query = query.filter(Incident.verification_status == filters.verification_status)

        if filters.geographic_scope:
            query = query.filter(Incident.geographic_scope == filters.geographic_scope)

        if filters.location_state:
            query = query.filter(Incident.location_state == filters.location_state)

        if filters.date_from:
            query = query.filter(Incident.date_occurred >= filters.date_from)

        if filters.date_to:
            query = query.filter(Incident.date_occurred <= filters.date_to)

        # Filter by actor
        if filters.actor_id:
            query = query.join(IncidentActor).filter(IncidentActor.actor_id == filters.actor_id)

        # Filter by person
        if filters.person_id:
            query = query.join(IncidentPerson).filter(IncidentPerson.person_id == filters.person_id)

        # Filter by target
        if filters.target_id:
            query = query.join(IncidentTarget).filter(IncidentTarget.target_id == filters.target_id)

        # Filter by pattern
        if filters.pattern_id:
            query = query.join(IncidentPattern).filter(IncidentPattern.pattern_id == filters.pattern_id)

        # Filter by legal framework
        if filters.legal_framework_id:
            query = query.join(IncidentLegalFramework).filter(
                IncidentLegalFramework.legal_framework_id == filters.legal_framework_id
            )

        # Search across title and summary
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(or_(
                Incident.title.ilike(search_term),
                Incident.summary.ilike(search_term),
                Incident.detailed_description.ilike(search_term)
            ))

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        incidents = query.order_by(Incident.date_occurred.desc()).offset(filters.skip).limit(filters.limit).all()

        return incidents, total

    @staticmethod
    def update(db: Session, incident_id: str, incident_update: IncidentUpdate) -> Optional[Incident]:
        """Update an incident."""
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not db_incident:
            return None

        update_data = incident_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_incident, key, value)

        db.commit()
        db.refresh(db_incident)
        return db_incident

    @staticmethod
    def delete(db: Session, incident_id: str) -> bool:
        """Delete an incident (cascade deletes sources and relationships)."""
        db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not db_incident:
            return False

        db.delete(db_incident)
        db.commit()
        return True

    @staticmethod
    def add_actor(db: Session, incident_id: str, actor_id: str, role: ActorRoleEnum) -> Optional[IncidentActor]:
        """Add an actor to an incident."""
        # Check if relationship already exists
        existing = db.query(IncidentActor).filter(
            IncidentActor.incident_id == incident_id,
            IncidentActor.actor_id == actor_id
        ).first()

        if existing:
            return existing

        incident_actor = IncidentActor(incident_id=incident_id, actor_id=actor_id, role=role)
        db.add(incident_actor)
        db.commit()
        db.refresh(incident_actor)
        return incident_actor

    @staticmethod
    def add_target(db: Session, incident_id: str, target_id: str) -> Optional[IncidentTarget]:
        """Add a target to an incident."""
        existing = db.query(IncidentTarget).filter(
            IncidentTarget.incident_id == incident_id,
            IncidentTarget.target_id == target_id
        ).first()

        if existing:
            return existing

        incident_target = IncidentTarget(incident_id=incident_id, target_id=target_id)
        db.add(incident_target)
        db.commit()
        db.refresh(incident_target)
        return incident_target

    @staticmethod
    def add_pattern(db: Session, incident_id: str, pattern_id: str) -> Optional[IncidentPattern]:
        """Add a pattern to an incident."""
        existing = db.query(IncidentPattern).filter(
            IncidentPattern.incident_id == incident_id,
            IncidentPattern.pattern_id == pattern_id
        ).first()

        if existing:
            return existing

        incident_pattern = IncidentPattern(incident_id=incident_id, pattern_id=pattern_id)
        db.add(incident_pattern)
        db.commit()
        db.refresh(incident_pattern)
        return incident_pattern

    @staticmethod
    def add_legal_framework(db: Session, incident_id: str, legal_framework_id: str, violation_type: ViolationTypeEnum) -> Optional[IncidentLegalFramework]:
        """Add a legal framework to an incident."""
        existing = db.query(IncidentLegalFramework).filter(
            IncidentLegalFramework.incident_id == incident_id,
            IncidentLegalFramework.legal_framework_id == legal_framework_id
        ).first()

        if existing:
            return existing

        incident_lf = IncidentLegalFramework(
            incident_id=incident_id,
            legal_framework_id=legal_framework_id,
            violation_type=violation_type
        )
        db.add(incident_lf)
        db.commit()
        db.refresh(incident_lf)
        return incident_lf

    @staticmethod
    def get_source_count(db: Session, incident_id: str) -> int:
        """Get count of sources for an incident."""
        return db.query(func.count(Source.id)).filter(Source.incident_id == incident_id).scalar()
