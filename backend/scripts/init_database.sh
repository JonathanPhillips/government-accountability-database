#!/bin/bash
# Database Initialization Script
# This script initializes the database schema and creates initial data

set -e

echo "Initializing GADB database..."

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Run Alembic migrations
echo "Running database migrations..."
cd "$(dirname "$0")/.."
alembic upgrade head

echo "Database migrations completed successfully"

# Create initial admin user if it doesn't exist
echo "Creating initial admin user..."
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.auth import get_password_hash
from sqlalchemy import select

db = SessionLocal()
try:
    # Check if admin user exists
    existing_admin = db.execute(
        select(User).where(User.email == 'admin@gadb.local')
    ).scalar_one_or_none()

    if not existing_admin:
        admin_user = User(
            email='admin@gadb.local',
            username='admin',
            hashed_password=get_password_hash('changeme123'),
            full_name='System Administrator',
            is_active=True,
            role='admin'
        )
        db.add(admin_user)
        db.commit()
        print('✓ Admin user created')
        print('  Email: admin@gadb.local')
        print('  Password: changeme123')
        print('  ⚠️  IMPORTANT: Change the default password immediately!')
    else:
        print('✓ Admin user already exists')
finally:
    db.close()
"

echo ""
echo "Database initialization completed successfully!"
echo ""
echo "Next steps:"
echo "1. Change the default admin password"
echo "2. Create additional user accounts as needed"
echo "3. Configure application settings"
