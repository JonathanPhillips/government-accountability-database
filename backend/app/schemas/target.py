"""Target schemas."""
from pydantic import Field
from .base import BaseSchema, TimestampSchema


class TargetBase(BaseSchema):
    """Base target schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)


class TargetCreate(TargetBase):
    """Schema for creating a target."""
    pass


class TargetUpdate(BaseSchema):
    """Schema for updating a target."""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1)


class TargetResponse(TargetBase, TimestampSchema):
    """Schema for target responses."""
    id: str
