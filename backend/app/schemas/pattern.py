"""Pattern schemas."""
from pydantic import Field
from typing import Optional
from .base import BaseSchema, TimestampSchema


class PatternBase(BaseSchema):
    """Base pattern schema."""
    name: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    historical_precedent: Optional[str] = None


class PatternCreate(PatternBase):
    """Schema for creating a pattern."""
    pass


class PatternUpdate(BaseSchema):
    """Schema for updating a pattern."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, min_length=1)
    historical_precedent: Optional[str] = None


class PatternResponse(PatternBase, TimestampSchema):
    """Schema for pattern responses."""
    id: str
