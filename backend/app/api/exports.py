"""Export API endpoints."""
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import csv
import json
from io import StringIO

from app.database import get_db
from app.services.incident_service import IncidentService
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum
from app.schemas.incident import IncidentFilters

router = APIRouter(prefix="/export", tags=["Export"])


def incident_to_dict(incident) -> dict:
    """Convert incident model to dictionary for export."""
    return {
        'id': incident.id,
        'title': incident.title,
        'date_occurred': incident.date_occurred.isoformat() if incident.date_occurred else None,
        'date_range_end': incident.date_range_end.isoformat() if incident.date_range_end else None,
        'summary': incident.summary,
        'detailed_description': getattr(incident, 'detailed_description', None),
        'severity': str(incident.severity).replace('SeverityEnum.', ''),
        'verification_status': str(incident.verification_status).replace('VerificationStatusEnum.', ''),
        'geographic_scope': str(incident.geographic_scope).replace('GeographicScopeEnum.', ''),
        'location_state': incident.location_state,
        'location_city': incident.location_city,
        'location_details': getattr(incident, 'location_details', None),
        'created_at': incident.created_at.isoformat(),
        'updated_at': incident.updated_at.isoformat()
    }


@router.get("/incidents/csv")
def export_incidents_csv(
    category_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    severity: Optional[SeverityEnum] = None,
    verification_status: Optional[VerificationStatusEnum] = None,
    geographic_scope: Optional[GeographicScopeEnum] = None,
    location_state: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db)
):
    """
    Export incidents to CSV format with optional filters.

    Maximum 10,000 records per export.
    """
    filters = IncidentFilters(
        skip=0,
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

    # Create CSV in memory
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'id', 'title', 'date_occurred', 'date_range_end', 'summary',
        'detailed_description', 'severity', 'verification_status',
        'geographic_scope', 'location_state', 'location_city',
        'location_details', 'created_at', 'updated_at'
    ])

    writer.writeheader()
    for incident in incidents:
        writer.writerow(incident_to_dict(incident))

    # Return CSV response
    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=incidents_export.csv"
        }
    )


@router.get("/incidents/json")
def export_incidents_json(
    category_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    severity: Optional[SeverityEnum] = None,
    verification_status: Optional[VerificationStatusEnum] = None,
    geographic_scope: Optional[GeographicScopeEnum] = None,
    location_state: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db)
):
    """
    Export incidents to JSON format with optional filters.

    Maximum 10,000 records per export.
    """
    filters = IncidentFilters(
        skip=0,
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

    # Convert incidents to dictionaries
    incidents_data = [incident_to_dict(incident) for incident in incidents]

    # Create export metadata
    export_data = {
        "metadata": {
            "total_exported": len(incidents_data),
            "total_matching": total,
            "filters_applied": {
                "category_id": category_id,
                "severity": str(severity) if severity else None,
                "verification_status": str(verification_status) if verification_status else None,
                "geographic_scope": str(geographic_scope) if geographic_scope else None,
                "location_state": location_state,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "search": search
            }
        },
        "incidents": incidents_data
    }

    # Return JSON response
    json_content = json.dumps(export_data, indent=2, default=str)
    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=incidents_export.json"
        }
    )


@router.get("/analytics/csv")
def export_analytics_csv(db: Session = Depends(get_db)):
    """Export analytics summary to CSV format."""
    from app.models.incident import Incident
    from sqlalchemy import func

    # Get aggregated data
    severity_counts = (
        db.query(Incident.severity, func.count(Incident.id))
        .group_by(Incident.severity)
        .all()
    )

    verification_counts = (
        db.query(Incident.verification_status, func.count(Incident.id))
        .group_by(Incident.verification_status)
        .all()
    )

    scope_counts = (
        db.query(Incident.geographic_scope, func.count(Incident.id))
        .group_by(Incident.geographic_scope)
        .all()
    )

    state_counts = (
        db.query(Incident.location_state, func.count(Incident.id))
        .filter(Incident.location_state.isnot(None))
        .group_by(Incident.location_state)
        .order_by(func.count(Incident.id).desc())
        .all()
    )

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Severity section
    writer.writerow(['Severity Analysis'])
    writer.writerow(['Severity', 'Count'])
    for severity, count in severity_counts:
        writer.writerow([str(severity).replace('SeverityEnum.', ''), count])
    writer.writerow([])

    # Verification section
    writer.writerow(['Verification Status Analysis'])
    writer.writerow(['Status', 'Count'])
    for status, count in verification_counts:
        writer.writerow([str(status).replace('VerificationStatusEnum.', ''), count])
    writer.writerow([])

    # Geographic scope section
    writer.writerow(['Geographic Scope Analysis'])
    writer.writerow(['Scope', 'Count'])
    for scope, count in scope_counts:
        writer.writerow([str(scope).replace('GeographicScopeEnum.', ''), count])
    writer.writerow([])

    # State section
    writer.writerow(['State Analysis'])
    writer.writerow(['State', 'Count'])
    for state, count in state_counts:
        writer.writerow([state, count])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=analytics_export.csv"
        }
    )
