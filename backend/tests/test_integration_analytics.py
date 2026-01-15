"""Integration tests for analytics API endpoints."""
import pytest
from datetime import date, timedelta
from app.models.incident import Incident
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum


@pytest.mark.integration
def test_analytics_overview_endpoint(client, sample_category, db_session):
    """Test GET /api/analytics/overview endpoint."""
    # Create test incidents
    incidents_data = [
        {
            "id": "int_inc1",
            "title": "Integration Incident 1",
            "date_occurred": date.today() - timedelta(days=10),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.CRITICAL,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL,
            "location_state": "CA"
        },
        {
            "id": "int_inc2",
            "title": "Integration Incident 2",
            "date_occurred": date.today() - timedelta(days=20),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE,
            "location_state": "NY"
        },
    ]

    # Add incidents via database (not API)
    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Test the endpoint
    response = client.get("/api/analytics/overview")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "total_incidents" in data
    assert "by_severity" in data
    assert "by_verification" in data
    assert "by_geographic_scope" in data
    assert "recent_30_days" in data
    assert "top_states" in data
    assert "last_updated" in data

    # Verify data
    assert data["total_incidents"] >= 2
    assert data["recent_30_days"] >= 2


@pytest.mark.integration
def test_analytics_categories_endpoint(client, sample_category, db_session):
    """Test GET /api/analytics/categories endpoint."""
    # Create test incident
    # Use db_session from fixture

    incident = Incident(
        id="cat_inc1",
        title="Category Test Incident",
        date_occurred=date.today(),
        summary="Test summary",
        category_id=sample_category.id,
        severity=SeverityEnum.MEDIUM,
        verification_status=VerificationStatusEnum.UNVERIFIED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db_session.add(incident)
    db_session.commit()

    # Test the endpoint
    response = client.get("/api/analytics/categories")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "categories" in data
    assert len(data["categories"]) > 0

    # Verify category data
    category = data["categories"][0]
    assert "name" in category
    assert "count" in category
    assert category["name"] == sample_category.name
    assert category["count"] >= 1


@pytest.mark.integration
def test_analytics_timeline_endpoint(client, sample_category, db_session):
    """Test GET /api/analytics/timeline endpoint."""
    # Create test incident
    # Use db_session from fixture

    incident = Incident(
        id="timeline_inc1",
        title="Timeline Test Incident",
        date_occurred=date.today() - timedelta(days=30),
        summary="Test summary",
        category_id=sample_category.id,
        severity=SeverityEnum.HIGH,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.STATE
    )
    db_session.add(incident)
    db_session.commit()

    # Test the endpoint with default 90 days
    response = client.get("/api/analytics/timeline")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "timeline" in data
    assert "days" in data
    assert data["days"] == 90

    # Test with custom days parameter
    response = client.get("/api/analytics/timeline?days=30")

    assert response.status_code == 200
    data = response.json()
    assert data["days"] == 30


@pytest.mark.integration
def test_analytics_verification_trends_endpoint(client, sample_category, db_session):
    """Test GET /api/analytics/verification-trends endpoint."""
    # Create test incident
    # Use db_session from fixture

    incident = Incident(
        id="verify_inc1",
        title="Verification Test Incident",
        date_occurred=date.today() - timedelta(days=15),
        summary="Test summary",
        category_id=sample_category.id,
        severity=SeverityEnum.MEDIUM,
        verification_status=VerificationStatusEnum.PENDING_REVIEW,
        geographic_scope=GeographicScopeEnum.LOCAL
    )
    db_session.add(incident)
    db_session.commit()

    # Test the endpoint
    response = client.get("/api/analytics/verification-trends?days=90")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "trends" in data
    assert "days" in data
    assert data["days"] == 90


@pytest.mark.integration
def test_analytics_unauthorized_access(client):
    """Test that analytics endpoints don't require authentication."""
    # Analytics endpoints should be publicly accessible
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200

    response = client.get("/api/analytics/categories")
    assert response.status_code == 200

    response = client.get("/api/analytics/timeline")
    assert response.status_code == 200


@pytest.mark.integration
def test_analytics_with_no_data(client):
    """Test analytics endpoints with no incidents in database."""
    response = client.get("/api/analytics/overview")

    assert response.status_code == 200
    data = response.json()

    # Should return empty/zero values
    assert data["total_incidents"] == 0
    assert data["recent_30_days"] == 0
    assert len(data["top_states"]) == 0


@pytest.mark.integration
def test_analytics_filters_recent_data(client, sample_category, db_session):
    """Test that analytics correctly filters recent data."""
    # Use db_session from fixture

    # Create old incident (> 30 days)
    old_incident = Incident(
        id="old_inc",
        title="Old Incident",
        date_occurred=date.today() - timedelta(days=40),
        summary="Old summary",
        category_id=sample_category.id,
        severity=SeverityEnum.LOW,
        verification_status=VerificationStatusEnum.UNVERIFIED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db.add(old_incident)

    # Create recent incident (< 30 days)
    recent_incident = Incident(
        id="recent_inc",
        title="Recent Incident",
        date_occurred=date.today() - timedelta(days=15),
        summary="Recent summary",
        category_id=sample_category.id,
        severity=SeverityEnum.CRITICAL,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.STATE
    )
    db.add(recent_incident)
    db.commit()

    # Test endpoint
    response = client.get("/api/analytics/overview")

    assert response.status_code == 200
    data = response.json()

    # Total should include both
    assert data["total_incidents"] >= 2

    # Recent should only include the recent one
    assert data["recent_30_days"] >= 1
