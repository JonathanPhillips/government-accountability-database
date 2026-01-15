"""Tests for Category API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Category

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


def test_create_category(client):
    """Test creating a category."""
    response = client.post(
        "/api/categories/",
        json={
            "name": "Test Category",
            "description": "A test category for integration testing"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "A test category for integration testing"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_category(client):
    """Test that creating duplicate category fails."""
    # Create first category
    client.post(
        "/api/categories/",
        json={
            "name": "Court Order Defiance",
            "description": "Test"
        }
    )

    # Try to create duplicate
    response = client.post(
        "/api/categories/",
        json={
            "name": "Court Order Defiance",
            "description": "Different description"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_categories(client):
    """Test listing categories with pagination."""
    # Create multiple categories
    for i in range(5):
        client.post(
            "/api/categories/",
            json={
                "name": f"Category {i}",
                "description": f"Description {i}"
            }
        )

    # List all
    response = client.get("/api/categories/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5

    # Test pagination
    response = client.get("/api/categories/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_get_category(client):
    """Test getting a specific category."""
    # Create category
    create_response = client.post(
        "/api/categories/",
        json={
            "name": "Test Category",
            "description": "Test description"
        }
    )
    category_id = create_response.json()["id"]

    # Get category
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Test Category"


def test_get_nonexistent_category(client):
    """Test getting a category that doesn't exist."""
    response = client.get("/api/categories/nonexistent-id")
    assert response.status_code == 404


def test_update_category(client):
    """Test updating a category."""
    # Create category
    create_response = client.post(
        "/api/categories/",
        json={
            "name": "Original Name",
            "description": "Original description"
        }
    )
    category_id = create_response.json()["id"]

    # Update category
    response = client.put(
        f"/api/categories/{category_id}",
        json={
            "name": "Updated Name",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"


def test_delete_category(client):
    """Test deleting a category."""
    # Create category
    create_response = client.post(
        "/api/categories/",
        json={
            "name": "To Delete",
            "description": "Will be deleted"
        }
    )
    category_id = create_response.json()["id"]

    # Delete category
    response = client.delete(f"/api/categories/{category_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 404
