"""Source schemas."""
from pydantic import Field
from typing import Optional
from datetime import date
from app.models.base import SourceTypeEnum, ReliabilityEnum
from .base import BaseSchema, TimestampSchema


class SourceBase(BaseSchema):
    """Base source schema."""
    source_type: SourceTypeEnum
    title: str = Field(..., min_length=1, max_length=500)
    url: Optional[str] = Field(None, max_length=1000)
    publication_date: Optional[date] = None
    publisher: Optional[str] = Field(None, max_length=300)
    author: Optional[str] = Field(None, max_length=300)
    reliability: ReliabilityEnum = ReliabilityEnum.SECONDARY
    archived_url: Optional[str] = Field(None, max_length=1000)
    archived_locally: bool = False
    local_file_path: Optional[str] = Field(None, max_length=1000)
    excerpt: Optional[str] = None


class SourceCreate(SourceBase):
    """Schema for creating a source."""
    incident_id: str


class SourceUpdate(BaseSchema):
    """Schema for updating a source."""
    source_type: Optional[SourceTypeEnum] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    url: Optional[str] = Field(None, max_length=1000)
    publication_date: Optional[date] = None
    publisher: Optional[str] = Field(None, max_length=300)
    author: Optional[str] = Field(None, max_length=300)
    reliability: Optional[ReliabilityEnum] = None
    archived_url: Optional[str] = Field(None, max_length=1000)
    archived_locally: Optional[bool] = None
    local_file_path: Optional[str] = Field(None, max_length=1000)
    excerpt: Optional[str] = None


class SourceResponse(SourceBase, TimestampSchema):
    """Schema for source responses."""
    id: str
    incident_id: str
