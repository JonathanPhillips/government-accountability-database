"""Tests for Incident API endpoints."""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Category, Actor, Target
from app.models.base import ActorTypeEnum

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_category():
    """Create a sample category for testing."""
    db = TestingSessionLocal()
    category = Category(
        id="test_category",
        name="Court Order Defiance",
        description="Test category"
    )
    db.add(category)
    db.commit()
    db.close()
    return category


@pytest.fixture
def sample_actor():
    """Create a sample actor for testing."""
    db = TestingSessionLocal()
    actor = Actor(
        id="test_actor",
        name="Test Agency",
        actor_type=ActorTypeEnum.AGENCY,
        active=True
    )
    db.add(actor)
    db.commit()
    db.close()
    return actor


@pytest.fixture
def sample_target():
    """Create a sample target for testing."""
    db = TestingSessionLocal()
    target = Target(
        id="test_target",
        name="Asylum Seekers",
        description="Test target"
    )
    db.add(target)
    db.commit()
    db.close()
    return target


def test_create_incident_minimal(client, sample_category):
    """Test creating an incident with minimal required fields."""
    response = client.post(
        "/api/incidents/",
        json={
            "title": "Test Incident",
            "date_occurred": "2025-01-15",
            "summary": "A test incident summary",
            "category_id": "test_category",
            "severity": "medium",
            "verification_status": "unverified",
            "geographic_scope": "federal"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Incident"
    assert data["summary"] == "A test incident summary"
    assert "id" in data


def test_create_incident_full(client, sample_category, sample_actor, sample_target):
    """Test creating an incident with all fields and relationships."""
    response = client.post(
        "/api/incidents/",
        json={
            "title": "Full Test Incident",
            "date_occurred": "2025-01-15",
            "date_range_end": "2025-01-20",
            "summary": "Complete incident",
            "detailed_description": "Detailed description here",
            "category_id": "test_category",
            "severity": "high",
            "verification_status": "documented",
            "geographic_scope": "state",
            "location_state": "California",
            "location_city": "Los Angeles",
            "actor_ids": ["test_actor"],
            "target_ids": ["test_target"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Full Test Incident"
    assert data["severity"] == "high"
    assert len(data["actors"]) == 1
    assert len(data["targets"]) == 1


def test_create_incident_validation_errors(client):
    """Test that validation errors are returned for invalid data."""
    # Missing required fields
    response = client.post(
        "/api/incidents/",
        json={
            "title": "Test"
        }
    )
    assert response.status_code == 422  # Validation error


def test_list_incidents(client, sample_category):
    """Test listing incidents with pagination."""
    # Create multiple incidents
    for i in range(5):
        client.post(
            "/api/incidents/",
            json={
                "title": f"Incident {i}",
                "date_occurred": "2025-01-15",
                "summary": f"Summary {i}",
                "category_id": "test_category"
            }
        )

    # List all
    response = client.get("/api/incidents/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_filter_by_category(client, sample_category):
    """Test filtering incidents by category."""
    # Create incident
    client.post(
        "/api/incidents/",
        json={
            "title": "Test Incident",
            "date_occurred": "2025-01-15",
            "summary": "Test",
            "category_id": "test_category"
        }
    )

    # Filter by category
    response = client.get(f"/api/incidents/?category_id=test_category")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


def test_filter_by_date_range(client, sample_category):
    """Test filtering incidents by date range."""
    # Create incidents with different dates
    client.post(
        "/api/incidents/",
        json={
            "title": "Early Incident",
            "date_occurred": "2025-01-01",
            "summary": "Test",
            "category_id": "test_category"
        }
    )
    client.post(
        "/api/incidents/",
        json={
            "title": "Late Incident",
            "date_occurred": "2025-12-31",
            "summary": "Test",
            "category_id": "test_category"
        }
    )

    # Filter to only get first half of year
    response = client.get("/api/incidents/?date_from=2025-01-01&date_to=2025-06-30")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Early Incident"


def test_full_text_search(client, sample_category):
    """Test full-text search across incidents."""
    # Create incidents with specific keywords
    client.post(
        "/api/incidents/",
        json={
            "title": "Deportation Case",
            "date_occurred": "2025-01-15",
            "summary": "Testing deportation procedures",
            "category_id": "test_category"
        }
    )
    client.post(
        "/api/incidents/",
        json={
            "title": "Court Filing",
            "date_occurred": "2025-01-15",
            "summary": "Court case details",
            "category_id": "test_category"
        }
    )

    # Search for "deportation"
    response = client.get("/api/incidents/?search=deportation")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Deportation" in data["items"][0]["title"]


def test_get_incident_detail(client, sample_category):
    """Test getting detailed incident with all relationships."""
    # Create incident
    create_response = client.post(
        "/api/incidents/",
        json={
            "title": "Detail Test",
            "date_occurred": "2025-01-15",
            "summary": "Test",
            "category_id": "test_category"
        }
    )
    incident_id = create_response.json()["id"]

    # Get detailed view
    response = client.get(f"/api/incidents/{incident_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Detail Test"
    assert "sources" in data
    assert "actors" in data
    assert "targets" in data


def test_update_incident(client, sample_category):
    """Test updating an incident."""
    # Create incident
    create_response = client.post(
        "/api/incidents/",
        json={
            "title": "Original Title",
            "date_occurred": "2025-01-15",
            "summary": "Original summary",
            "category_id": "test_category"
        }
    )
    incident_id = create_response.json()["id"]

    # Update incident
    response = client.put(
        f"/api/incidents/{incident_id}",
        json={
            "title": "Updated Title",
            "severity": "critical"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["severity"] == "critical"


def test_delete_incident(client, sample_category):
    """Test soft deleting an incident."""
    # Create incident
    create_response = client.post(
        "/api/incidents/",
        json={
            "title": "To Delete",
            "date_occurred": "2025-01-15",
            "summary": "Will be deleted",
            "category_id": "test_category"
        }
    )
    incident_id = create_response.json()["id"]

    # Delete incident
    response = client.delete(f"/api/incidents/{incident_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/incidents/{incident_id}")
    assert response.status_code == 404


def test_add_actor_to_incident(client, sample_category, sample_actor):
    """Test adding an actor to an incident."""
    # Create incident
    create_response = client.post(
        "/api/incidents/",
        json={
            "title": "Test",
            "date_occurred": "2025-01-15",
            "summary": "Test",
            "category_id": "test_category"
        }
    )
    incident_id = create_response.json()["id"]

    # Add actor
    response = client.post(
        f"/api/incidents/{incident_id}/actors",
        json={
            "actor_id": "test_actor",
            "role": "perpetrator"
        }
    )
    assert response.status_code == 201

    # Verify actor was added
    incident = client.get(f"/api/incidents/{incident_id}").json()
    assert len(incident["actors"]) == 1
    assert incident["actors"][0]["actor"]["id"] == "test_actor"


def test_add_target_to_incident(client, sample_category, sample_target):
    """Test adding a target to an incident."""
    # Create incident
    create_response = client.post(
        "/api/incidents/",
        json={
            "title": "Test",
            "date_occurred": "2025-01-15",
            "summary": "Test",
            "category_id": "test_category"
        }
    )
    incident_id = create_response.json()["id"]

    # Add target
    response = client.post(
        f"/api/incidents/{incident_id}/targets",
        json={"target_id": "test_target"}
    )
    assert response.status_code == 201

    # Verify target was added
    incident = client.get(f"/api/incidents/{incident_id}").json()
    assert len(incident["targets"]) == 1
