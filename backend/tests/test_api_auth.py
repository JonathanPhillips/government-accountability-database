"""Tests for authentication API endpoints."""
import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.base import UserRoleEnum
from app.utils.auth import verify_password, get_password_hash


def test_password_hashing():
    """Test password hashing functionality."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # Verify password is hashed
    assert hashed != password
    assert len(hashed) > 0

    # Verify password can be verified
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_user(db_session):
    """Test user creation."""
    hashed_password = get_password_hash("securepassword123")

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER,
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True
    assert user.role == UserRoleEnum.VIEWER
    assert user.hashed_password != "securepassword123"  # Should be hashed
    assert verify_password("securepassword123", user.hashed_password)


def test_create_admin_user(db_session):
    """Test admin user creation."""
    hashed_password = get_password_hash("adminpass123")

    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=hashed_password,
        role=UserRoleEnum.ADMIN,
        is_active=True
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email == "admin@example.com"
    assert user.username == "admin"
    assert user.role == UserRoleEnum.ADMIN
    assert user.is_active is True


def test_duplicate_email(db_session):
    """Test that duplicate emails are prevented."""
    hashed_password = get_password_hash("password123")

    # Create first user
    user1 = User(
        email="duplicate@example.com",
        username="user1",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user1)
    db_session.commit()

    # Attempt to create second user with same email
    user2 = User(
        email="duplicate@example.com",
        username="user2",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user2)

    # This should fail due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_duplicate_username(db_session):
    """Test that duplicate usernames are prevented."""
    hashed_password = get_password_hash("password123")

    # Create first user
    user1 = User(
        email="user1@example.com",
        username="duplicateuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user1)
    db_session.commit()

    # Attempt to create second user with same username
    user2 = User(
        email="user2@example.com",
        username="duplicateuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user2)

    # This should fail due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_authenticate_user_valid_credentials(db_session):
    """Test user authentication with valid credentials."""
    # Create a test user
    hashed_password = get_password_hash("correctpassword")
    user = User(
        email="auth@example.com",
        username="authuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Simulate authentication
    db_user = db_session.query(User).filter(User.email == "auth@example.com").first()
    assert db_user is not None
    assert verify_password("correctpassword", db_user.hashed_password)


def test_authenticate_user_invalid_password(db_session):
    """Test user authentication with invalid password."""
    # Create a test user
    hashed_password = get_password_hash("correctpassword")
    user = User(
        email="auth2@example.com",
        username="authuser2",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Simulate authentication with wrong password
    db_user = db_session.query(User).filter(User.email == "auth2@example.com").first()
    assert db_user is not None
    assert not verify_password("wrongpassword", db_user.hashed_password)


def test_authenticate_user_nonexistent_email(db_session):
    """Test user authentication with nonexistent email."""
    db_user = db_session.query(User).filter(User.email == "nonexistent@example.com").first()
    assert db_user is None


def test_authenticate_inactive_user(db_session):
    """Test that inactive users are marked as inactive."""
    # Create a user
    hashed_password = get_password_hash("password123")
    user = User(
        email="inactive@example.com",
        username="inactiveuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER,
        is_active=False  # Create as inactive
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Verify user is inactive
    assert user.is_active is False

    # In real app, login endpoint would check is_active
    db_user = db_session.query(User).filter(User.email == "inactive@example.com").first()
    assert db_user is not None
    assert db_user.is_active is False


def test_get_user_by_email(db_session):
    """Test retrieving user by email."""
    hashed_password = get_password_hash("password123")
    user = User(
        email="getuser@example.com",
        username="getuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user)
    db_session.commit()

    # Retrieve user by email
    retrieved_user = db_session.query(User).filter(User.email == "getuser@example.com").first()

    assert retrieved_user is not None
    assert retrieved_user.email == "getuser@example.com"
    assert retrieved_user.username == "getuser"


def test_get_user_by_username(db_session):
    """Test retrieving user by username."""
    hashed_password = get_password_hash("password123")
    user = User(
        email="getuser2@example.com",
        username="getuser2",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user)
    db_session.commit()

    # Retrieve user by username
    retrieved_user = db_session.query(User).filter(User.username == "getuser2").first()

    assert retrieved_user is not None
    assert retrieved_user.email == "getuser2@example.com"
    assert retrieved_user.username == "getuser2"


def test_user_timestamps(db_session):
    """Test that user timestamps are set correctly."""
    hashed_password = get_password_hash("password123")

    before_creation = datetime.utcnow()
    user = User(
        email="timestamp@example.com",
        username="timestampuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    after_creation = datetime.utcnow()

    assert user.created_at is not None
    assert user.updated_at is not None
    assert before_creation <= user.created_at <= after_creation
    assert before_creation <= user.updated_at <= after_creation


def test_admin_privileges(db_session):
    """Test admin user privileges."""
    hashed_password = get_password_hash("password123")

    # Create regular user
    regular_user = User(
        email="regular@example.com",
        username="regularuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.VIEWER
    )
    db_session.add(regular_user)

    # Create admin user
    admin_user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=hashed_password,
        role=UserRoleEnum.ADMIN
    )
    db_session.add(admin_user)

    db_session.commit()

    assert regular_user.role == UserRoleEnum.VIEWER
    assert admin_user.role == UserRoleEnum.ADMIN


def test_password_security(db_session):
    """Test password security requirements."""
    # Test that different passwords produce different hashes
    password1 = "password123"
    password2 = "password456"

    hash1 = get_password_hash(password1)
    hash2 = get_password_hash(password2)

    assert hash1 != hash2

    # Test that same password produces different hashes (due to salt)
    hash1a = get_password_hash(password1)
    hash1b = get_password_hash(password1)

    assert hash1a != hash1b  # Different due to random salt

    # But both should verify correctly
    assert verify_password(password1, hash1a)
    assert verify_password(password1, hash1b)


def test_user_roles(db_session):
    """Test different user roles."""
    hashed_password = get_password_hash("password123")

    # Test all user roles
    roles = [UserRoleEnum.ADMIN, UserRoleEnum.EDITOR, UserRoleEnum.VIEWER]

    for idx, role in enumerate(roles):
        user = User(
            email=f"user{idx}@example.com",
            username=f"user{idx}",
            hashed_password=hashed_password,
            role=role
        )
        db_session.add(user)

    db_session.commit()

    # Verify roles were set correctly
    admin = db_session.query(User).filter(User.email == "user0@example.com").first()
    editor = db_session.query(User).filter(User.email == "user1@example.com").first()
    viewer = db_session.query(User).filter(User.email == "user2@example.com").first()

    assert admin.role == UserRoleEnum.ADMIN
    assert editor.role == UserRoleEnum.EDITOR
    assert viewer.role == UserRoleEnum.VIEWER
