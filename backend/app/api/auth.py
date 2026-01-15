"""Authentication API endpoints."""
from datetime import timedelta
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.base import UserRoleEnum
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    PasswordChange
)
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_access_token
)
from app.utils.deps import get_current_active_user, require_role
from app.utils.rate_limit import limiter, AUTH_RATE_LIMIT
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_RATE_LIMIT)
def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """
    Register a new user.

    Rate limited to 5 requests per minute to prevent abuse.

    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique)
    - **password**: Password (minimum 8 characters)
    - **role**: User role (default: viewer)
    """
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        organization=user_data.organization,
        role=user_data.role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
@limiter.limit(AUTH_RATE_LIMIT)
def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Login with email and password to receive access and refresh tokens.

    Rate limited to 5 requests per minute to prevent brute force attacks.

    - **email**: Registered email address
    - **password**: User password
    """
    # Get user
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
@limiter.limit(AUTH_RATE_LIMIT)
def refresh_token(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get a new access token using a refresh token.

    Rate limited to 5 requests per minute to prevent token abuse.

    - **refresh_token**: Valid refresh token
    """
    # Decode refresh token
    payload = decode_access_token(refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current authenticated user information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Update current user profile.

    - **email**: New email (optional)
    - **username**: New username (optional)
    - **full_name**: Full name (optional)
    - **organization**: Organization (optional)
    """
    # Check email uniqueness if changing
    if user_update.email and user_update.email != current_user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    # Check username uniqueness if changing
    if user_update.username and user_update.username != current_user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    # Update other fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.organization is not None:
        current_user.organization = user_update.organization

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.

    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()


# Admin endpoints
@router.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRoleEnum.ADMIN)),
    db: Session = Depends(get_db)
) -> list[User]:
    """
    List all users (admin only).

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role(UserRoleEnum.ADMIN)),
    db: Session = Depends(get_db)
) -> User:
    """
    Update any user (admin only).

    - **user_id**: User ID to update
    - **email**: New email (optional)
    - **username**: New username (optional)
    - **full_name**: Full name (optional)
    - **organization**: Organization (optional)
    - **role**: User role (optional)
    - **is_active**: Active status (optional)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if user_update.email:
        user.email = user_update.email
    if user_update.username:
        user.username = user_update.username
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.organization is not None:
        user.organization = user_update.organization
    if user_update.role:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).

    - **user_id**: User ID to delete
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    db.delete(user)
    db.commit()
