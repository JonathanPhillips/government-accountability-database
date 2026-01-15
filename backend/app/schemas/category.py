"""Category schemas."""
from pydantic import Field
from typing import Optional
from .base import BaseSchema, TimestampSchema


class CategoryBase(BaseSchema):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    id: Optional[str] = None


class CategoryUpdate(BaseSchema):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)


class CategoryResponse(CategoryBase, TimestampSchema):
    """Schema for category responses."""
    id: str
