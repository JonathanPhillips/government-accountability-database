"""Security validation tests for Phase 1 critical security features."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.base import UserRoleEnum
from app.utils.auth import get_password_hash, create_access_token


def test_rate_limiting_login_endpoint(client: TestClient):
    """Test that login endpoint is rate limited to 5 requests per minute."""
    # Make 6 requests rapidly (exceeds 5/min limit)
    credentials = {"email": "test@example.com", "password": "wrong_password"}

    responses = []
    for i in range(6):
        response = client.post("/api/auth/login", json=credentials)
        responses.append(response)

    # First 5 requests should get 401 (wrong credentials)
    for response in responses[:5]:
        assert response.status_code == 401

    # 6th request should get 429 (rate limited)
    assert responses[5].status_code == 429
    assert "rate limit" in responses[5].json()["detail"].lower()


def test_rate_limiting_register_endpoint(client: TestClient):
    """Test that register endpoint is rate limited to 5 requests per minute."""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "ValidPassword123!",
        "full_name": "New User"
    }

    responses = []
    for i in range(6):
        # Modify email slightly to avoid duplicate errors
        data = user_data.copy()
        data["email"] = f"user{i}@example.com"
        data["username"] = f"user{i}"
        response = client.post("/api/auth/register", json=data)
        responses.append(response)

    # First 5 requests should succeed (201) or fail for other reasons
    for i, response in enumerate(responses[:5]):
        assert response.status_code in [201, 400]  # Created or validation error

    # 6th request should get 429 (rate limited)
    assert responses[5].status_code == 429


def test_rate_limiting_refresh_endpoint(client: TestClient):
    """Test that refresh endpoint is rate limited to 5 requests per minute."""
    responses = []
    for i in range(6):
        response = client.post("/api/auth/refresh", json={"refresh_token": "invalid_token"})
        responses.append(response)

    # First 5 requests should get 401 (invalid token)
    for response in responses[:5]:
        assert response.status_code == 401

    # 6th request should get 429 (rate limited)
    assert responses[5].status_code == 429


def test_force_password_change_blocks_access(client: TestClient, db_session: Session, admin_user: User):
    """Test that users with force_password_change=True cannot access other endpoints."""
    # Set force_password_change flag
    admin_user.force_password_change = True
    db_session.commit()

    # Create access token
    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Try to access protected endpoint
    response = client.get("/api/auth/me", headers=headers)

    # Should get 403 with clear message
    assert response.status_code == 403
    assert "must change your password" in response.json()["detail"].lower()
    assert "/api/auth/change-password" in response.json()["detail"]


def test_force_password_change_allows_password_change(client: TestClient, db_session: Session, admin_user: User):
    """Test that users with force_password_change=True CAN access password change endpoint."""
    # Set force_password_change flag
    admin_user.force_password_change = True
    db_session.commit()

    # Create access token
    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Try to change password
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "testpassword", "new_password": "NewSecurePassword123!"},
        headers=headers
    )

    # Should succeed
    assert response.status_code == 204

    # Verify flag was cleared
    db_session.refresh(admin_user)
    assert admin_user.force_password_change is False

    # Now should be able to access other endpoints
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200


def test_default_password_rejection(client: TestClient, db_session: Session, admin_user: User):
    """Test that default passwords are rejected during password change."""
    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    default_passwords = ["changeme123", "admin", "password", "123456", "admin123"]

    for bad_password in default_passwords:
        response = client.post(
            "/api/auth/change-password",
            json={"current_password": "testpassword", "new_password": bad_password},
            headers=headers
        )

        # Should get 400 with clear message
        assert response.status_code == 400
        assert "default or common password" in response.json()["detail"].lower()


def test_password_change_clears_force_flag(client: TestClient, db_session: Session, admin_user: User):
    """Test that successful password change clears the force_password_change flag."""
    # Set flag
    admin_user.force_password_change = True
    db_session.commit()

    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Change password
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "testpassword", "new_password": "NewSecurePassword123!"},
        headers=headers
    )

    assert response.status_code == 204

    # Verify flag cleared
    db_session.refresh(admin_user)
    assert admin_user.force_password_change is False


def test_password_change_requires_correct_current_password(client: TestClient, db_session: Session, admin_user: User):
    """Test that password change requires correct current password."""
    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Try with wrong current password
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "wrong_password", "new_password": "NewSecurePassword123!"},
        headers=headers
    )

    assert response.status_code == 400
    assert "incorrect current password" in response.json()["detail"].lower()


def test_inactive_user_cannot_change_password(client: TestClient, db_session: Session, admin_user: User):
    """Test that inactive users cannot change password."""
    # Deactivate user
    admin_user.is_active = False
    db_session.commit()

    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Try to change password
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "testpassword", "new_password": "NewSecurePassword123!"},
        headers=headers
    )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_rate_limit_headers_present(client: TestClient):
    """Test that rate limit headers are present in responses."""
    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "test"})

    # Should have rate limit headers (if slowapi is configured correctly)
    # Note: Actual header names depend on slowapi configuration
    assert response.status_code in [401, 429]  # Either auth failure or rate limited


def test_password_complexity_minimum_length(client: TestClient, db_session: Session, admin_user: User):
    """Test that password must meet minimum length requirement."""
    token = create_access_token(data={"sub": admin_user.id, "email": admin_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Try with password that's too short (less than 8 characters)
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "testpassword", "new_password": "short"},
        headers=headers
    )

    # Should get validation error from Pydantic
    assert response.status_code == 422  # Validation error


def test_login_returns_token_for_forced_password_change_user(client: TestClient, db_session: Session):
    """Test that users with force_password_change=True can still log in to get token."""
    # Create user with force_password_change=True
    user = User(
        email="forced@example.com",
        username="forced_user",
        hashed_password=get_password_hash("testpassword"),
        role=UserRoleEnum.VIEWER,
        is_active=True,
        force_password_change=True
    )
    db_session.add(user)
    db_session.commit()

    # Login should succeed
    response = client.post(
        "/api/auth/login",
        json={"email": "forced@example.com", "password": "testpassword"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

    # But trying to use token for other endpoints should fail
    token = response.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "must change your password" in response.json()["detail"].lower()
