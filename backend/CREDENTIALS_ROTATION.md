# Credentials Rotation Guide

**Generated**: 2026-01-14
**Purpose**: Document secure credential generation for production deployment

## Why Rotate Credentials?

The current credentials in `.env.production` should be rotated for security best practices:
1. Credentials were generated during initial setup
2. May have been exposed through logs, backups, or other means
3. Production deployments should use unique, securely generated credentials

## Generate New Secure Credentials

Use Python's `secrets` module for cryptographically secure random generation:

```bash
cd backend
python3 -c "
import secrets

print('# Copy these to your .env.production file')
print('# Generated:', secrets.token_urlsafe(8))
print()
print('SECRET_KEY=' + secrets.token_hex(32))
print('JWT_SECRET_KEY=' + secrets.token_hex(32))
print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))
print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))
print('ADMIN_PASSWORD=' + secrets.token_urlsafe(16))
"
```

## Example Output (DO NOT USE THESE - GENERATE YOUR OWN)

```
SECRET_KEY=2ba10584004b93d99976517f105b713722b4b6ef6f97c93e1cb5e1a5a05acfb3
JWT_SECRET_KEY=01f557bf84be68cb3181bbcc61bec017db55d0d557e6aa8a7db7a1060ae30106
POSTGRES_PASSWORD=W_6LXZGPWsXBG46I4ARDfFx30CSXE1KYZPGd7IHFHY8
REDIS_PASSWORD=wN1Qv73iHpizsH00AsVniXfV8vtpioDPMp-WEPKnPys
ADMIN_PASSWORD=T-s9yVxNSuAjb5bdrF3Zmw
```

## Rotation Steps

### 1. Generate New Credentials

Run the Python script above to generate new credentials.

### 2. Update Backend .env.production

Update the following variables in `backend/.env.production`:

```bash
SECRET_KEY=<new_secret_key>
JWT_SECRET_KEY=<new_jwt_secret_key>
POSTGRES_PASSWORD=<new_postgres_password>
REDIS_PASSWORD=<new_redis_password>
ADMIN_PASSWORD=<new_admin_password>
```

### 3. Update docker-compose.prod.yml

Update the following environment variables in `docker-compose.prod.yml`:

**PostgreSQL service:**
```yaml
environment:
  POSTGRES_USER: gadb_user
  POSTGRES_PASSWORD: <new_postgres_password>  # Match backend/.env.production
  POSTGRES_DB: gadb
```

**Redis service:**
```yaml
command: redis-server --requirepass <new_redis_password>  # Match backend/.env.production
```

**Backend service:**
```yaml
environment:
  SECRET_KEY: <new_secret_key>
  JWT_SECRET_KEY: <new_jwt_secret_key>
  DATABASE_URL: postgresql://gadb_user:<new_postgres_password>@postgres:5432/gadb
  REDIS_URL: redis://:<new_redis_password>@redis:6379/0
```

### 4. Update DATABASE_URL and REDIS_URL

Ensure the DATABASE_URL and REDIS_URL in `backend/.env.production` match the new passwords:

```bash
DATABASE_URL=postgresql://gadb_user:<new_postgres_password>@postgres:5432/gadb
REDIS_URL=redis://:<new_redis_password>@redis:6379/0
CELERY_BROKER_URL=redis://:<new_redis_password>@redis:6379/0
CELERY_RESULT_BACKEND=redis://:<new_redis_password>@redis:6379/0
```

### 5. Restart Services

After updating all configuration files:

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 6. Verify Rotation

1. Check backend logs: `docker-compose -f docker-compose.prod.yml logs backend`
2. Test login with new admin password
3. Verify database connectivity
4. Verify Redis connectivity
5. Test API endpoints

## Security Checklist

- [ ] New credentials generated with `secrets` module
- [ ] All credentials are unique and different from previous values
- [ ] `backend/.env.production` updated
- [ ] `docker-compose.prod.yml` updated
- [ ] DATABASE_URL and REDIS_URL updated with new passwords
- [ ] Services restarted successfully
- [ ] Login tested with new admin password
- [ ] Database connections verified
- [ ] Redis connections verified
- [ ] API endpoints tested and working
- [ ] Old credentials securely destroyed (removed from backups, notes, etc.)

## Password Strength Guidelines

- **SECRET_KEY**: 64 hex characters (256 bits of entropy)
- **JWT_SECRET_KEY**: 64 hex characters (256 bits of entropy)
- **POSTGRES_PASSWORD**: 32+ URL-safe characters (192+ bits of entropy)
- **REDIS_PASSWORD**: 32+ URL-safe characters (192+ bits of entropy)
- **ADMIN_PASSWORD**: 16+ URL-safe characters (96+ bits of entropy, will be changed on first login)

## Important Notes

1. **Never commit credentials to git** - `.env.production` is in .gitignore
2. **Store credentials securely** - Use a password manager or secrets management service
3. **Rotate regularly** - Change credentials every 90 days or after suspected exposure
4. **Use different credentials per environment** - Dev, staging, and production should have different credentials
5. **Document rotation** - Keep a record of when credentials were last rotated (without storing the credentials themselves)

## Emergency Rotation

If credentials are compromised:

1. **Immediately** generate new credentials
2. Update all configuration files
3. Restart all services
4. Invalidate all existing JWT tokens (users will need to log in again)
5. Check logs for suspicious activity
6. Consider notifying users if data may have been accessed

---

**Last Updated**: 2026-01-14
**Next Rotation Due**: 2026-04-14 (90 days)
