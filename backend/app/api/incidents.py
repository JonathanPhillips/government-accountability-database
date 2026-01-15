"""Incident API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.services.incident_service import IncidentService
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum, UserRoleEnum
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate, IncidentUpdate, IncidentResponse,
    IncidentDetailResponse, IncidentListResponse, IncidentFilters,
    AddActorToIncident, AddTargetToIncident, AddPatternToIncident,
    AddLegalFrameworkToIncident
)
from app.schemas.source import SourceCreate, SourceResponse
from app.utils.deps import get_current_active_user, get_optional_user, require_role

router = APIRouter()


@router.post("/", response_model=IncidentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident: IncidentCreate,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Create a new incident. Requires EDITOR role or higher."""
    db_incident = IncidentService.create(db, incident)
    # Reload with relationships
    return IncidentService.get_by_id(db, db_incident.id, load_relationships=True)


@router.get("/", response_model=IncidentListResponse)
def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    severity: Optional[SeverityEnum] = None,
    verification_status: Optional[VerificationStatusEnum] = None,
    geographic_scope: Optional[GeographicScopeEnum] = None,
    location_state: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List incidents with filtering and pagination."""
    filters = IncidentFilters(
        skip=skip,
        limit=limit,
        category_id=category_id,
        actor_id=actor_id,
        severity=severity,
        verification_status=verification_status,
        geographic_scope=geographic_scope,
        location_state=location_state,
        date_from=date_from,
        date_to=date_to,
        search=search
    )

    incidents, total = IncidentService.get_list(db, filters)

    # Add source count to each incident
    incident_responses = []
    for incident in incidents:
        source_count = IncidentService.get_source_count(db, incident.id)
        incident_dict = {
            **incident.__dict__,
            "source_count": source_count
        }
        incident_responses.append(incident_dict)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": incident_responses
    }


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get a specific incident with all relationships."""
    incident = IncidentService.get_by_id(db, incident_id, load_relationships=True)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )

    # Add source count
    source_count = IncidentService.get_source_count(db, incident_id)

    return {
        **incident.__dict__,
        "source_count": source_count,
        "sources": incident.sources,
        "actors": [{"actor": ia.actor, "role": ia.role} for ia in incident.actors],
        "persons": [{"person": ip.person, "role": ip.role} for ip in incident.persons],
        "targets": [it.target for it in incident.targets],
        "legal_frameworks": [{"legal_framework": ilf.legal_framework, "violation_type": ilf.violation_type} for ilf in incident.legal_frameworks],
        "patterns": [ip.pattern for ip in incident.patterns]
    }


@router.put("/{incident_id}", response_model=IncidentDetailResponse)
def update_incident(
    incident_id: str,
    incident_update: IncidentUpdate,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Update an incident. Requires EDITOR role or higher."""
    incident = IncidentService.update(db, incident_id, incident_update)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )
    return IncidentService.get_by_id(db, incident_id, load_relationships=True)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: str,
    current_user: User = Depends(require_role(UserRoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete an incident. Requires ADMIN role."""
    success = IncidentService.delete(db, incident_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )
    return None


# Relationship endpoints
@router.post("/{incident_id}/actors", status_code=status.HTTP_201_CREATED)
def add_actor_to_incident(
    incident_id: str,
    actor_data: AddActorToIncident,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Add an actor to an incident. Requires EDITOR role or higher."""
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )

    IncidentService.add_actor(db, incident_id, actor_data.actor_id, actor_data.role)
    return {"message": "Actor added to incident"}


@router.post("/{incident_id}/targets", status_code=status.HTTP_201_CREATED)
def add_target_to_incident(
    incident_id: str,
    target_data: AddTargetToIncident,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Add a target to an incident. Requires EDITOR role or higher."""
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )

    IncidentService.add_target(db, incident_id, target_data.target_id)
    return {"message": "Target added to incident"}


@router.post("/{incident_id}/patterns", status_code=status.HTTP_201_CREATED)
def add_pattern_to_incident(
    incident_id: str,
    pattern_data: AddPatternToIncident,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Add a pattern to an incident. Requires EDITOR role or higher."""
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )

    IncidentService.add_pattern(db, incident_id, pattern_data.pattern_id)
    return {"message": "Pattern added to incident"}


@router.post("/{incident_id}/legal-frameworks", status_code=status.HTTP_201_CREATED)
def add_legal_framework_to_incident(
    incident_id: str,
    lf_data: AddLegalFrameworkToIncident,
    current_user: User = Depends(require_role(UserRoleEnum.EDITOR)),
    db: Session = Depends(get_db)
):
    """Add a legal framework to an incident. Requires EDITOR role or higher."""
    incident = IncidentService.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found"
        )

    IncidentService.add_legal_framework(
        db, incident_id, lf_data.legal_framework_id, lf_data.violation_type
    )
    return {"message": "Legal framework added to incident"}
