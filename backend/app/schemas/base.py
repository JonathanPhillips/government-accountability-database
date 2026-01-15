"""Base schemas and common types."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, TypeVar, Generic
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """Schema for models with timestamps."""
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    skip: int = 0
    limit: int = 100

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skip": 0,
                "limit": 100
            }
        }
    )


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    total: int
    skip: int
    limit: int
    items: list[T]

    model_config = ConfigDict(from_attributes=True)
