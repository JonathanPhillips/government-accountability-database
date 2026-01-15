"""Incident schemas."""
from pydantic import Field
from typing import Optional, List
from datetime import date
from app.models.base import (
    SeverityEnum,
    VerificationStatusEnum,
    GeographicScopeEnum,
    ActorRoleEnum,
    PersonRoleEnum,
    ViolationTypeEnum
)
from .base import BaseSchema, TimestampSchema
from .source import SourceResponse
from .actor import ActorResponse
from .person import PersonResponse
from .target import TargetResponse
from .legal_framework import LegalFrameworkResponse
from .pattern import PatternResponse


class IncidentBase(BaseSchema):
    """Base incident schema."""
    title: str = Field(..., min_length=1, max_length=500)
    date_occurred: date
    date_range_end: Optional[date] = None
    summary: str = Field(..., min_length=1)
    detailed_description: Optional[str] = None
    category_id: str
    subcategory: Optional[str] = Field(None, max_length=200)
    severity: SeverityEnum = SeverityEnum.MEDIUM
    verification_status: VerificationStatusEnum = VerificationStatusEnum.UNVERIFIED
    geographic_scope: GeographicScopeEnum = GeographicScopeEnum.FEDERAL
    location_state: Optional[str] = Field(None, max_length=100)
    location_city: Optional[str] = Field(None, max_length=100)


class IncidentCreate(IncidentBase):
    """Schema for creating an incident."""
    # Optional relationship IDs that can be added during creation
    actor_ids: Optional[List[str]] = []
    person_ids: Optional[List[str]] = []
    target_ids: Optional[List[str]] = []
    legal_framework_ids: Optional[List[str]] = []
    pattern_ids: Optional[List[str]] = []


class IncidentUpdate(BaseSchema):
    """Schema for updating an incident."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    date_occurred: Optional[date] = None
    date_range_end: Optional[date] = None
    summary: Optional[str] = Field(None, min_length=1)
    detailed_description: Optional[str] = None
    category_id: Optional[str] = None
    subcategory: Optional[str] = Field(None, max_length=200)
    severity: Optional[SeverityEnum] = None
    verification_status: Optional[VerificationStatusEnum] = None
    geographic_scope: Optional[GeographicScopeEnum] = None
    location_state: Optional[str] = Field(None, max_length=100)
    location_city: Optional[str] = Field(None, max_length=100)


class IncidentResponse(IncidentBase, TimestampSchema):
    """Schema for basic incident responses (list view)."""
    id: str
    created_by: str
    source_count: int = 0


class ActorInIncident(BaseSchema):
    """Actor with their role in the incident."""
    actor: ActorResponse
    role: ActorRoleEnum


class PersonInIncident(BaseSchema):
    """Person with their role in the incident."""
    person: PersonResponse
    role: PersonRoleEnum


class LegalFrameworkInIncident(BaseSchema):
    """Legal framework with violation type."""
    legal_framework: LegalFrameworkResponse
    violation_type: ViolationTypeEnum


class IncidentDetailResponse(IncidentResponse):
    """Schema for detailed incident responses (detail view)."""
    sources: List[SourceResponse] = []
    actors: List[ActorInIncident] = []
    persons: List[PersonInIncident] = []
    targets: List[TargetResponse] = []
    legal_frameworks: List[LegalFrameworkInIncident] = []
    patterns: List[PatternResponse] = []


class IncidentListResponse(BaseSchema):
    """Schema for paginated incident list."""
    total: int
    skip: int
    limit: int
    items: List[IncidentResponse]


class AddActorToIncident(BaseSchema):
    """Schema for adding an actor to an incident."""
    actor_id: str
    role: ActorRoleEnum = ActorRoleEnum.PERPETRATOR


class AddPersonToIncident(BaseSchema):
    """Schema for adding a person to an incident."""
    person_id: str
    role: PersonRoleEnum = PersonRoleEnum.ORDERED


class AddLegalFrameworkToIncident(BaseSchema):
    """Schema for adding a legal framework to an incident."""
    legal_framework_id: str
    violation_type: ViolationTypeEnum = ViolationTypeEnum.ALLEGED


class AddTargetToIncident(BaseSchema):
    """Schema for adding a target to an incident."""
    target_id: str


class AddPatternToIncident(BaseSchema):
    """Schema for adding a pattern to an incident."""
    pattern_id: str


class IncidentFilters(BaseSchema):
    """Query parameters for filtering incidents."""
    category_id: Optional[str] = None
    actor_id: Optional[str] = None
    person_id: Optional[str] = None
    target_id: Optional[str] = None
    pattern_id: Optional[str] = None
    legal_framework_id: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    verification_status: Optional[VerificationStatusEnum] = None
    geographic_scope: Optional[GeographicScopeEnum] = None
    location_state: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100
