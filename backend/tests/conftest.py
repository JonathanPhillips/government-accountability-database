"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import *


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sample_category(db_session):
    """Create a sample category for testing."""
    from app.models import Category

    category = Category(
        id="test_category",
        name="Test Category",
        description="A test category for unit tests"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
def sample_actor(db_session):
    """Create a sample actor for testing."""
    from app.models import Actor
    from app.models.base import ActorTypeEnum

    actor = Actor(
        id="test_actor",
        name="Test Agency",
        actor_type=ActorTypeEnum.AGENCY,
        description="A test agency",
        active=True
    )
    db_session.add(actor)
    db_session.commit()
    db_session.refresh(actor)
    return actor


@pytest.fixture(scope="function")
def sample_incident(db_session, sample_category):
    """Create a sample incident for testing."""
    from app.models import Incident
    from app.models.base import SeverityEnum, VerificationStatusEnum, GeographicScopeEnum
    from datetime import date

    incident = Incident(
        id="test_incident",
        title="Test Incident",
        date_occurred=date(2025, 1, 1),
        summary="A test incident summary",
        detailed_description="Detailed description of the test incident",
        category_id=sample_category.id,
        severity=SeverityEnum.MEDIUM,
        verification_status=VerificationStatusEnum.UNVERIFIED,
        geographic_scope=GeographicScopeEnum.FEDERAL
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    return incident


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create an admin user for testing."""
    from app.models.user import User
    from app.models.base import UserRoleEnum
    from app.utils.auth import get_password_hash

    user = User(
        email="admin@test.com",
        username="admintest",
        hashed_password=get_password_hash("admin123"),
        role=UserRoleEnum.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Get an admin authentication token."""
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(admin_token):
    """Get authentication headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}
