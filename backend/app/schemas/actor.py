"""Actor schemas."""
from pydantic import Field, HttpUrl
from typing import Optional
from app.models.base import ActorTypeEnum
from .base import BaseSchema, TimestampSchema


class ActorBase(BaseSchema):
    """Base actor schema."""
    name: str = Field(..., min_length=1, max_length=300)
    actor_type: ActorTypeEnum
    description: Optional[str] = None
    wikipedia_url: Optional[str] = None
    active: bool = True


class ActorCreate(ActorBase):
    """Schema for creating an actor."""
    parent_actor_id: Optional[str] = None


class ActorUpdate(BaseSchema):
    """Schema for updating an actor."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    actor_type: Optional[ActorTypeEnum] = None
    description: Optional[str] = None
    wikipedia_url: Optional[str] = None
    active: Optional[bool] = None
    parent_actor_id: Optional[str] = None


class ActorResponse(ActorBase, TimestampSchema):
    """Schema for actor responses."""
    id: str
    parent_actor_id: Optional[str] = None


class ActorWithIncidentsResponse(ActorResponse):
    """Actor response with incident count."""
    incident_count: int = 0
