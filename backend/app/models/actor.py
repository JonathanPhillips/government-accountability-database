"""Actor model - government agencies, officials, entities."""
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin, ActorTypeEnum


class Actor(Base, TimestampMixin):
    """Government agencies, officials, contractors, and entities involved in incidents."""

    __tablename__ = "actors"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(300), nullable=False, unique=True, index=True)
    actor_type = Column(Enum(ActorTypeEnum), nullable=False, index=True)

    # Hierarchical relationship (e.g., ICE -> DHS)
    parent_actor_id = Column(String, ForeignKey("actors.id"), nullable=True)
    parent_actor = relationship("Actor", remote_side=[id], backref="sub_actors")

    description = Column(Text, nullable=True)
    wikipedia_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    incidents = relationship("IncidentActor", back_populates="actor")

    def __repr__(self):
        return f"<Actor(id='{self.id}', name='{self.name}', type='{self.actor_type}')>"
