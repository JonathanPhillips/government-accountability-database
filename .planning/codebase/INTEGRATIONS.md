# External Integrations

**Analysis Date:** 2026-01-14

## APIs & External Services

**Web Archival:**
- Internet Archive Wayback Machine - URL archival and preservation
  - API: `https://archive.org/wayback/available`
  - Configuration: `backend/app/config.py` (`wayback_machine_api`)
  - Usage: `backend/app/models/source.py` (`archived_url` field)
  - Auth: None (public API)

**AI/ML Services:**
- Anthropic Claude API - AI content extraction (planned feature)
  - SDK: `anthropic==0.8.1`
  - Auth: `ANTHROPIC_API_KEY` in environment variables
  - Status: Dependency installed but not yet integrated in code

**RSS Feed Sources (Data Ingestion):**
Configured in `backend/app/tasks/ingestion_tasks.py`:
- ProPublica - `https://www.propublica.org/feeds/propublica/main`
- The Intercept - `https://theintercept.com/feed/`
- BBC News - `http://feeds.bbci.co.uk/news/rss.xml`
- Electronic Frontier Foundation (EFF) - `https://www.eff.org/rss/updates.xml`
- NPR - `https://feeds.npr.org/1001/rss.xml`

**External Content Processing:**
- YouTube - Video transcript extraction
  - Library: `youtube-transcript-api==0.6.2`
  - Service: `backend/app/services/youtube_ingester.py`
- Web Scraping - General HTML content extraction
  - Libraries: `beautifulsoup4`, `requests`
  - Service: `backend/app/services/rss_ingester.py`

## Data Storage

**Databases:**
- PostgreSQL 14 - Production database
  - Connection: `backend/app/database.py` via SQLAlchemy
  - Environment: `DATABASE_URL` (default: `postgresql://gadb:password@localhost:5432/gadb`)
  - Client: SQLAlchemy 2.0.25 with psycopg2-binary and asyncpg
  - Migrations: Alembic in `backend/alembic/versions/`
- SQLite - Development/testing database
  - Connection: `backend/app/database.py`
  - Environment: `DATABASE_URL=sqlite:///./gadb.db`

**Caching & Queue:**
- Redis 7 - Cache and Celery message broker
  - Connection: `backend/app/celery_app.py`, `backend/app/config.py`
  - Environment: `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
  - Default: `redis://localhost:6379/0`

**File Storage:**
- Local File System - PDF and document storage
  - Upload directory: `/app/uploads`, `/app/data/pdfs`
  - Configuration: `MAX_UPLOAD_SIZE` in environment variables
  - No cloud storage integration (S3, GCS, Azure Blob) - local only

## Authentication & Identity

**Auth Provider:**
- JWT Authentication - Custom implementation
  - Libraries: `python-jose[cryptography]`, `passlib[bcrypt]`
  - Implementation: `backend/app/utils/auth.py`, `backend/app/api/auth.py`
  - Token storage: Frontend stores JWT in localStorage/sessionStorage
  - Session management: JWT with configurable expiration

**Role-Based Access Control:**
- Hierarchical roles: VIEWER < REVIEWER < EDITOR < ADMIN
  - Implementation: `backend/app/models/base.py` (`UserRoleEnum`)
  - Enforcement: `backend/app/utils/deps.py` (`require_role` dependency)
  - No external OAuth providers (Google, GitHub, etc.)

## Monitoring & Observability

**Error Tracking (Optional):**
- Sentry - Error and exception tracking
  - Environment: `SENTRY_DSN`, `SENTRY_ENVIRONMENT`
  - Status: Configured but not required (optional monitoring)

**Application Monitoring (Optional):**
- New Relic - Application performance monitoring
  - Environment: `NEW_RELIC_LICENSE_KEY`
  - Status: Configured but not required (optional monitoring)

**Logs:**
- Docker Logs - stdout/stderr via Docker/Docker Compose
  - No centralized log aggregation (CloudWatch, Datadog, etc.)
  - Health check logs: `/health` (liveness), `/health/ready` (readiness)

## CI/CD & Deployment

**Hosting:**
- Docker Compose - Development and production orchestration
  - Files: `docker-compose.yml` (dev), `docker-compose.prod.yml` (prod)
  - Services: PostgreSQL, Redis, Backend API, Frontend SPA, Nginx
  - Deployment: Manual or scripted deployment

**CI Pipeline:**
- GitHub Actions - Automated testing and deployment
  - Workflows: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`, `.github/workflows/e2e-tests.yml`
  - Coverage: Codecov integration for test coverage reporting
  - Security: Trivy vulnerability scanning for Docker images
  - Secrets: Stored in GitHub repository secrets

**Container Registry:**
- Docker Hub - Container image storage (implied, not explicitly configured)

## Environment Configuration

**Development:**
- Required env vars: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `CORS_ORIGINS`
- Secrets location: `.env` files (gitignored)
- Mock services: Stripe test mode not applicable, local PostgreSQL/SQLite, local Redis
- Default admin: `admin@gadb.local` / `changeme123` (MUST CHANGE)

**Staging:**
- Not explicitly configured (can use production setup with different env vars)

**Production:**
- Secrets management: Environment variables in `.env.production` files
- Database: PostgreSQL with automated backups (`backend/scripts/backup_database.sh`)
- Failover/redundancy: Not configured (single-instance deployment)

## Webhooks & Callbacks

**Incoming:**
- None currently implemented

**Outgoing:**
- None currently implemented

## Document Processing

**PDF Processing:**
- Tesseract OCR - Optical character recognition
  - System dependency: Installed in `backend/Dockerfile`
  - Python wrapper: `pytesseract==0.3.10`
  - Service: `backend/app/services/pdf_processor.py`
- PDF Libraries - Text extraction
  - `PyPDF2==3.0.1`, `pdfplumber==0.10.4`
  - Service: `backend/app/services/pdf_processor.py`

## Background Jobs

**Celery Beat:**
- Scheduled task execution
  - Schedule: Hourly RSS feed ingestion (`backend/app/celery_app.py`)
  - Tasks: `backend/app/tasks/ingestion_tasks.py`
  - Redis backend for task results

## Health Checks & Monitoring

**Health Check Endpoints:**
- `/health` - Liveness probe (API server running)
- `/health/ready` - Readiness probe (API + database connectivity)
- Location: `backend/app/main.py`

**Docker Health Checks:**
- Backend: `curl -f http://localhost:8000/health`
- Frontend: `wget --spider http://localhost:80/`
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`

## Not Detected/Not Used

- **Payment processors** - None (Stripe, PayPal, Square, etc.)
- **Analytics services** - None (Google Analytics, Mixpanel, Amplitude, etc.)
- **CDN services** - None (CloudFlare, Fastly, Akamai, etc.)
- **Cloud storage** - None (AWS S3, Google Cloud Storage, Azure Blob)
- **OAuth providers** - None (Google, GitHub, Microsoft, Auth0)
- **Real-time communication** - None (WebSockets, Socket.io, Pusher)
- **Search engines** - None (Elasticsearch, Algolia, Typesense) - SQL-based search only
- **GraphQL** - None (REST API only)
- **Email services** - SMTP configured but disabled by default (`SMTP_ENABLED=False`)

---

*Integration audit: 2026-01-14*
*Update when adding/removing external services*
