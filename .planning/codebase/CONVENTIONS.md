# Coding Conventions

**Analysis Date:** 2026-01-14

## Naming Patterns

**Files:**
- Backend: snake_case for all Python modules (e.g., `incident_service.py`, `auth.py`, `pdf_processor.py`)
- Frontend components: PascalCase (e.g., `IncidentListPage.tsx`, `Header.tsx`, `AnalyticsDashboard.tsx`)
- Frontend utilities: camelCase (e.g., `api.ts`, `export.ts`)
- Tests: `test_*.py` for backend, `*.test.ts` or `*.test.tsx` for frontend
- Config files: Standard names (e.g., `tsconfig.json`, `vite.config.ts`, `pytest.ini`)

**Functions:**
- Backend: snake_case for all functions (e.g., `create_incident`, `get_by_id`, `hash_password`)
- Frontend: camelCase for functions (e.g., `exportIncidentsCSV`, `buildExportQueryString`, `getIncident`)
- Event handlers: `handle` prefix (e.g., `handleClick`, `handleSubmit`, `handleChange`)

**Variables:**
- Backend: snake_case (e.g., `db_session`, `incident_data`, `sample_category`)
- Frontend: camelCase (e.g., `mockAnalyticsData`, `queryString`, `baseUrl`)
- Constants: UPPER_SNAKE_CASE (e.g., `TEST_DATABASE_URL`, `MAX_UPLOAD_SIZE`, `API_BASE_URL`)

**Types:**
- Backend classes: PascalCase (e.g., `Incident`, `IncidentService`, `UserRoleEnum`)
- Backend enums: PascalCase with "Enum" suffix (e.g., `SeverityEnum`, `StatusEnum`, `UserRoleEnum`)
- Frontend interfaces: PascalCase, no "I" prefix (e.g., `IncidentDetail`, `Category`, `PaginatedResponse<T>`)
- Frontend types: PascalCase (e.g., `SeverityType`, `IncidentFilters`)

## Code Style

**Formatting:**
- Backend: 4-space indentation, double quotes for strings, line length ~79-100 characters
- Frontend: 2-space indentation, single quotes for strings, semicolons required
- No Prettier configuration detected - formatting relies on ESLint or editor settings
- Trailing commas present in frontend object literals

**Linting:**
- Backend: No explicit linter configured (no `.flake8`, `pylint.rc`, or `pyproject.toml` found)
- Frontend: ESLint with flat config (`frontend/eslint.config.js`)
  - Base: `@eslint/js` recommended config
  - TypeScript: `typescript-eslint` configs
  - React: `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`
  - Target: ES2020
  - Run: `npm run lint`

## Import Organization

**Order:**
- Backend: Standard library → Third-party packages → Local modules
  - Example: `import os` → `from fastapi import FastAPI` → `from app.models import Incident`
- Frontend: External packages → Internal modules → Relative imports → Type imports
  - Example pattern:
    ```typescript
    import React from 'react';  // External
    import { api } from '../services/api';  // Internal
    import type { IncidentFilters } from '../types';  // Types
    ```

**Grouping:**
- Blank lines between import groups (external, internal, relative)
- Alphabetical within each group (not strictly enforced)

**Path Aliases:**
- Backend: Relative imports only (no path aliases)
- Frontend: No path aliases configured (could use `@/` for `src/` but not currently used)

## Error Handling

**Patterns:**
- Backend: Throw exceptions, catch at API boundaries (route handlers)
  - Service layer throws domain exceptions
  - API layer catches and returns HTTP status codes
  - Example: `raise HTTPException(status_code=404, detail="Not found")`
- Frontend: Try/catch in API calls, log to console, optional user error state
  - Example: `catch (error) { console.error('Error:', error); }`
- Background tasks: Celery automatic retry with exponential backoff

**Error Types:**
- Backend: FastAPI `HTTPException` for API errors
- Backend: Custom exceptions extend Python `Exception` class
- Frontend: Native JavaScript `Error` objects

**When to throw:**
- Backend: Invalid input, missing dependencies, authorization failures, not found errors
- Frontend: API call failures, validation errors

**Error handling gaps:**
- Backend: Some services use `print()` instead of proper logging (see CONCERNS.md)
- Frontend: Most components log errors to console only, no user-facing error states

## Logging

**Framework:**
- Backend: Python `logging` module (configured in `backend/app/main.py`)
- Frontend: `console.log`, `console.error` (no structured logging library)
- Background tasks: Celery task logging to stdout

**Patterns:**
- Backend: Structured logging with levels (DEBUG, INFO, WARNING, ERROR)
- Backend issue: Some services use `print()` statements (needs migration to `logger`)
- Frontend: Console logging for debugging, no production logging strategy
- Frontend locations: `console.error()` in components (e.g., `Header.tsx:34`, `HomePage.tsx:22`, `UserManagement.tsx:36,60,75`)

## Comments

**When to Comment:**
- Backend: Explain why, not what - business logic, edge cases, workarounds
- Frontend: JSDoc for public APIs, inline for complex logic
- Avoid obvious comments (e.g., `# increment counter`)

**JSDoc/TSDoc:**
- Frontend: Triple-slash comments for functions (e.g., `/** * Utility functions for exporting data */`)
- Backend: Triple-quoted docstrings at module and class level
- Example: `"""Incident service for business logic."""`

**TODO Comments:**
- Format: `// TODO: description` (frontend) or `# TODO: description` (backend)
- No username or issue tracking enforced
- Several TODOs detected in codebase (see CONCERNS.md)

## Function Design

**Size:**
- Keep functions under 50-100 lines
- Extract helpers for complex logic
- Some large files detected (>300 lines) that could be refactored

**Parameters:**
- Backend: Explicit parameters with type hints (e.g., `def create(db: Session, incident: IncidentCreate) -> Incident:`)
- Frontend: Max 3-4 parameters, use options object for more
- Frontend: Destructure objects in parameter list where appropriate

**Return Values:**
- Backend: Explicit return type hints in function signatures
- Frontend: TypeScript return types inferred or explicit
- Return early for guard clauses

## Module Design

**Exports:**
- Backend: No explicit exports (Python imports directly from modules)
- Frontend: Named exports preferred (e.g., `export const api = ...`)
- Frontend: Default exports for React components (not consistently enforced)
- Frontend: Export from `index.ts` for public API (not extensively used)

**Barrel Files:**
- Backend: `__init__.py` files used to make directories into packages (often empty)
- Frontend: `index.ts` in `types/` directory for centralized type exports
- Pattern: Not extensively used for barrel exports

## Type Hints & Type Safety

**Backend:**
- Consistent use of Python type hints (PEP 484)
- Type hints on function parameters and return values
- Example: `def get_list(db: Session, filters: Dict[str, Any]) -> List[Incident]:`
- Optional types: `Optional[Type]` from `typing` module
- No mypy configuration detected

**Frontend:**
- TypeScript strict mode enabled (`frontend/tsconfig.app.json`)
- Explicit type annotations on function parameters and return types
- Type imports: `import type { Type }` for type-only imports
- Generics: Used appropriately (e.g., `PaginatedResponse<T>`)
- Optional chaining and nullish coalescing used throughout

## Component Patterns (Frontend)

**React Patterns:**
- Functional components with hooks (no class components)
- useState, useEffect used extensively
- No global state management (Redux, Zustand) - component-local state only
- Props: Typed interfaces or inline types

**Component Organization:**
- Pages (route components) in `src/pages/`
- Reusable components in `src/components/`
- Some large page components (>400 lines) could be extracted

---

*Convention analysis: 2026-01-14*
*Update when patterns change*
