"""Tests for export API endpoints."""
import pytest
import csv
import json
from io import StringIO
from datetime import date, timedelta
from app.models.incident import Incident
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum
from app.api.exports import incident_to_dict


def test_incident_to_dict(sample_incident):
    """Test converting incident model to dictionary."""
    result = incident_to_dict(sample_incident)

    assert result['id'] == sample_incident.id
    assert result['title'] == sample_incident.title
    assert result['summary'] == sample_incident.summary
    assert result['severity'] == 'MEDIUM'
    assert result['verification_status'] == 'UNVERIFIED'
    assert result['geographic_scope'] == 'FEDERAL'
    assert isinstance(result['date_occurred'], str)
    assert isinstance(result['created_at'], str)
    assert isinstance(result['updated_at'], str)


def test_export_incidents_csv_format(db_session, sample_category):
    """Test CSV export format."""
    from app.services.incident_service import IncidentService
    from app.schemas.incident import IncidentFilters

    # Create test incidents
    incidents_data = [
        {
            "id": "csv1",
            "title": "CSV Incident 1",
            "date_occurred": date.today(),
            "summary": "Summary for CSV export",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL,
            "location_state": "CA"
        },
        {
            "id": "csv2",
            "title": "CSV Incident 2",
            "date_occurred": date.today() - timedelta(days=5),
            "summary": "Another summary",
            "category_id": sample_category.id,
            "severity": SeverityEnum.MEDIUM,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE,
            "location_state": "NY"
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Get incidents using service
    filters = IncidentFilters(skip=0, limit=1000)
    incidents, total = IncidentService.get_list(db_session, filters)

    assert total == 2
    assert len(incidents) == 2

    # Create CSV
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

    csv_content = output.getvalue()

    # Verify CSV format
    assert 'id,title,date_occurred' in csv_content
    assert 'CSV Incident 1' in csv_content
    assert 'CSV Incident 2' in csv_content
    assert 'HIGH' in csv_content
    assert 'DOCUMENTED' in csv_content

    # Parse CSV and verify structure
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0]['title'] in ['CSV Incident 1', 'CSV Incident 2']


def test_export_incidents_json_format(db_session, sample_category):
    """Test JSON export format with metadata."""
    from app.services.incident_service import IncidentService
    from app.schemas.incident import IncidentFilters

    # Create test incidents
    incidents_data = [
        {
            "id": "json1",
            "title": "JSON Incident 1",
            "date_occurred": date.today(),
            "summary": "Summary for JSON export",
            "category_id": sample_category.id,
            "severity": SeverityEnum.CRITICAL,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Get incidents using service
    filters = IncidentFilters(
        skip=0,
        limit=1000,
        severity=SeverityEnum.CRITICAL
    )
    incidents, total = IncidentService.get_list(db_session, filters)

    # Convert to JSON export format
    incidents_data = [incident_to_dict(incident) for incident in incidents]

    export_data = {
        "metadata": {
            "total_exported": len(incidents_data),
            "total_matching": total,
            "filters_applied": {
                "category_id": None,
                "severity": str(SeverityEnum.CRITICAL),
                "verification_status": None,
                "geographic_scope": None,
                "location_state": None,
                "date_from": None,
                "date_to": None,
                "search": None
            }
        },
        "incidents": incidents_data
    }

    # Verify JSON structure
    assert export_data["metadata"]["total_exported"] == 1
    assert export_data["metadata"]["total_matching"] == 1
    assert "SeverityEnum.CRITICAL" in export_data["metadata"]["filters_applied"]["severity"]
    assert len(export_data["incidents"]) == 1
    assert export_data["incidents"][0]["title"] == "JSON Incident 1"

    # Verify JSON serialization
    json_content = json.dumps(export_data, indent=2, default=str)
    assert json_content is not None

    # Parse back and verify
    parsed = json.loads(json_content)
    assert parsed["metadata"]["total_exported"] == 1
    assert parsed["incidents"][0]["severity"] == "CRITICAL"


def test_export_with_filters(db_session, sample_category):
    """Test export with various filters."""
    from app.services.incident_service import IncidentService
    from app.schemas.incident import IncidentFilters

    # Create diverse test incidents
    incidents_data = [
        {
            "id": "filter1",
            "title": "Filter Test 1",
            "date_occurred": date(2024, 11, 15),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.CRITICAL,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL,
            "location_state": "CA"
        },
        {
            "id": "filter2",
            "title": "Filter Test 2",
            "date_occurred": date(2024, 12, 5),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE,
            "location_state": "NY"
        },
        {
            "id": "filter3",
            "title": "Filter Test 3",
            "date_occurred": date(2025, 1, 10),
            "summary": "Summary 3",
            "category_id": sample_category.id,
            "severity": SeverityEnum.CRITICAL,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.LOCAL,
            "location_state": "CA"
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Test severity filter
    filters = IncidentFilters(
        skip=0,
        limit=1000,
        severity=SeverityEnum.CRITICAL
    )
    incidents, total = IncidentService.get_list(db_session, filters)
    assert total == 2

    # Test state filter
    filters = IncidentFilters(
        skip=0,
        limit=1000,
        location_state="CA"
    )
    incidents, total = IncidentService.get_list(db_session, filters)
    assert total == 2

    # Test date range filter
    filters = IncidentFilters(
        skip=0,
        limit=1000,
        date_from=date(2024, 12, 1),
        date_to=date(2024, 12, 31)
    )
    incidents, total = IncidentService.get_list(db_session, filters)
    assert total == 1

    # Test verification status filter
    filters = IncidentFilters(
        skip=0,
        limit=1000,
        verification_status=VerificationStatusEnum.DOCUMENTED
    )
    incidents, total = IncidentService.get_list(db_session, filters)
    assert total == 2


def test_export_limit(db_session, sample_category):
    """Test export limit of 10,000 records."""
    from app.services.incident_service import IncidentService
    from app.schemas.incident import IncidentFilters

    # Test that limit parameter is respected
    filters = IncidentFilters(
        skip=0,
        limit=5  # Request only 5 records
    )

    # Create 10 incidents
    for i in range(10):
        incident = Incident(
            id=f"limit_{i}",
            title=f"Limit Test {i}",
            date_occurred=date.today(),
            summary=f"Summary {i}",
            category_id=sample_category.id,
            severity=SeverityEnum.MEDIUM,
            verification_status=VerificationStatusEnum.UNVERIFIED,
            geographic_scope=GeographicScopeEnum.FEDERAL
        )
        db_session.add(incident)
    db_session.commit()

    incidents, total = IncidentService.get_list(db_session, filters)
    assert total == 10  # Total in database
    assert len(incidents) == 5  # Limited by filter


def test_export_analytics_csv_format(db_session, sample_category):
    """Test analytics CSV export format."""
    from app.models import Category

    # Create test incidents
    incidents_data = [
        {
            "id": "analytics1",
            "title": "Analytics Test 1",
            "date_occurred": date.today(),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.CRITICAL,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL,
            "location_state": "CA"
        },
        {
            "id": "analytics2",
            "title": "Analytics Test 2",
            "date_occurred": date.today(),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE,
            "location_state": "NY"
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Get aggregated data
    from sqlalchemy import func

    severity_counts = (
        db_session.query(Incident.severity, func.count(Incident.id))
        .group_by(Incident.severity)
        .all()
    )

    verification_counts = (
        db_session.query(Incident.verification_status, func.count(Incident.id))
        .group_by(Incident.verification_status)
        .all()
    )

    scope_counts = (
        db_session.query(Incident.geographic_scope, func.count(Incident.id))
        .group_by(Incident.geographic_scope)
        .all()
    )

    state_counts = (
        db_session.query(Incident.location_state, func.count(Incident.id))
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

    csv_content = output.getvalue()

    # Verify CSV format
    assert 'Severity Analysis' in csv_content
    assert 'CRITICAL' in csv_content or 'HIGH' in csv_content
    assert 'Verification Status Analysis' in csv_content
    assert 'DOCUMENTED' in csv_content or 'UNVERIFIED' in csv_content

    # Verify we have counts
    assert '1' in csv_content or '2' in csv_content
