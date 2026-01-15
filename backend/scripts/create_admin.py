"""Script to create an admin user."""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.base import UserRoleEnum
from app.utils.auth import get_password_hash


def create_admin_user(
    email: str,
    username: str,
    password: str,
    full_name: str = None
):
    """Create an admin user."""
    db: Session = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email '{email}' already exists")
            return False

        existing_username = db.query(User).filter(User.username == username).first()
        if existing_username:
            print(f"❌ User with username '{username}' already exists")
            return False

        # Create admin user
        admin_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=UserRoleEnum.ADMIN,
            is_superuser=True,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Username: {username}")
        print(f"   Role: {admin_user.role}")
        print(f"   Superuser: {admin_user.is_superuser}")

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("=== GADB Admin User Creation ===\n")

    # Get user input
    email = input("Enter admin email: ").strip()
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password (min 8 characters): ").strip()
    confirm_password = input("Confirm password: ").strip()
    full_name = input("Enter full name (optional): ").strip() or None

    # Validate input
    if not email or not username or not password:
        print("❌ Email, username, and password are required")
        sys.exit(1)

    if password != confirm_password:
        print("❌ Passwords do not match")
        sys.exit(1)

    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        sys.exit(1)

    # Create admin user
    success = create_admin_user(email, username, password, full_name)

    if success:
        print("\n✅ You can now login at: http://localhost:5173/login")
    else:
        sys.exit(1)
