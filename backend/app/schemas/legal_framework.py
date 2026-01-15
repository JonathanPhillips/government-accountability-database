"""Legal framework schemas."""
from pydantic import Field
from typing import Optional
from app.models.base import LegalFrameworkTypeEnum
from .base import BaseSchema, TimestampSchema


class LegalFrameworkBase(BaseSchema):
    """Base legal framework schema."""
    name: str = Field(..., min_length=1, max_length=300)
    framework_type: LegalFrameworkTypeEnum
    citation: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    url: Optional[str] = Field(None, max_length=1000)


class LegalFrameworkCreate(LegalFrameworkBase):
    """Schema for creating a legal framework."""
    pass


class LegalFrameworkUpdate(BaseSchema):
    """Schema for updating a legal framework."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    framework_type: Optional[LegalFrameworkTypeEnum] = None
    citation: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    url: Optional[str] = Field(None, max_length=1000)


class LegalFrameworkResponse(LegalFrameworkBase, TimestampSchema):
    """Schema for legal framework responses."""
    id: str
