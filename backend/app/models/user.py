"""User model for authentication and authorization."""
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from .base import generate_uuid, TimestampMixin, UserRoleEnum


class User(Base, TimestampMixin):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)

    # Authorization
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    force_password_change = Column(Boolean, default=False, nullable=False)

    # Profile
    organization = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', role='{self.role}')>"

    def has_permission(self, required_role: UserRoleEnum) -> bool:
        """Check if user has required permission level."""
        if self.is_superuser:
            return True

        # Role hierarchy: admin > editor > reviewer > viewer
        role_hierarchy = {
            UserRoleEnum.VIEWER: 1,
            UserRoleEnum.REVIEWER: 2,
            UserRoleEnum.EDITOR: 3,
            UserRoleEnum.ADMIN: 4,
        }

        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level
