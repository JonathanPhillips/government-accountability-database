# Technology Stack

**Analysis Date:** 2026-01-14

## Languages

**Primary:**
- Python 3.11 - Backend application code (`backend/Dockerfile`, `backend/requirements.txt`)
- TypeScript 5.9.3 - Frontend application code (`frontend/package.json`, `frontend/tsconfig.json`)

**Secondary:**
- JavaScript (ES2020) - Build configuration (`frontend/vite.config.ts`, `frontend/tailwind.config.js`)
- SQL - Database migrations (`backend/alembic/versions/*.py`)
- YAML - Configuration and CI/CD (`.github/workflows/*.yml`, `docker-compose.yml`)

## Runtime

**Environment:**
- Python 3.11 - Backend runtime (`backend/Dockerfile`: `FROM python:3.11-slim`)
- Node.js 20 - Frontend runtime (`frontend/Dockerfile`: `FROM node:20-alpine`)
- ASGI - Application server interface via Uvicorn

**Package Manager:**
- pip - Python packages (`backend/requirements.txt`)
- npm - Node.js packages (`frontend/package.json`)
- Note: No lockfiles committed to repository

## Frameworks

**Core:**
- FastAPI 0.109.0 - Async web framework for backend API (`backend/app/main.py`)
- React 19.2.0 - UI library for frontend (`frontend/src/App.tsx`)
- SQLAlchemy 2.0.25 - Python ORM (`backend/app/models/*.py`)
- React Router DOM 7.12.0 - Client-side routing (`frontend/src/App.tsx`)

**Testing:**
- pytest 7.4.4 - Backend testing framework (`backend/pytest.ini`)
- Vitest 4.0.17 - Frontend unit testing (`frontend/vitest.config.ts`)
- Playwright 1.57.0 - E2E testing (`frontend/playwright.config.ts`)
- pytest-cov 4.1.0 - Backend coverage reporting
- @testing-library/react 16.3.1 - React component testing

**Build/Dev:**
- Vite 7.2.4 - Frontend bundler and dev server (`frontend/vite.config.ts`)
- Uvicorn 0.27.0 - ASGI server for FastAPI (`backend/requirements.txt`)
- Alembic 1.13.1 - Database migration tool (`backend/alembic.ini`)
- TypeScript 5.9.3 - Type system (`frontend/tsconfig.json`)
- Tailwind CSS 4.1.18 - Utility-first CSS framework (`frontend/tailwind.config.js`)

## Key Dependencies

**Critical:**
- Pydantic 2.5.3 - Data validation and settings management (`backend/app/schemas/*.py`, `backend/app/config.py`)
- Celery 5.3.6 - Distributed task queue for background jobs (`backend/app/celery_app.py`)
- python-jose[cryptography] 3.3.0 - JWT token handling (`backend/app/utils/auth.py`)
- passlib[bcrypt] 1.7.4 + bcrypt 3.2.0 - Password hashing (`backend/app/utils/auth.py`)
- Axios 1.13.2 - Frontend HTTP client (`frontend/src/services/api.ts`)

**Infrastructure:**
- psycopg2-binary 2.9.9 + asyncpg 0.29.0 - PostgreSQL adapters (`backend/app/database.py`)
- Redis 5.0.1 - Message broker and cache backend (`backend/app/celery_app.py`)
- feedparser 6.0.11 - RSS feed parsing (`backend/app/services/rss_ingester.py`)
- beautifulsoup4 4.12.3 - HTML/XML parsing (`backend/app/services/rss_ingester.py`)
- PyPDF2 3.0.1 + pdfplumber 0.10.4 - PDF processing (`backend/app/services/pdf_processor.py`)
- anthropic 0.8.1 - Claude AI integration (`backend/requirements.txt`)

## Configuration

**Environment:**
- .env files for environment variables (`backend/.env.example`, `frontend/.env.example`)
- Pydantic Settings for type-safe configuration (`backend/app/config.py`)
- Key configs: DATABASE_URL, REDIS_URL, SECRET_KEY, CORS_ORIGINS, ANTHROPIC_API_KEY

**Build:**
- `frontend/vite.config.ts` - Dev server proxy to backend (http://localhost:8000)
- `frontend/tsconfig.json` - TypeScript strict mode enabled
- `frontend/tailwind.config.js` - Custom color palette and content paths
- `backend/alembic.ini` - Database migration configuration
- `backend/pytest.ini` - Test configuration with custom markers

## Platform Requirements

**Development:**
- Any platform with Docker and Docker Compose
- Python 3.11+ for local backend development
- Node.js 20+ for local frontend development
- PostgreSQL 14+ (or SQLite for testing)
- Redis 7+ for caching and task queue

**Production:**
- Docker containers on any Linux host
- PostgreSQL 14+ database (Alpine variant used in docker-compose)
- Redis 7+ (Alpine variant used in docker-compose)
- Nginx for reverse proxy and static file serving
- Supports Kubernetes/K3s deployment (manifests in `kubernetes/`)

---

*Stack analysis: 2026-01-14*
*Update after major dependency changes*
