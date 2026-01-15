# Codebase Structure

**Analysis Date:** 2026-01-14

## Directory Layout

```
govt_accountability/
├── backend/              # Python FastAPI backend
├── frontend/             # React TypeScript frontend
├── kubernetes/           # K8s/K3s deployment manifests
├── .github/              # GitHub Actions CI/CD workflows
├── docker-compose.yml    # Development environment
├── docker-compose.prod.yml  # Production environment
├── README.md             # Project documentation
├── DEPLOYMENT.md         # Deployment guide
├── CONTRIBUTING.md       # Development guidelines
├── SECURITY.md           # Security policy
├── CHANGELOG.md          # Version history
├── STATUS.md             # Project status
└── LICENSE               # MIT License
```

## Directory Purposes

**backend/**
- Purpose: Python FastAPI backend application
- Contains: API endpoints, business logic, data models, background tasks
- Entry point: `backend/app/main.py`
- Key subdirectories: `app/`, `alembic/`, `scripts/`, `tests/`
- Configuration: `requirements.txt`, `Dockerfile`, `pytest.ini`, `alembic.ini`

**frontend/**
- Purpose: React TypeScript frontend application
- Contains: UI components, pages, API client, routing
- Entry point: `frontend/src/main.tsx`
- Key subdirectories: `src/`, `e2e/`, `tests/`, `public/`
- Configuration: `package.json`, `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`

**kubernetes/**
- Purpose: Kubernetes deployment manifests for K3s/K8s
- Contains: Deployment, Service, ConfigMap, Ingress definitions
- Key files: Backend, frontend, database, Redis deployments

**.github/workflows/**
- Purpose: CI/CD automation with GitHub Actions
- Contains: Test, build, deploy, security scanning workflows
- Key files: `ci.yml`, `deploy.yml`, `e2e-tests.yml`

## Backend Directory Structure (`backend/`)

```
backend/
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration version scripts
│   └── env.py                    # Alembic configuration
├── app/                          # Main application package
│   ├── api/                      # API route handlers (controllers)
│   │   ├── __init__.py
│   │   ├── incidents.py          # Incident CRUD endpoints
│   │   ├── categories.py         # Category endpoints
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── analytics.py          # Analytics endpoints
│   │   ├── exports.py            # Data export endpoints
│   │   └── ingestion.py          # Content ingestion endpoints
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── incident.py           # Primary data model
│   │   ├── actor.py              # Government entity model
│   │   ├── person.py             # Individual person model
│   │   ├── source.py             # Evidence source model
│   │   ├── category.py           # Categorization model
│   │   ├── target.py             # Affected party model
│   │   ├── pattern.py            # Behavioral pattern model
│   │   ├── legal_framework.py    # Legal reference model
│   │   ├── user.py               # User account model
│   │   ├── ingestion_queue.py    # Content queue model
│   │   ├── junctions.py          # Many-to-many relationships
│   │   └── base.py               # Base classes, enums, mixins
│   ├── schemas/                  # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── incident.py           # Request/response schemas
│   │   ├── actor.py              # Actor schemas
│   │   ├── category.py           # Category schemas
│   │   ├── [mirrors models dir] # One schema file per model
│   │   └── base.py               # Base schema classes
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── incident_service.py   # Incident operations
│   │   ├── actor_service.py      # Actor operations
│   │   ├── category_service.py   # Category operations
│   │   ├── rss_ingester.py       # RSS feed processing
│   │   ├── youtube_ingester.py   # YouTube integration
│   │   └── pdf_processor.py      # PDF content extraction
│   ├── tasks/                    # Celery background tasks
│   │   ├── __init__.py
│   │   └── ingestion_tasks.py    # Async content ingestion
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── auth.py               # JWT token handling
│   │   └── deps.py               # FastAPI dependencies (auth, RBAC)
│   ├── __init__.py
│   ├── config.py                 # Application configuration
│   ├── database.py               # Database connection setup
│   ├── main.py                   # FastAPI application entry point
│   └── celery_app.py             # Celery configuration
├── scripts/                      # Utility scripts
│   ├── backup_database.sh        # Database backup
│   ├── restore_database.sh       # Database restore
│   ├── init_database.sh          # Database initialization
│   ├── create_admin.py           # Admin user creation
│   └── seed_data.py              # Sample data seeding
├── tests/                        # Test suite (61 tests, 44% coverage)
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_models.py            # Model unit tests
│   ├── test_api_incidents.py     # Incident API tests
│   ├── test_api_auth.py          # Auth API tests
│   ├── test_api_analytics.py     # Analytics API tests
│   ├── test_integration_auth.py  # Integration tests
│   └── [additional test files]
├── .env.example                  # Development environment template
├── .env.production.example       # Production environment template
├── Dockerfile                    # Multi-stage container build
├── requirements.txt              # Python dependencies (pinned)
├── pytest.ini                    # Test configuration
└── alembic.ini                   # Migration configuration
```

## Frontend Directory Structure (`frontend/`)

```
frontend/
├── src/                          # Source code
│   ├── components/               # Reusable UI components
│   │   ├── Layout.tsx            # Page layout wrapper
│   │   ├── Header.tsx            # Navigation header
│   │   └── Footer.tsx            # Page footer
│   ├── pages/                    # Route-level page components
│   │   ├── HomePage.tsx          # Landing page
│   │   ├── IncidentListPage.tsx  # Incident browser (439 lines)
│   │   ├── IncidentDetailPage.tsx # Incident detail view
│   │   ├── AnalyticsDashboard.tsx # Analytics visualization (288 lines)
│   │   ├── Login.tsx             # Authentication
│   │   ├── Register.tsx          # User registration
│   │   ├── AdminDashboard.tsx    # Admin interface
│   │   ├── UserManagement.tsx    # User administration
│   │   ├── IngestionQueue.tsx    # Ingestion management
│   │   ├── IngestionQueueDetail.tsx # Queue item details
│   │   └── AddIngestionSource.tsx # Add sources (333 lines)
│   ├── services/                 # API client layer
│   │   └── api.ts                # Axios client, API functions
│   ├── types/                    # TypeScript type definitions
│   │   └── index.ts              # Interface definitions
│   ├── utils/                    # Utility functions
│   │   ├── api.ts                # API utilities
│   │   ├── export.ts             # Data export utilities
│   │   └── __tests__/            # Unit tests for utils
│   │       └── export.test.ts
│   ├── App.tsx                   # Root component, routing
│   ├── main.tsx                  # React entry point
│   └── index.css                 # Global styles (Tailwind)
├── e2e/                          # Playwright E2E tests (32 tests)
│   ├── dashboard.spec.ts         # Dashboard tests
│   ├── analytics.spec.ts         # Analytics tests
│   ├── search-filter.spec.ts     # Search/filter tests
│   └── export.spec.ts            # Export functionality tests
├── tests/                        # Unit tests (33 tests)
│   ├── setup.ts                  # Test configuration
│   └── [additional test files]
├── public/                       # Static assets
│   ├── index.html                # HTML entry point
│   └── [static files]
├── .env.example                  # Frontend environment template
├── .env.production.example       # Production template
├── .env.development              # Development config
├── Dockerfile                    # Multi-stage container build
├── nginx.conf                    # Nginx configuration for production
├── package.json                  # npm dependencies
├── vite.config.ts                # Vite build configuration
├── vitest.config.ts              # Unit test configuration
├── playwright.config.ts          # E2E test configuration
├── tailwind.config.js            # Tailwind CSS configuration
├── postcss.config.js             # PostCSS configuration
├── eslint.config.js              # ESLint configuration
└── tsconfig.json                 # TypeScript configuration
    └── tsconfig.app.json         # App-specific TS config
    └── tsconfig.node.json        # Node-specific TS config
```

## Key File Locations

**Entry Points:**
- `backend/app/main.py` - FastAPI application initialization
- `backend/app/celery_app.py` - Celery worker configuration
- `frontend/src/main.tsx` - React application entry point
- `frontend/src/App.tsx` - React router configuration

**Configuration:**
- `backend/app/config.py` - Backend settings (Pydantic Settings)
- `backend/.env.example` - Backend environment variables
- `backend/alembic.ini` - Database migration config
- `backend/pytest.ini` - Backend test configuration
- `frontend/vite.config.ts` - Frontend build configuration
- `frontend/tsconfig.json` - TypeScript compiler settings
- `frontend/tailwind.config.js` - Tailwind CSS customization
- `frontend/vitest.config.ts` - Frontend test configuration
- `docker-compose.yml` - Development orchestration
- `docker-compose.prod.yml` - Production orchestration

**Core Logic:**
- `backend/app/models/*.py` - Database models (11 files)
- `backend/app/services/*.py` - Business logic (6 files)
- `backend/app/api/*.py` - API endpoints (6 files)
- `backend/app/schemas/*.py` - Request/response schemas (mirrors models)
- `frontend/src/pages/*.tsx` - Page components (12 files)
- `frontend/src/services/api.ts` - API client

**Testing:**
- `backend/tests/` - Backend test suite (61 tests, 44% coverage)
- `backend/tests/conftest.py` - Pytest fixtures
- `frontend/tests/` - Frontend unit tests (33 tests)
- `frontend/e2e/` - E2E test suite (32 test cases)

**Documentation:**
- `README.md` - Project overview and quickstart
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `CONTRIBUTING.md` - Development guidelines
- `SECURITY.md` - Security policy and reporting
- `CHANGELOG.md` - Version history
- `STATUS.md` - Current project status
- `LICENSE` - MIT License

**Infrastructure:**
- `backend/Dockerfile` - Backend container definition
- `frontend/Dockerfile` - Frontend container definition
- `backend/scripts/*.sh` - Database management scripts
- `kubernetes/*.yaml` - K8s deployment manifests
- `.github/workflows/*.yml` - CI/CD workflows (4 files)

## Naming Conventions

**Files:**
- Backend modules: snake_case (e.g., `incident_service.py`, `auth.py`)
- Frontend components: PascalCase (e.g., `IncidentListPage.tsx`, `Header.tsx`)
- Frontend utilities: camelCase (e.g., `api.ts`, `export.ts`)
- Tests: `test_*.py` (backend), `*.test.ts[x]` (frontend)
- Config files: kebab-case or standard names (e.g., `docker-compose.yml`, `tsconfig.json`)

**Directories:**
- snake_case for Python packages (e.g., `app/`, `services/`, `utils/`)
- camelCase for TypeScript/JavaScript (e.g., `src/`, `components/`, `pages/`)
- Plural for collections (e.g., `models/`, `schemas/`, `tests/`)

**Special Patterns:**
- `__init__.py` - Python package initialization (makes directory a package)
- `conftest.py` - Pytest fixture definition file
- `index.ts` - TypeScript barrel export (re-exports from directory)
- `*.test.ts[x]` - Frontend unit tests (co-located with source)
- `*.spec.ts` - E2E tests (in separate e2e/ directory)

## Where to Add New Code

**New Incident Feature:**
- Model: `backend/app/models/new_model.py`
- Schema: `backend/app/schemas/new_model.py`
- Service: `backend/app/services/new_service.py`
- API: `backend/app/api/new_endpoint.py`
- Tests: `backend/tests/test_api_new.py`
- Frontend: `frontend/src/pages/NewFeaturePage.tsx`

**New API Endpoint:**
- Endpoint: `backend/app/api/[resource].py` (or add to existing)
- Schema: `backend/app/schemas/[resource].py`
- Service: `backend/app/services/[resource]_service.py` (if complex logic)
- Tests: `backend/tests/test_api_[resource].py`

**New Frontend Page:**
- Component: `frontend/src/pages/NewPage.tsx`
- Route: Add to `frontend/src/App.tsx`
- API calls: Add to `frontend/src/services/api.ts`
- Types: Add to `frontend/src/types/index.ts`
- Tests: `frontend/src/pages/__tests__/NewPage.test.tsx`

**New Background Task:**
- Task definition: `backend/app/tasks/[domain]_tasks.py`
- Service logic: `backend/app/services/[processor].py`
- Schedule: Add to `backend/app/celery_app.py`
- Tests: `backend/tests/test_tasks_[domain].py`

**Utilities:**
- Backend: `backend/app/utils/[utility].py`
- Frontend: `frontend/src/utils/[utility].ts`
- Tests co-located with source

## Special Directories

**backend/alembic/versions/**
- Purpose: Database migration version scripts
- Source: Generated by `alembic revision --autogenerate`
- Committed: Yes (source control for schema evolution)
- Note: Do not manually edit unless necessary

**frontend/dist/**
- Purpose: Production build output
- Source: Generated by `npm run build` (Vite)
- Committed: No (in .gitignore)

**backend/__pycache__/, frontend/node_modules/**
- Purpose: Compiled Python bytecode, npm dependencies
- Source: Auto-generated
- Committed: No (in .gitignore)

**kubernetes/**
- Purpose: Kubernetes deployment manifests for production
- Source: Hand-written YAML
- Committed: Yes
- Used for: K3s/K8s deployments

**.github/workflows/**
- Purpose: CI/CD automation workflows
- Source: Hand-written GitHub Actions YAML
- Committed: Yes
- Runs on: GitHub Actions runners

---

*Structure analysis: 2026-01-14*
*Update when directory structure changes*
