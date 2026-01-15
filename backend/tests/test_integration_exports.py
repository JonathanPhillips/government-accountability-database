"""Integration tests for export API endpoints."""
import pytest
import csv
import json
from io import StringIO
from datetime import date, timedelta
from app.models.incident import Incident
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum


@pytest.mark.integration
def test_export_incidents_csv_endpoint(client, sample_category, db_session):
    """Test GET /api/export/incidents/csv endpoint."""
    # Create test incidents
    # Use db_session from fixture
    # db_session from fixture

    for i in range(3):
        incident = Incident(
            id=f"export_csv_{i}",
            title=f"Export CSV Incident {i}",
            date_occurred=date.today() - timedelta(days=i),
            summary=f"Summary {i}",
            category_id=sample_category.id,
            severity=SeverityEnum.HIGH,
            verification_status=VerificationStatusEnum.DOCUMENTED,
            geographic_scope=GeographicScopeEnum.FEDERAL,
            location_state="CA"
        )
        db_session.add(incident)
    db_session.commit()

    # Test CSV export
    response = client.get("/api/export/incidents/csv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    assert "incidents_export.csv" in response.headers["content-disposition"]

    # Verify CSV content
    csv_content = response.text
    assert "id,title,date_occurred" in csv_content
    assert "Export CSV Incident" in csv_content

    # Parse CSV
    reader = csv.DictReader(StringIO(csv_content))
    rows = list(reader)
    assert len(rows) >= 3


@pytest.mark.integration
def test_export_incidents_json_endpoint(client, sample_category, db_session):
    """Test GET /api/export/incidents/json endpoint."""
    # Create test incidents
    # Use db_session from fixture
    # db_session from fixture

    incident = Incident(
        id="export_json_1",
        title="Export JSON Incident",
        date_occurred=date.today(),
        summary="JSON export test",
        category_id=sample_category.id,
        severity=SeverityEnum.CRITICAL,
        verification_status=VerificationStatusEnum.ADJUDICATED,
        geographic_scope=GeographicScopeEnum.STATE
    )
    db_session.add(incident)
    db_session.commit()

    # Test JSON export
    response = client.get("/api/export/incidents/json")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment" in response.headers["content-disposition"]
    assert "incidents_export.json" in response.headers["content-disposition"]

    # Verify JSON structure
    data = response.json()
    assert "metadata" in data
    assert "incidents" in data

    # Verify metadata
    metadata = data["metadata"]
    assert "total_exported" in metadata
    assert "total_matching" in metadata
    assert "filters_applied" in metadata
    assert metadata["total_exported"] >= 1

    # Verify incidents
    assert len(data["incidents"]) >= 1
    assert data["incidents"][0]["title"] == "Export JSON Incident"


@pytest.mark.integration
def test_export_with_filters(client, sample_category, db_session):
    """Test export endpoints with various filters."""
    # Create diverse incidents
    # Use db_session from fixture
    # db_session from fixture

    incidents = [
        Incident(
            id="filter_exp_1",
            title="Critical CA Incident",
            date_occurred=date(2024, 11, 15),
            summary="Critical incident",
            category_id=sample_category.id,
            severity=SeverityEnum.CRITICAL,
            verification_status=VerificationStatusEnum.DOCUMENTED,
            geographic_scope=GeographicScopeEnum.STATE,
            location_state="CA"
        ),
        Incident(
            id="filter_exp_2",
            title="High NY Incident",
            date_occurred=date(2024, 12, 10),
            summary="High incident",
            category_id=sample_category.id,
            severity=SeverityEnum.HIGH,
            verification_status=VerificationStatusEnum.PENDING_REVIEW,
            geographic_scope=GeographicScopeEnum.FEDERAL,
            location_state="NY"
        ),
    ]

    for incident in incidents:
        db_session.add(incident)
    db_session.commit()

    # Test severity filter
    response = client.get("/api/export/incidents/json?severity=SeverityEnum.CRITICAL")
    assert response.status_code == 200
    data = response.json()

    # Should only export critical incidents
    critical_incidents = [inc for inc in data["incidents"] if inc["severity"] == "CRITICAL"]
    assert len(critical_incidents) >= 1

    # Test state filter
    response = client.get("/api/export/incidents/csv?location_state=CA")
    assert response.status_code == 200
    csv_content = response.text
    assert "Critical CA Incident" in csv_content


@pytest.mark.integration
def test_export_analytics_csv_endpoint(client, sample_category, db_session):
    """Test GET /api/export/analytics/csv endpoint."""
    # Create test incidents
    # Use db_session from fixture
    # db_session from fixture

    for severity in [SeverityEnum.CRITICAL, SeverityEnum.HIGH, SeverityEnum.MEDIUM]:
        incident = Incident(
            id=f"analytics_exp_{severity.value}",
            title=f"{severity.value} Incident",
            date_occurred=date.today(),
            summary=f"Summary for {severity.value}",
            category_id=sample_category.id,
            severity=severity,
            verification_status=VerificationStatusEnum.DOCUMENTED,
            geographic_scope=GeographicScopeEnum.FEDERAL
        )
        db_session.add(incident)
    db_session.commit()

    # Test analytics CSV export
    response = client.get("/api/export/analytics/csv")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "analytics_export.csv" in response.headers["content-disposition"]

    # Verify CSV content
    csv_content = response.text
    assert "Severity Analysis" in csv_content
    assert "Verification Status Analysis" in csv_content
    assert "Geographic Scope Analysis" in csv_content
    assert "CRITICAL" in csv_content or "HIGH" in csv_content or "MEDIUM" in csv_content


@pytest.mark.integration
def test_export_limit_parameter(client, sample_category, db_session):
    """Test export limit parameter."""
    # Create 15 incidents
    # Use db_session from fixture
    # db_session from fixture

    for i in range(15):
        incident = Incident(
            id=f"limit_exp_{i}",
            title=f"Limit Test {i}",
            date_occurred=date.today(),
            summary=f"Summary {i}",
            category_id=sample_category.id,
            severity=SeverityEnum.MEDIUM,
            verification_status=VerificationStatusEnum.UNVERIFIED,
            geographic_scope=GeographicScopeEnum.LOCAL
        )
        db_session.add(incident)
    db_session.commit()

    # Request only 5 incidents
    response = client.get("/api/export/incidents/json?limit=5")

    assert response.status_code == 200
    data = response.json()

    # Should export only 5 incidents
    assert len(data["incidents"]) == 5
    assert data["metadata"]["total_exported"] == 5
    assert data["metadata"]["total_matching"] >= 15


@pytest.mark.integration
def test_export_date_range_filter(client, sample_category, db_session):
    """Test export with date range filter."""
    # Use db_session from fixture
    # db_session from fixture

    # Create incidents in different date ranges
    old_incident = Incident(
        id="date_old",
        title="Old Incident",
        date_occurred=date(2024, 1, 15),
        summary="Old",
        category_id=sample_category.id,
        severity=SeverityEnum.LOW,
        verification_status=VerificationStatusEnum.UNVERIFIED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db_session.add(old_incident)

    recent_incident = Incident(
        id="date_recent",
        title="Recent Incident",
        date_occurred=date(2024, 12, 15),
        summary="Recent",
        category_id=sample_category.id,
        severity=SeverityEnum.HIGH,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.STATE
    )
    db_session.add(recent_incident)
    db_session.commit()

    # Export with date range filter
    response = client.get("/api/export/incidents/json?date_from=2024-12-01&date_to=2024-12-31")

    assert response.status_code == 200
    data = response.json()

    # Should only export December 2024 incidents
    december_incidents = [inc for inc in data["incidents"]
                         if "2024-12" in inc["date_occurred"]]
    assert len(december_incidents) >= 1

    # Verify filters are recorded in metadata
    assert data["metadata"]["filters_applied"]["date_from"] == "2024-12-01"
    assert data["metadata"]["filters_applied"]["date_to"] == "2024-12-31"


@pytest.mark.integration
def test_export_empty_database(client):
    """Test export endpoints with empty database."""
    # CSV export
    response = client.get("/api/export/incidents/csv")
    assert response.status_code == 200
    csv_content = response.text
    assert "id,title,date_occurred" in csv_content  # Header should be present

    # JSON export
    response = client.get("/api/export/incidents/json")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total_exported"] == 0
    assert len(data["incidents"]) == 0

    # Analytics CSV export
    response = client.get("/api/export/analytics/csv")
    assert response.status_code == 200
    csv_content = response.text
    assert "Severity Analysis" in csv_content


@pytest.mark.integration
def test_export_max_limit_enforcement(client, sample_category):
    """Test that export limit is enforced at 10,000 records."""
    # We can't create 10,000 records in test, but we can verify the parameter validation

    # Request more than max limit (10,000)
    response = client.get("/api/export/incidents/json?limit=15000")

    # Should either reject or cap at 10,000
    # FastAPI Query validation with le=10000 should return 422
    assert response.status_code == 422


@pytest.mark.integration
def test_export_public_access(client):
    """Test that export endpoints don't require authentication."""
    # Export endpoints should be publicly accessible
    response = client.get("/api/export/incidents/csv")
    assert response.status_code == 200

    response = client.get("/api/export/incidents/json")
    assert response.status_code == 200

    response = client.get("/api/export/analytics/csv")
    assert response.status_code == 200
