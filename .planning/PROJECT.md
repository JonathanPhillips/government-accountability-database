# Government Accountability Database (GADB) - Project Overview

**Project Type**: Brownfield - Existing Production-Ready Application
**Created**: 2026-01-14
**Status**: Active Development - Quality & Security Improvements

## Project Vision

A comprehensive web application for tracking, documenting, and analyzing government accountability incidents including misconduct, corruption, constitutional violations, and civil liberties abuses.

## Current State

### What's Built ✅
- **Core Application**: Full-stack application with FastAPI backend and React frontend
- **Authentication**: JWT-based auth with role-based access control (ADMIN, EDITOR, REVIEWER, VIEWER)
- **Database Schema**: Comprehensive 11-model schema tracking incidents, actors, sources, categories
- **API Layer**: RESTful endpoints for all entities with pagination, filtering, export
- **Analytics Dashboard**: Visualizations with charts for trends, severity, geography
- **Content Ingestion**:
  - RSS feed processing from 5 sources (ProPublica, The Intercept, BBC, EFF, NPR)
  - YouTube transcript extraction
  - PDF content processing with OCR support
  - Celery background task queue
- **Testing**: 126 tests (44% backend coverage, 61 tests + 33 frontend tests + 32 E2E cases)
- **Infrastructure**: Docker Compose setup, GitHub Actions CI/CD, Kubernetes manifests

### What Needs Improvement 🔧
From codebase analysis (.planning/codebase/CONCERNS.md):

**Critical Security Issues:**
1. Committed .env files with real secrets (POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY)
2. No rate limiting on any API endpoints (vulnerable to brute force, credential stuffing)
3. Hardcoded default admin credentials widely documented

**Quality Issues:**
1. Service layer completely untested (incident_service, actor_service, category_service, rss_ingester, youtube_ingester, pdf_processor)
2. Celery background tasks untested (ingestion_tasks.py)
3. Print statements instead of proper logging in 8+ locations
4. Bare exception handling with silent failures
5. Frontend error handling only logs to console (no user feedback)

**Technical Debt:**
1. Large files (439 lines for IncidentListPage.tsx, 335 lines for auth.py)
2. Hardcoded API URL in frontend (not environment-configurable)
3. N+1 query potential without eager loading
4. No caching strategy for frequently accessed data

## Immediate Goals (Sprint 1-2)

### Priority 1: Critical Security Fixes 🚨
**Why**: Production deployment blockers that expose system to attacks

**Requirements**:
1. Remove committed .env files from git history
   - Use `git rm --cached` for all .env files
   - Rotate all exposed credentials (POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY)
   - Verify .gitignore properly excludes .env files
   - Add pre-commit hook to prevent future commits

2. Implement rate limiting with slowapi
   - Authentication endpoints: 5 requests/minute
   - Read endpoints: 100 requests/minute
   - Write endpoints: 20 requests/minute
   - Add rate limit headers to responses

3. Force admin password change on first login
   - Detect default password and require immediate change
   - Add validation to reject default password
   - Generate random admin password during setup

### Priority 2: Testing for Untested Services 🧪
**Why**: Core business logic lacks validation; refactoring is risky without tests

**Requirements**:
1. Test suite for service classes (target: 80% coverage)
   - `backend/app/services/incident_service.py`
   - `backend/app/services/actor_service.py`
   - `backend/app/services/category_service.py`
   - `backend/app/services/rss_ingester.py`
   - `backend/app/services/youtube_ingester.py`
   - `backend/app/services/pdf_processor.py`

2. Test suite for Celery background tasks
   - `backend/app/tasks/ingestion_tasks.py` (ingest_rss_feed, ingest_all_feeds, cleanup_old_queue_items)
   - Mock Celery and external dependencies
   - Test error handling and retry logic

### Priority 3: Logging and Error Handling Improvements 📊
**Why**: Production debugging impossible without proper logging; users don't see errors

**Requirements**:
1. Replace all print() statements with logger.error() or logger.warning()
   - `backend/app/services/pdf_processor.py:49,78,176`
   - `backend/app/services/youtube_ingester.py:48`
   - `backend/app/services/rss_ingester.py:64,150`

2. Fix bare exception handling
   - Replace `except: pass` with specific exception types
   - Log all caught exceptions with context

3. Add user-facing error states in frontend
   - Display error messages to users when operations fail
   - Add error state to all major components (Header, HomePage, UserManagement, etc.)

## Near-Term Goals (Sprint 3-4)

### Code Quality Improvements
1. Refactor large files (>300 lines) into smaller components
2. Extract duplicate query patterns into helper functions
3. Add eager loading to prevent N+1 queries
4. Make API URL configurable via environment variable

### Performance Optimization
1. Implement Redis caching for frequently accessed data
2. Add database indexes on filtered columns
3. Add default pagination limits (max 100 items per page)
4. Optimize bundle size and implement code splitting

### Enhanced Testing
1. Increase backend coverage from 44% to 80%
2. Complete E2E test implementation (infrastructure exists)
3. Add integration tests for ingestion workflows

## Long-Term Vision

### Advanced Features
- Real-time notifications for new incidents
- Advanced analytics with ML-based pattern detection
- Public API with API keys and rate limit tiers
- Mobile applications (iOS/Android)
- Elasticsearch integration for advanced search

### Operational Excellence
- Monitoring dashboards (Grafana/Prometheus)
- Error tracking with Sentry
- Automated dependency updates
- Performance regression testing
- Security scanning automation

## Technical Context

### Technology Stack
- **Backend**: Python 3.11, FastAPI 0.104, SQLAlchemy 2.0, PostgreSQL 14, Redis 7, Celery
- **Frontend**: React 19.2, TypeScript 5.9, Vite 7.2, Tailwind CSS 4.1
- **Testing**: pytest (backend), Vitest (frontend), Playwright (E2E)
- **Infrastructure**: Docker, Docker Compose, Kubernetes/K3s, Nginx, GitHub Actions

### Architecture Pattern
Decoupled client-server with layered backend:
1. API Layer (FastAPI routers)
2. Service Layer (business logic)
3. Data Access Layer (SQLAlchemy ORM)
4. Schema Layer (Pydantic validation)
5. Infrastructure Layer (config, auth, deps)
6. Background Processing (Celery tasks)

### Key Files
- Backend entry: `backend/app/main.py`
- Frontend entry: `frontend/src/main.tsx`
- Models: `backend/app/models/*.py` (11 files)
- Services: `backend/app/services/*.py` (6 files)
- API routes: `backend/app/api/*.py` (6 files)
- Tests: `backend/tests/` (61 tests), `frontend/tests/` (33 tests), `frontend/e2e/` (32 test cases)

## Success Criteria

### Sprint 1-2 (Security & Quality)
- ✅ All .env files removed from git history
- ✅ All credentials rotated
- ✅ Rate limiting implemented on all endpoints
- ✅ Admin password change forced on first login
- ✅ Service layer tests with 80%+ coverage
- ✅ Celery task tests with mocked dependencies
- ✅ All print() replaced with proper logging
- ✅ Frontend error states implemented

### Sprint 3-4 (Performance & Polish)
- ✅ Backend test coverage reaches 80%
- ✅ Redis caching implemented
- ✅ Database indexes added
- ✅ Large files refactored (<300 lines)
- ✅ E2E tests fully implemented
- ✅ API URL configurable

### Long-Term Success
- ✅ Production deployment with monitoring
- ✅ Zero critical security vulnerabilities
- ✅ 90%+ test coverage
- ✅ Sub-2-second page load times
- ✅ Active user base tracking incidents

## Development Guidelines

### Code Style
- Backend: PEP 8, type hints, docstrings for complex functions
- Frontend: ESLint, TypeScript strict mode, functional components with hooks
- Git: Conventional commits (feat:, fix:, docs:, test:, refactor:, chore:)

### Quality Gates
- All tests must pass before merge
- Code review required for all PRs
- Linting and type checking must pass
- No new security vulnerabilities introduced

### Testing Strategy
- Unit tests: Fast, isolated, test single functions/classes
- Integration tests: Test multiple components together with real database
- E2E tests: Test complete user workflows in browser

## Resources

### Documentation
- [README.md](../README.md) - Project overview
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment guide
- [SECURITY.md](../SECURITY.md) - Security policy
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [.planning/codebase/](.) - Codebase analysis (7 documents, 1,762 lines)

### Quick Start
```bash
# Start development environment
docker-compose up

# Run backend tests
cd backend && pytest tests/ -v --cov=app

# Run frontend tests
cd frontend && npm test

# Access application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

**Last Updated**: 2026-01-14
**Current Sprint**: Sprint 1 - Critical Security Fixes
**Next Review**: After Priority 1 completion
