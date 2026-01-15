# GADB Scripts

Utility scripts for managing the GADB application.

## Create Admin User

To create the first admin user:

```bash
# From the backend directory
docker-compose exec backend python scripts/create_admin.py
```

Or run directly if you have the environment set up locally:

```bash
cd backend
python scripts/create_admin.py
```

The script will prompt you for:
- Email address
- Username
- Password (minimum 8 characters)
- Password confirmation
- Full name (optional)

The created user will have:
- Role: ADMIN
- Superuser: Yes
- Active: Yes

## Direct Database Access

Alternatively, you can promote an existing user to admin:

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U gadb gadb

# Promote user to admin
UPDATE users SET role='admin', is_superuser=true WHERE email='user@example.com';
```
