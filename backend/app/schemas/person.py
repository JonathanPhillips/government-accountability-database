"""Person schemas."""
from pydantic import Field
from typing import Optional
from .base import BaseSchema, TimestampSchema


class PersonBase(BaseSchema):
    """Base person schema."""
    name: str = Field(..., min_length=1, max_length=200)
    current_title: Optional[str] = Field(None, max_length=200)
    biography_summary: Optional[str] = None


class PersonCreate(PersonBase):
    """Schema for creating a person."""
    agency_id: Optional[str] = None


class PersonUpdate(BaseSchema):
    """Schema for updating a person."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    current_title: Optional[str] = Field(None, max_length=200)
    biography_summary: Optional[str] = None
    agency_id: Optional[str] = None


class PersonResponse(PersonBase, TimestampSchema):
    """Schema for person responses."""
    id: str
    agency_id: Optional[str] = None
