"""Tests for SQLAlchemy models."""
import pytest
from datetime import date
from app.models import (
    Incident, Actor, Person, Target, LegalFramework,
    Source, Pattern, Category, IngestionQueue,
    IncidentActor, IncidentPerson, IncidentTarget
)
from app.models.base import (
    SeverityEnum, VerificationStatusEnum, GeographicScopeEnum,
    ActorTypeEnum, ActorRoleEnum, SourceTypeEnum, ReliabilityEnum
)


def test_incident_creation(db_session, sample_category):
    """Test creating an incident."""
    incident = Incident(
        title="Test Incident",
        date_occurred=date(2025, 1, 1),
        summary="Test summary",
        category_id=sample_category.id,
        severity=SeverityEnum.HIGH,
        verification_status=VerificationStatusEnum.DOCUMENTED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db_session.add(incident)
    db_session.commit()

    assert incident.id is not None
    assert incident.title == "Test Incident"
    assert incident.severity == SeverityEnum.HIGH
    assert incident.created_at is not None
    assert incident.updated_at is not None


def test_actor_hierarchy(db_session):
    """Test parent-child actor relationships."""
    # Create parent actor (DHS)
    parent = Actor(
        name="Department of Homeland Security",
        actor_type=ActorTypeEnum.AGENCY,
        active=True
    )
    db_session.add(parent)
    db_session.commit()

    # Create child actor (ICE)
    child = Actor(
        name="Immigration and Customs Enforcement",
        actor_type=ActorTypeEnum.AGENCY,
        parent_actor_id=parent.id,
        active=True
    )
    db_session.add(child)
    db_session.commit()

    # Verify hierarchy
    db_session.refresh(parent)
    assert len(parent.sub_actors) == 1
    assert parent.sub_actors[0].name == "Immigration and Customs Enforcement"
    assert child.parent_actor.name == "Department of Homeland Security"


def test_source_incident_relationship(db_session, sample_incident):
    """Test source-incident relationship."""
    source = Source(
        incident_id=sample_incident.id,
        source_type=SourceTypeEnum.COURT_FILING,
        title="Test Court Filing",
        url="https://example.com/filing",
        reliability=ReliabilityEnum.PRIMARY
    )
    db_session.add(source)
    db_session.commit()

    # Verify relationship
    db_session.refresh(sample_incident)
    assert len(sample_incident.sources) == 1
    assert sample_incident.sources[0].title == "Test Court Filing"
    assert source.incident.title == sample_incident.title


def test_all_enums_valid(db_session):
    """Test that all enum values are valid."""
    # This test ensures enums are properly defined
    assert SeverityEnum.LOW == "low"
    assert SeverityEnum.MEDIUM == "medium"
    assert SeverityEnum.HIGH == "high"
    assert SeverityEnum.CRITICAL == "critical"

    assert VerificationStatusEnum.UNVERIFIED == "unverified"
    assert VerificationStatusEnum.DOCUMENTED == "documented"
    assert VerificationStatusEnum.ADJUDICATED == "adjudicated"


def test_junction_table_constraints(db_session, sample_incident, sample_actor):
    """Test unique constraints on junction tables."""
    # Create first incident-actor link
    link1 = IncidentActor(
        incident_id=sample_incident.id,
        actor_id=sample_actor.id,
        role=ActorRoleEnum.PERPETRATOR
    )
    db_session.add(link1)
    db_session.commit()

    # Try to create duplicate - should fail due to unique constraint
    link2 = IncidentActor(
        incident_id=sample_incident.id,
        actor_id=sample_actor.id,
        role=ActorRoleEnum.COMPLICIT
    )
    db_session.add(link2)

    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_category_unique_name(db_session):
    """Test that category names must be unique."""
    cat1 = Category(name="Court Order Defiance", description="Test")
    db_session.add(cat1)
    db_session.commit()

    cat2 = Category(name="Court Order Defiance", description="Different")
    db_session.add(cat2)

    with pytest.raises(Exception):  # Should fail on unique constraint
        db_session.commit()


def test_incident_date_range(db_session, sample_category):
    """Test incidents can have date ranges for ongoing events."""
    incident = Incident(
        title="Ongoing Test",
        date_occurred=date(2025, 1, 1),
        date_range_end=date(2025, 6, 1),
        summary="Test",
        category_id=sample_category.id,
        severity=SeverityEnum.LOW,
        verification_status=VerificationStatusEnum.UNVERIFIED,
        geographic_scope=GeographicScopeEnum.LOCAL
    )
    db_session.add(incident)
    db_session.commit()

    assert incident.date_occurred == date(2025, 1, 1)
    assert incident.date_range_end == date(2025, 6, 1)


def test_source_cascade_delete(db_session, sample_incident):
    """Test that deleting an incident cascades to delete sources."""
    source = Source(
        incident_id=sample_incident.id,
        source_type=SourceTypeEnum.NEWS_PRIMARY,
        title="Test Source",
        reliability=ReliabilityEnum.SECONDARY
    )
    db_session.add(source)
    db_session.commit()
    source_id = source.id

    # Delete incident
    db_session.delete(sample_incident)
    db_session.commit()

    # Verify source is also deleted
    deleted_source = db_session.query(Source).filter_by(id=source_id).first()
    assert deleted_source is None
