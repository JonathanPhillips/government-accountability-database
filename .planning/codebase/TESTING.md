# Testing Patterns

**Analysis Date:** 2026-01-14

## Test Framework

**Runner:**
- Backend: pytest 7.4.4 (`backend/pytest.ini`)
- Frontend: Vitest 4.0.17 (`frontend/vitest.config.ts`)
- E2E: Playwright 1.57.0 (`frontend/playwright.config.ts`)

**Assertion Library:**
- Backend: Built-in Python `assert` statements
- Frontend: Vitest built-in `expect` with matchers from `@testing-library/jest-dom`

**Run Commands:**
```bash
# Backend
cd backend
pytest                                  # Run all tests
pytest --cov=app                        # With coverage
pytest -v                               # Verbose output
pytest tests/test_models.py             # Single file
pytest -m integration                   # By marker

# Frontend
cd frontend
npm test                                # Run all unit tests
npm test -- --watch                     # Watch mode
npm test -- path/to/file.test.ts        # Single file
npm run test:coverage                   # Coverage report
npm run test:e2e                        # E2E tests (Playwright)
```

## Test File Organization

**Location:**
- Backend: Separate `tests/` directory (`backend/tests/`)
- Frontend unit: Co-located `__tests__/` directories (e.g., `src/utils/__tests__/export.test.ts`)
- Frontend E2E: Separate `e2e/` directory (`frontend/e2e/`)

**Naming:**
- Backend: `test_*.py` (e.g., `test_models.py`, `test_api_incidents.py`, `test_integration_auth.py`)
- Frontend unit: `*.test.ts` or `*.test.tsx` (e.g., `export.test.ts`, `AnalyticsDashboard.test.tsx`)
- Frontend E2E: `*.spec.ts` (e.g., `dashboard.spec.ts`, `analytics.spec.ts`)

**Structure:**
```
backend/tests/
  conftest.py           # Pytest fixtures
  test_models.py        # Model unit tests
  test_api_*.py         # API endpoint tests
  test_integration_*.py # Integration tests

frontend/src/
  utils/__tests__/
    export.test.ts      # Utility tests
  pages/__tests__/
    AnalyticsDashboard.test.tsx  # Component tests

frontend/e2e/
  dashboard.spec.ts     # E2E tests
  analytics.spec.ts
```

## Test Structure

**Suite Organization:**

**Backend:**
```python
# backend/tests/test_models.py
def test_incident_creation(db_session, sample_category):
    """Test creating an incident."""
    # arrange
    incident = Incident(
        title="Test Incident",
        date_occurred=date(2025, 1, 1),
        # ... other fields
    )

    # act
    db_session.add(incident)
    db_session.commit()

    # assert
    assert incident.id is not None
    assert incident.title == "Test Incident"
```

**Frontend:**
```typescript
// frontend/src/utils/__tests__/export.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('buildExportQueryString', () => {
  it('builds empty query string with no filters', () => {
    const result = buildExportQueryString({});
    expect(result).toBe('');
  });

  it('builds query string with category filter', () => {
    const result = buildExportQueryString({ category_id: 1 });
    expect(result).toBe('?category_id=1');
  });
});
```

**Patterns:**
- Backend: Function-based tests, descriptive names, arrange/act/assert pattern
- Frontend: `describe` blocks for grouping, `it` for individual tests
- Use `beforeEach` for per-test setup, avoid `beforeAll`
- Use `afterEach` to restore mocks: `vi.restoreAllMocks()` (frontend), fixture cleanup (backend)

## Mocking

**Framework:**
- Backend: pytest fixtures with dependency injection
- Frontend: Vitest `vi.mock()`, `vi.fn()`, `vi.mocked()`

**Backend Patterns:**
```python
# backend/tests/conftest.py
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def sample_incident(db_session, sample_category):
    """Pre-created incident for testing."""
    incident = Incident(...)
    db_session.add(incident)
    db_session.commit()
    return incident
```

**Frontend Patterns:**
```typescript
import { vi } from 'vitest';

// Mock module
vi.mock('../services/api', () => ({
  api: {
    get: vi.fn()
  }
}));

// In test
beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.get).mockImplementation((url: string) => {
    if (url === '/analytics/summary') {
      return Promise.resolve({ data: mockData });
    }
  });
});
```

**What to Mock:**
- Backend: Database (in-memory SQLite), external APIs, file system
- Frontend: API calls (axios), browser APIs (localStorage, document methods), external services
- Background tasks: Celery tasks (not currently tested)

**What NOT to Mock:**
- Backend: Internal pure functions, SQLAlchemy ORM (use test database)
- Frontend: Simple utilities, TypeScript types

## Fixtures and Factories

**Backend Test Data:**
```python
# backend/tests/conftest.py
@pytest.fixture
def sample_category(db_session):
    """Pre-created category for testing."""
    category = Category(
        name="Government Misconduct",
        description="Test category"
    )
    db_session.add(category)
    db_session.commit()
    return category

@pytest.fixture
def admin_user(db_session):
    """Admin user with token for testing protected endpoints."""
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("testpassword"),
        role=UserRoleEnum.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def admin_token(admin_user):
    """JWT token for admin user."""
    return create_access_token(data={"sub": admin_user.email})
```

**Frontend Test Data:**
```typescript
// Inline factory functions
function createTestConfig(overrides?: Partial<Config>): Config {
  return {
    targetDir: '/tmp/test',
    global: false,
    ...overrides
  };
}

// Mock data in test files
const mockAnalyticsData = {
  summary: { total_incidents: 150 },
  by_severity: [...]
};
```

**Location:**
- Backend: Fixtures in `conftest.py`, shared across all tests
- Frontend: Factory functions in test files, mock data inline

## Coverage

**Requirements:**
- Backend: No enforced coverage target (current: 44%, 61 tests)
- Frontend: No enforced coverage target (current: 33 unit tests, 32 E2E tests)
- Focus on critical paths: services, models, API endpoints

**Configuration:**
- Backend: `pytest-cov` plugin, configured via command line
- Frontend: Vitest coverage via c8 (built-in)
- Excludes: Test files, configuration files

**View Coverage:**
```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm run test:coverage
open coverage/index.html
```

## Test Types

**Unit Tests:**
- Backend: Test single function/class in isolation (23 tests)
  - Examples: `test_models.py` (model creation, relationships)
  - Mock: All external dependencies (database uses in-memory SQLite)
  - Speed: Fast (<100ms per test)
- Frontend: Test single component or utility function (33 tests)
  - Examples: `export.test.ts`, component rendering tests
  - Mock: API calls, browser APIs
  - Speed: Fast

**Integration Tests:**
- Backend: Test multiple modules together (38 tests)
  - Examples: `test_integration_auth.py` (API + service + database)
  - Mock: Only external boundaries (no mocking of internal modules)
  - Database: In-memory SQLite with real schema
- Frontend: Limited integration testing (most tests are unit-level)

**E2E Tests:**
- Frontend: Playwright for full user flows (32 test cases, infrastructure ready)
  - Examples: `dashboard.spec.ts`, `analytics.spec.ts`, `search-filter.spec.ts`, `export.spec.ts`
  - Configuration: `playwright.config.ts`
  - Status: Infrastructure exists but tests not yet fully implemented
  - Note: Need to add `data-testid` attributes to components (planned enhancement)

## Common Patterns

**Async Testing:**

**Backend:**
```python
# pytest-asyncio for async tests
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected
```

**Frontend:**
```typescript
it('should handle async operation', async () => {
  const result = await asyncFunction();
  expect(result).toBe('expected');
});
```

**Error Testing:**

**Backend:**
```python
def test_error_handling(db_session):
    with pytest.raises(HTTPException) as exc_info:
        # operation that should raise
    assert exc_info.value.status_code == 404
```

**Frontend:**
```typescript
it('should throw on invalid input', () => {
  expect(() => functionCall()).toThrow('error message');
});

// Async error
it('should reject on failure', async () => {
  await expect(asyncCall()).rejects.toThrow('error message');
});
```

**Component Testing (Frontend):**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('renders dashboard with data', async () => {
  render(<AnalyticsDashboard />);

  await waitFor(() => {
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
  });
});
```

**API Endpoint Testing (Backend):**
```python
def test_list_incidents(client, admin_token, sample_incident):
    """Test GET /api/incidents endpoint."""
    response = client.get(
        "/api/incidents",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0
```

**Snapshot Testing:**
- Not used in this codebase
- Prefer explicit assertions for clarity

## Test Markers (Backend)

**Custom Markers:**
```ini
# backend/pytest.ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

**Usage:**
```python
@pytest.mark.integration
def test_auth_flow(client, db_session):
    """Integration test for authentication flow."""
    ...
```

## Test Coverage Gaps

**Missing Tests:**
- Service layer: No tests for `incident_service.py`, `actor_service.py`, `category_service.py`, `rss_ingester.py`, `pdf_processor.py`, `youtube_ingester.py`
- Background tasks: No tests for `ingestion_tasks.py`
- Frontend: Many components lack tests
- E2E: Infrastructure exists but tests not fully implemented

**Priority Areas for Testing:**
- Service layer business logic (high impact)
- Celery background tasks (data integrity)
- API error handling paths
- Frontend user interaction flows

---

*Testing analysis: 2026-01-14*
*Update when test patterns change*
