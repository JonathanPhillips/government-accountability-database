# Architecture

**Analysis Date:** 2026-01-14

## Pattern Overview

**Overall:** Decoupled Client-Server Architecture (Modern Full-Stack Monorepo)

**Key Characteristics:**
- Clear separation between frontend (React SPA) and backend (FastAPI REST API)
- Asynchronous background processing via Celery task queue
- Layered architecture with clear boundaries
- RESTful API communication with JWT authentication
- Docker containerized for development and production

## Layers

**Backend Layer 1: Presentation Layer (API Controllers)**
- Purpose: HTTP request handling, validation, response formatting
- Contains: FastAPI router endpoints, request/response handling
- Location: `backend/app/api/*.py`
- Key files: `incidents.py`, `auth.py`, `analytics.py`, `categories.py`, `exports.py`, `ingestion.py`
- Depends on: Service layer, schema layer, utilities (auth, dependencies)
- Used by: Frontend HTTP clients
- Pattern: FastAPI routers with dependency injection

**Backend Layer 2: Service Layer (Business Logic)**
- Purpose: Core business logic, complex operations, data transformation
- Contains: Business rules, multi-model operations, external service integration
- Location: `backend/app/services/*.py`
- Key files: `incident_service.py`, `actor_service.py`, `category_service.py`, `rss_ingester.py`, `pdf_processor.py`
- Depends on: Data access layer (models), external APIs
- Used by: API layer, Celery tasks
- Pattern: Static methods in service classes (stateless)

**Backend Layer 3: Data Access Layer (Repository Pattern via ORM)**
- Purpose: Database schema definitions, ORM relationships, data persistence
- Contains: SQLAlchemy models with relationships and constraints
- Location: `backend/app/models/*.py`
- Key files: `incident.py`, `actor.py`, `category.py`, `source.py`, `user.py`, `junctions.py`, `base.py`
- Depends on: Database connection, SQLAlchemy
- Used by: Service layer
- Pattern: SQLAlchemy declarative models with explicit relationships

**Backend Layer 4: Schema/Validation Layer (DTOs)**
- Purpose: Request validation, response serialization, API contracts
- Contains: Pydantic models with validation rules
- Location: `backend/app/schemas/*.py`
- Key files: Mirror models directory (e.g., `incident.py`, `actor.py`, `category.py`, `base.py`)
- Depends on: Pydantic, model enums
- Used by: API layer for request/response validation
- Pattern: Pydantic models with validators

**Backend Layer 5: Infrastructure Layer**
- Purpose: Database connections, configuration, authentication, utilities
- Contains: Cross-cutting concerns and infrastructure setup
- Location: `backend/app/database.py`, `backend/app/config.py`, `backend/app/utils/*.py`
- Key files: `database.py` (connection management), `config.py` (Pydantic settings), `utils/auth.py` (JWT), `utils/deps.py` (DI)
- Depends on: Environment variables, external libraries
- Used by: All layers
- Pattern: Dependency injection via FastAPI

**Backend Layer 6: Background Processing**
- Purpose: Asynchronous task execution, scheduled jobs
- Contains: Celery tasks for RSS ingestion, content processing
- Location: `backend/app/tasks/*.py`, `backend/app/celery_app.py`
- Key files: `ingestion_tasks.py` (RSS feed processing), `celery_app.py` (configuration)
- Depends on: Redis (broker), service layer, models
- Used by: Celery Beat (scheduler), manual triggers
- Pattern: Celery distributed task queue

**Frontend Layer 1: Presentation Layer**
- Purpose: UI components, user interaction, state management
- Contains: React components, pages, routing
- Location: `frontend/src/pages/*.tsx`, `frontend/src/components/*.tsx`
- Key files: `HomePage.tsx`, `IncidentListPage.tsx`, `AnalyticsDashboard.tsx`, `Layout.tsx`, `Header.tsx`
- Depends on: API client layer, type definitions
- Used by: React Router
- Pattern: Functional components with hooks

**Frontend Layer 2: API Client Layer**
- Purpose: HTTP communication with backend, request/response handling
- Contains: Axios client configuration and API resource functions
- Location: `frontend/src/services/api.ts`
- Functions: `incidentsApi.list()`, `incidentsApi.get()`, `categoriesApi.list()`, `authApi.login()`
- Depends on: Axios, type definitions
- Used by: Components and pages
- Pattern: Resource-based API client organization

**Frontend Layer 3: Type Definitions**
- Purpose: TypeScript interfaces matching backend schemas
- Contains: Type definitions for all API entities
- Location: `frontend/src/types/index.ts`
- Depends on: Nothing (pure TypeScript interfaces)
- Used by: All frontend layers
- Pattern: TypeScript interfaces

**Frontend Layer 4: Utilities**
- Purpose: Helper functions and shared logic
- Contains: Export utilities, formatting helpers
- Location: `frontend/src/utils/*.ts`
- Key files: `export.ts` (CSV/JSON export), `api.ts` (API helpers)
- Depends on: Type definitions
- Used by: Components and API client
- Pattern: Pure utility functions

## Data Flow

**HTTP Request Flow (Read Operation):**
1. User interacts with component → Component triggers API call
2. API client (`frontend/src/services/api.ts`) sends HTTP request
3. Backend entry point (`backend/app/main.py`) receives request
4. Router (`backend/app/api/incidents.py`) matches endpoint
5. Dependency injection runs (`backend/app/utils/deps.py`): Authentication + Authorization (RBAC)
6. Service layer (`backend/app/services/incident_service.py`) executes business logic
7. ORM models (`backend/app/models/incident.py`) query database (PostgreSQL/SQLite)
8. Pydantic schema (`backend/app/schemas/incident.py`) validates and serializes response
9. JSON response → Frontend → State update → Component re-render

**HTTP Write Flow (Create Incident):**
1. Form submission → API client sends POST request
2. Pydantic schema validates request body (`IncidentCreate`)
3. Authorization check (require_role: EDITOR or ADMIN)
4. Service layer creates incident with relationships
5. Database transaction: Insert incident + junction tables
6. Commit transaction, return `IncidentDetailResponse`
7. Frontend updates state and redirects to detail page

**Background Task Flow (RSS Ingestion):**
1. Celery Beat scheduler triggers hourly cron (`backend/app/celery_app.py`)
2. Celery worker executes task (`backend/app/tasks/ingestion_tasks.py` → `ingest_all_feeds()`)
3. RSSIngester service fetches and parses feeds (`backend/app/services/rss_ingester.py`)
4. Content extracted and metadata parsed (title, date, summary)
5. Insert into `ingestion_queue` table with status PENDING
6. Status updated: PENDING → IN_PROGRESS → COMPLETED/FAILED
7. Optional: Notification or webhook (not currently implemented)

**State Management:**
- Backend: Stateless request handling, all state in database
- Frontend: Component-local state with React hooks (no global state management like Redux)
- Background tasks: Redis stores task results and queue state

## Key Abstractions

**Service Pattern:**
- Purpose: Encapsulate business logic separate from API layer
- Examples: `IncidentService`, `ActorService`, `CategoryService` in `backend/app/services/*.py`
- Pattern: Static methods on service classes (no instantiation needed)
- Benefit: Testable business logic, reusable across API and background tasks

**Repository Pattern (via SQLAlchemy ORM):**
- Purpose: Database abstraction and relationship management
- Examples: `Incident.sources`, `Incident.actors`, `Category.parent` in `backend/app/models/*.py`
- Pattern: Declarative models with explicit relationships
- Benefit: Type-safe queries, automatic relationship loading

**DTO Pattern (Data Transfer Objects):**
- Purpose: API contracts with validation
- Examples: `IncidentCreate` (input), `IncidentResponse` (output), `IncidentListResponse` (paginated) in `backend/app/schemas/*.py`
- Pattern: Pydantic models with field validators
- Benefit: Automatic validation, API documentation, type safety

**Junction Table Pattern:**
- Purpose: Many-to-many relationships with metadata
- Examples: `IncidentActor` (with role), `IncidentLegalFramework` (with violation_type) in `backend/app/models/junctions.py`
- Pattern: Explicit junction tables as SQLAlchemy models
- Benefit: Additional relationship metadata beyond simple association

**Dependency Injection Pattern:**
- Purpose: Loose coupling, testable dependencies
- Examples: `Depends(get_db)` for database session, `Depends(get_current_active_user)` for auth
- Pattern: FastAPI's dependency injection system
- Location: `backend/app/utils/deps.py`
- Benefit: Easy mocking in tests, clear dependency graph

**Role-Based Access Control (RBAC):**
- Purpose: Hierarchical authorization
- Implementation: `require_role(UserRoleEnum.EDITOR)` decorator in `backend/app/utils/deps.py`
- Roles: VIEWER < REVIEWER < EDITOR < ADMIN (hierarchical)
- Pattern: FastAPI dependency that raises 403 if role insufficient

## Entry Points

**Backend API Entry:**
- Location: `backend/app/main.py`
- Object: `app = FastAPI(title="Government Accountability Database API", version="1.0.0")`
- Triggers: HTTP requests to any registered route
- Responsibilities: Application initialization, middleware setup (CORS, security), router registration, health checks
- Start command: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

**Celery Worker Entry:**
- Location: `backend/app/celery_app.py`
- Object: `celery_app = Celery("gadb")`
- Triggers: Celery Beat schedule or manual task invocation
- Responsibilities: Background task configuration, Redis connection, task discovery
- Start command: `celery -A app.celery_app worker --loglevel=info`

**Frontend Application Entry:**
- Location: `frontend/src/main.tsx`
- Function: `createRoot(document.getElementById('root')!).render(<App />)`
- Triggers: Browser loads index.html
- Responsibilities: React initialization, DOM mounting
- Build command: `npm run build` → `vite build`

**Frontend Router Entry:**
- Location: `frontend/src/App.tsx`
- Component: `<BrowserRouter><Routes>...</Routes></BrowserRouter>`
- Triggers: URL navigation
- Responsibilities: Route matching and component rendering

## Error Handling

**Strategy:** Exception bubbling with centralized error handling

**Patterns:**
- Backend: Service layer throws Python exceptions → API layer catches and returns appropriate HTTP status codes
- Frontend: Try/catch in API calls → console.error() + optional user error state
- Background tasks: Celery automatic retry with exponential backoff

**HTTP Error Codes:**
- 400: Validation error (Pydantic)
- 401: Unauthorized (missing or invalid JWT)
- 403: Forbidden (insufficient role)
- 404: Not found
- 500: Internal server error

## Cross-Cutting Concerns

**Logging:**
- Backend: Python `logging` module (configured in `backend/app/main.py`)
- Frontend: `console.log`, `console.error` (no structured logging)
- Background tasks: Celery task logging to stdout

**Validation:**
- Backend: Pydantic schemas at API boundary (`backend/app/schemas/*.py`)
- Frontend: HTML5 form validation + client-side checks
- Database: SQLAlchemy constraints (NOT NULL, UNIQUE, CHECK)

**Authentication:**
- JWT middleware checks token on protected routes
- Implementation: `backend/app/utils/deps.py` → `get_current_active_user()`
- Token format: Bearer token in Authorization header
- Expiration: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in config

**Authorization:**
- Role-based access control via `require_role()` dependency
- Hierarchical: VIEWER can access public endpoints, EDITOR can create/update, ADMIN can manage users
- Enforcement: At API layer via FastAPI dependencies

**CORS:**
- Configured in `backend/app/main.py` with `CORSMiddleware`
- Allowed origins from `backend/app/config.py` (`cors_origins` list)
- Default origins: localhost:3000, localhost:5173

---

*Architecture analysis: 2026-01-14*
*Update when major patterns change*
