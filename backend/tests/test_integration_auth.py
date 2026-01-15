"""Integration tests for authentication API endpoints."""
import pytest
from app.models.user import User
from app.models.base import UserRoleEnum
from app.utils.auth import get_password_hash


@pytest.mark.integration
def test_register_new_user(client):
    """Test POST /api/auth/register endpoint."""
    user_data = {
        "email": "newuser@test.com",
        "username": "newuser",
        "password": "securepass123",
        "full_name": "New User",
        "organization": "Test Org",
        "role": "viewer"
    }

    response = client.post("/api/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"
    assert data["full_name"] == "New User"
    assert data["role"] == "viewer"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.integration
def test_register_duplicate_email(client, admin_user):
    """Test registration with duplicate email."""
    user_data = {
        "email": "admin@test.com",  # Already exists
        "username": "different",
        "password": "password123"
    }

    response = client.post("/api/auth/register", json=user_data)

    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()


@pytest.mark.integration
def test_register_duplicate_username(client, admin_user):
    """Test registration with duplicate username."""
    user_data = {
        "email": "different@test.com",
        "username": "admintest",  # Already exists
        "password": "password123"
    }

    response = client.post("/api/auth/register", json=user_data)

    assert response.status_code == 400
    assert "username already taken" in response.json()["detail"].lower()


@pytest.mark.integration
def test_login_success(client, admin_user):
    """Test POST /api/auth/login with valid credentials."""
    credentials = {
        "email": "admin@test.com",
        "password": "admin123"
    }

    response = client.post("/api/auth/login", json=credentials)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


@pytest.mark.integration
def test_login_invalid_password(client, admin_user):
    """Test login with invalid password."""
    credentials = {
        "email": "admin@test.com",
        "password": "wrongpassword"
    }

    response = client.post("/api/auth/login", json=credentials)

    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


@pytest.mark.integration
def test_login_nonexistent_user(client):
    """Test login with nonexistent email."""
    credentials = {
        "email": "nonexistent@test.com",
        "password": "anypassword"
    }

    response = client.post("/api/auth/login", json=credentials)

    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


@pytest.mark.integration
def test_login_inactive_user(client, db_session):
    """Test login with inactive user."""
    # Create inactive user
    inactive_user = User(
        email="inactive@test.com",
        username="inactive",
        hashed_password=get_password_hash("password123"),
        role=UserRoleEnum.VIEWER,
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()

    credentials = {
        "email": "inactive@test.com",
        "password": "password123"
    }

    response = client.post("/api/auth/login", json=credentials)

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


@pytest.mark.integration
def test_get_current_user(client, auth_headers):
    """Test GET /api/auth/me endpoint."""
    response = client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "admin@test.com"
    assert data["username"] == "admintest"
    assert data["role"] == "admin"
    assert data["is_active"] is True


@pytest.mark.integration
def test_get_current_user_unauthorized(client):
    """Test GET /api/auth/me without authentication."""
    response = client.get("/api/auth/me")

    assert response.status_code == 401


@pytest.mark.integration
def test_get_current_user_invalid_token(client):
    """Test GET /api/auth/me with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401


@pytest.mark.integration
def test_update_current_user(client, auth_headers):
    """Test PUT /api/auth/me endpoint."""
    update_data = {
        "full_name": "Updated Name",
        "organization": "Updated Org"
    }

    response = client.put("/api/auth/me", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["full_name"] == "Updated Name"
    assert data["organization"] == "Updated Org"
    assert data["email"] == "admin@test.com"  # Unchanged


@pytest.mark.integration
def test_change_password(client, auth_headers, db_session):
    """Test POST /api/auth/change-password endpoint."""
    password_data = {
        "current_password": "admin123",
        "new_password": "newpassword456"
    }

    response = client.post("/api/auth/change-password", json=password_data, headers=auth_headers)

    assert response.status_code == 204

    # Verify new password works
    credentials = {
        "email": "admin@test.com",
        "password": "newpassword456"
    }
    login_response = client.post("/api/auth/login", json=credentials)
    assert login_response.status_code == 200


@pytest.mark.integration
def test_change_password_wrong_current(client, auth_headers):
    """Test change password with incorrect current password."""
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword456"
    }

    response = client.post("/api/auth/change-password", json=password_data, headers=auth_headers)

    assert response.status_code == 400
    assert "incorrect current password" in response.json()["detail"].lower()


@pytest.mark.integration
def test_list_users_as_admin(client, auth_headers, db_session):
    """Test GET /api/auth/users endpoint as admin."""
    # Create additional users
    user1 = User(
        email="user1@test.com",
        username="user1",
        hashed_password=get_password_hash("pass123"),
        role=UserRoleEnum.VIEWER
    )
    user2 = User(
        email="user2@test.com",
        username="user2",
        hashed_password=get_password_hash("pass123"),
        role=UserRoleEnum.EDITOR
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    response = client.get("/api/auth/users", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 3  # admin + user1 + user2


@pytest.mark.integration
def test_list_users_unauthorized(client):
    """Test GET /api/auth/users without authentication."""
    response = client.get("/api/auth/users")

    assert response.status_code == 401


@pytest.mark.integration
def test_list_users_as_non_admin(client, db_session):
    """Test GET /api/auth/users as non-admin user."""
    # Create viewer user
    viewer = User(
        email="viewer@test.com",
        username="viewer",
        hashed_password=get_password_hash("viewer123"),
        role=UserRoleEnum.VIEWER,
        is_active=True
    )
    db_session.add(viewer)
    db_session.commit()

    # Login as viewer
    credentials = {
        "email": "viewer@test.com",
        "password": "viewer123"
    }
    login_response = client.post("/api/auth/login", json=credentials)
    viewer_token = login_response.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Try to list users
    response = client.get("/api/auth/users", headers=viewer_headers)

    assert response.status_code == 403


@pytest.mark.integration
def test_update_user_as_admin(client, auth_headers, db_session):
    """Test PUT /api/auth/users/{user_id} as admin."""
    # Create user to update
    user = User(
        email="updateme@test.com",
        username="updateme",
        hashed_password=get_password_hash("pass123"),
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Update user
    update_data = {
        "role": "editor",
        "is_active": False
    }

    response = client.put(f"/api/auth/users/{user.id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["role"] == "editor"
    assert data["is_active"] is False


@pytest.mark.integration
def test_delete_user_as_admin(client, auth_headers, db_session):
    """Test DELETE /api/auth/users/{user_id} as admin."""
    # Create user to delete
    user = User(
        email="deleteme@test.com",
        username="deleteme",
        hashed_password=get_password_hash("pass123"),
        role=UserRoleEnum.VIEWER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Delete user
    response = client.delete(f"/api/auth/users/{user.id}", headers=auth_headers)

    assert response.status_code == 204

    # Verify user is deleted
    get_response = client.get(f"/api/auth/users/{user.id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.integration
def test_delete_self_forbidden(client, auth_headers, admin_user):
    """Test that admin cannot delete their own account."""
    response = client.delete(f"/api/auth/users/{admin_user.id}", headers=auth_headers)

    assert response.status_code == 400
    assert "cannot delete your own account" in response.json()["detail"].lower()


@pytest.mark.integration
def test_refresh_token(client, admin_token, db_session):
    """Test POST /api/auth/refresh endpoint."""
    # Get refresh token
    credentials = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    login_response = client.post("/api/auth/login", json=credentials)
    refresh_token = login_response.json()["refresh_token"]

    # Use refresh token to get new access token
    response = client.post(f"/api/auth/refresh?refresh_token={refresh_token}")

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert len(data["access_token"]) > 0


@pytest.mark.integration
def test_refresh_token_invalid(client):
    """Test refresh token with invalid token."""
    response = client.post("/api/auth/refresh?refresh_token=invalid_token")

    assert response.status_code == 401


@pytest.mark.integration
def test_user_roles_validation(client):
    """Test that user role validation works."""
    # Try to register with invalid role
    user_data = {
        "email": "test@test.com",
        "username": "test",
        "password": "password123",
        "role": "invalid_role"
    }

    response = client.post("/api/auth/register", json=user_data)

    # Should return validation error
    assert response.status_code == 422
