"""Pydantic schemas for request/response validation."""
from .incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentDetailResponse
)
from .actor import ActorCreate, ActorUpdate, ActorResponse
from .person import PersonCreate, PersonUpdate, PersonResponse
from .target import TargetCreate, TargetUpdate, TargetResponse
from .legal_framework import LegalFrameworkCreate, LegalFrameworkUpdate, LegalFrameworkResponse
from .source import SourceCreate, SourceUpdate, SourceResponse
from .pattern import PatternCreate, PatternUpdate, PatternResponse
from .category import CategoryCreate, CategoryUpdate, CategoryResponse
from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData,
    PasswordChange
)

__all__ = [
    # Incident
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentResponse",
    "IncidentListResponse",
    "IncidentDetailResponse",
    # Actor
    "ActorCreate",
    "ActorUpdate",
    "ActorResponse",
    # Person
    "PersonCreate",
    "PersonUpdate",
    "PersonResponse",
    # Target
    "TargetCreate",
    "TargetUpdate",
    "TargetResponse",
    # Legal Framework
    "LegalFrameworkCreate",
    "LegalFrameworkUpdate",
    "LegalFrameworkResponse",
    # Source
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    # Pattern
    "PatternCreate",
    "PatternUpdate",
    "PatternResponse",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    "PasswordChange",
]
