"""Actor service for business logic."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models import Actor, IncidentActor
from app.schemas.actor import ActorCreate, ActorUpdate


class ActorService:
    """Service for actor operations."""

    @staticmethod
    def create(db: Session, actor: ActorCreate) -> Actor:
        """Create a new actor."""
        db_actor = Actor(**actor.model_dump())
        db.add(db_actor)
        db.commit()
        db.refresh(db_actor)
        return db_actor

    @staticmethod
    def get_by_id(db: Session, actor_id: str) -> Optional[Actor]:
        """Get actor by ID."""
        return db.query(Actor).filter(Actor.id == actor_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Actor]:
        """Get actor by name."""
        return db.query(Actor).filter(Actor.name == name).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Actor]:
        """Get all actors with pagination."""
        return db.query(Actor).offset(skip).limit(limit).all()

    @staticmethod
    def get_count(db: Session) -> int:
        """Get total count of actors."""
        return db.query(Actor).count()

    @staticmethod
    def get_incidents(db: Session, actor_id: str, skip: int = 0, limit: int = 100):
        """Get all incidents involving this actor."""
        from app.models import Incident
        return db.query(Incident).join(IncidentActor).filter(
            IncidentActor.actor_id == actor_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_incident_count(db: Session, actor_id: str) -> int:
        """Get count of incidents involving this actor."""
        return db.query(func.count(IncidentActor.incident_id)).filter(
            IncidentActor.actor_id == actor_id
        ).scalar()

    @staticmethod
    def update(db: Session, actor_id: str, actor_update: ActorUpdate) -> Optional[Actor]:
        """Update an actor."""
        db_actor = db.query(Actor).filter(Actor.id == actor_id).first()
        if not db_actor:
            return None

        update_data = actor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_actor, key, value)

        db.commit()
        db.refresh(db_actor)
        return db_actor

    @staticmethod
    def delete(db: Session, actor_id: str) -> bool:
        """Delete an actor."""
        db_actor = db.query(Actor).filter(Actor.id == actor_id).first()
        if not db_actor:
            return False

        db.delete(db_actor)
        db.commit()
        return True
