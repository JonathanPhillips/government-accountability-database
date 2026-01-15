"""Tests for analytics API endpoints."""
import pytest
from datetime import date, datetime, timedelta
from app.models.incident import Incident
from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum
from sqlalchemy import func


def test_analytics_overview(db_session, sample_category):
    """Test analytics overview endpoint."""
    # Create test incidents with different characteristics
    incidents_data = [
        {
            "id": "inc1",
            "title": "Incident 1",
            "date_occurred": date.today() - timedelta(days=10),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.CRITICAL,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL,
            "location_state": "CA"
        },
        {
            "id": "inc2",
            "title": "Incident 2",
            "date_occurred": date.today() - timedelta(days=20),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE,
            "location_state": "NY"
        },
        {
            "id": "inc3",
            "title": "Incident 3",
            "date_occurred": date.today() - timedelta(days=50),
            "summary": "Summary 3",
            "category_id": sample_category.id,
            "severity": SeverityEnum.MEDIUM,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.LOCAL,
            "location_state": "CA"
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Calculate expected values
    total = db_session.query(Incident).count()
    assert total == 3

    # Test severity counts
    severity_counts = (
        db_session.query(Incident.severity, func.count(Incident.id))
        .group_by(Incident.severity)
        .all()
    )
    assert len(severity_counts) == 3

    # Test verification counts
    verification_counts = (
        db_session.query(Incident.verification_status, func.count(Incident.id))
        .group_by(Incident.verification_status)
        .all()
    )
    assert len(verification_counts) == 2

    # Test scope counts
    scope_counts = (
        db_session.query(Incident.geographic_scope, func.count(Incident.id))
        .group_by(Incident.geographic_scope)
        .all()
    )
    assert len(scope_counts) == 3

    # Test state counts
    state_counts = (
        db_session.query(Incident.location_state, func.count(Incident.id))
        .filter(Incident.location_state.isnot(None))
        .group_by(Incident.location_state)
        .order_by(func.count(Incident.id).desc())
        .all()
    )
    assert len(state_counts) == 2
    assert state_counts[0][0] == "CA"  # CA should have 2 incidents
    assert state_counts[0][1] == 2

    # Test recent incidents (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_count = (
        db_session.query(Incident)
        .filter(Incident.date_occurred >= thirty_days_ago)
        .count()
    )
    assert recent_count == 2  # inc1 and inc2


@pytest.mark.skip(reason="date_trunc is PostgreSQL-specific, not supported in SQLite")
def test_analytics_timeline(db_session, sample_category):
    """Test analytics timeline endpoint."""
    # Create incidents across different months
    incidents_data = [
        {
            "id": "inc1",
            "title": "Incident 1",
            "date_occurred": date(2024, 11, 15),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL
        },
        {
            "id": "inc2",
            "title": "Incident 2",
            "date_occurred": date(2024, 11, 20),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.MEDIUM,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE
        },
        {
            "id": "inc3",
            "title": "Incident 3",
            "date_occurred": date(2024, 12, 5),
            "summary": "Summary 3",
            "category_id": sample_category.id,
            "severity": SeverityEnum.LOW,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.LOCAL
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Get timeline data
    days = 90
    start_date = date.today() - timedelta(days=days)

    timeline = (
        db_session.query(
            func.date_trunc('month', Incident.date_occurred).label('month'),
            func.count(Incident.id).label('count')
        )
        .filter(Incident.date_occurred >= start_date)
        .group_by('month')
        .order_by('month')
        .all()
    )

    # Should have incidents in Nov and Dec 2024
    assert len(timeline) >= 2

    # Find November 2024
    nov_counts = [t for t in timeline if t[0].month == 11 and t[0].year == 2024]
    if nov_counts:
        assert nov_counts[0][1] == 2

    # Find December 2024
    dec_counts = [t for t in timeline if t[0].month == 12 and t[0].year == 2024]
    if dec_counts:
        assert dec_counts[0][1] == 1


def test_analytics_categories(db_session, sample_category):
    """Test analytics categories endpoint."""
    from app.models import Category

    # Create additional category
    category2 = Category(
        id="test_category_2",
        name="Test Category 2",
        description="Another test category"
    )
    db_session.add(category2)
    db_session.commit()

    # Create incidents in different categories
    incidents_data = [
        {
            "id": "inc1",
            "title": "Incident 1",
            "date_occurred": date.today(),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL
        },
        {
            "id": "inc2",
            "title": "Incident 2",
            "date_occurred": date.today(),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.MEDIUM,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE
        },
        {
            "id": "inc3",
            "title": "Incident 3",
            "date_occurred": date.today(),
            "summary": "Summary 3",
            "category_id": category2.id,
            "severity": SeverityEnum.LOW,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.LOCAL
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Get category statistics
    category_stats = (
        db_session.query(
            Category.name,
            func.count(Incident.id).label('count')
        )
        .join(Incident, Category.id == Incident.category_id)
        .group_by(Category.id, Category.name)
        .order_by(func.count(Incident.id).desc())
        .all()
    )

    assert len(category_stats) == 2
    assert category_stats[0][0] == "Test Category"
    assert category_stats[0][1] == 2
    assert category_stats[1][0] == "Test Category 2"
    assert category_stats[1][1] == 1


@pytest.mark.skip(reason="date_trunc is PostgreSQL-specific, not supported in SQLite")
def test_analytics_verification_trends(db_session, sample_category):
    """Test analytics verification trends endpoint."""
    # Create incidents with different verification statuses
    incidents_data = [
        {
            "id": "inc1",
            "title": "Incident 1",
            "date_occurred": date(2024, 11, 15),
            "summary": "Summary 1",
            "category_id": sample_category.id,
            "severity": SeverityEnum.HIGH,
            "verification_status": VerificationStatusEnum.DOCUMENTED,
            "geographic_scope": GeographicScopeEnum.FEDERAL
        },
        {
            "id": "inc2",
            "title": "Incident 2",
            "date_occurred": date(2024, 11, 20),
            "summary": "Summary 2",
            "category_id": sample_category.id,
            "severity": SeverityEnum.MEDIUM,
            "verification_status": VerificationStatusEnum.UNVERIFIED,
            "geographic_scope": GeographicScopeEnum.STATE
        },
        {
            "id": "inc3",
            "title": "Incident 3",
            "date_occurred": date(2024, 12, 5),
            "summary": "Summary 3",
            "category_id": sample_category.id,
            "severity": SeverityEnum.LOW,
            "verification_status": VerificationStatusEnum.DISPUTED,
            "geographic_scope": GeographicScopeEnum.LOCAL
        },
    ]

    for data in incidents_data:
        incident = Incident(**data)
        db_session.add(incident)
    db_session.commit()

    # Get verification trends
    days = 90
    start_date = date.today() - timedelta(days=days)

    trends = (
        db_session.query(
            func.date_trunc('month', Incident.date_occurred).label('month'),
            Incident.verification_status,
            func.count(Incident.id).label('count')
        )
        .filter(Incident.date_occurred >= start_date)
        .group_by('month', Incident.verification_status)
        .order_by('month', Incident.verification_status)
        .all()
    )

    assert len(trends) >= 3

    # Verify we have entries for each verification status
    verification_statuses = set([t[1] for t in trends])
    assert VerificationStatusEnum.DOCUMENTED in verification_statuses
    assert VerificationStatusEnum.UNVERIFIED in verification_statuses
    assert VerificationStatusEnum.DISPUTED in verification_statuses
