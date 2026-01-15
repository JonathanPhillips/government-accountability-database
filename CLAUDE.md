# CLAUDE.md - Government Accountability Database (GADB)

This file provides guidance to Claude Code for working with the Government Accountability Database project.

## Project Overview

**Project Name**: Government Accountability Database (GADB)
**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: 2026-01-12

### Purpose
A comprehensive web application for tracking, documenting, and analyzing government accountability incidents including misconduct, corruption, constitutional violations, and civil liberties abuses.

### Technology Stack

**Backend:**
- Python 3.11+ with FastAPI 0.104+
- SQLAlchemy 2.0 with Alembic migrations
- PostgreSQL 14+ (production) / SQLite (dev/test)
- Redis 7+ for caching and Celery
- JWT authentication with Bcrypt
- pytest with 44% coverage

**Frontend:**
- React 19.2+ with TypeScript
- Tailwind CSS 4.0+
- Vite 7.0+ build tool
- React Router 7.0+
- Vitest for testing
- Playwright for E2E

**Infrastructure:**
- Docker with multi-stage builds
- Docker Compose (dev + prod configurations)
- GitHub Actions CI/CD (4 workflows)
- Kubernetes manifests (K3s/K8s ready)
- Nginx reverse proxy
- SSL/TLS support

## Project Structure

```
govt_accountability/
├── README.md                    # Project overview and quickstart
├── DEPLOYMENT.md                # Comprehensive deployment guide
├── CONTRIBUTING.md              # Development guidelines
├── CHANGELOG.md                 # Version history
├── SECURITY.md                  # Security policy
├── STATUS.md                    # Current project status
├── LICENSE                      # MIT License
├── docker-compose.yml           # Development environment
├── docker-compose.prod.yml      # Production environment
├── .github/
│   ├── workflows/               # CI/CD pipelines
│   │   ├── ci.yml              # Continuous integration
│   │   ├── deploy.yml          # Automated deployment
│   │   └── e2e-tests.yml       # E2E test automation
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   └── pull_request_template.md
├── backend/
│   ├── Dockerfile              # Backend container
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Dev environment template
│   ├── .env.production.example # Prod environment template
│   ├── pytest.ini              # Test configuration
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── tasks/             # Celery background tasks
│   │   ├── ingestion/         # Data ingestion
│   │   └── utils/             # Utilities
│   ├── scripts/               # Database management
│   │   ├── backup_database.sh
│   │   ├── restore_database.sh
│   │   └── init_database.sh
│   └── tests/                 # Backend test suite
├── frontend/
│   ├── Dockerfile             # Frontend container
│   ├── package.json           # npm dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.ts     # Tailwind configuration
│   ├── src/
│   │   ├── App.tsx           # Main application
│   │   ├── main.tsx          # Entry point
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── api/              # API client
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utility functions
│   ├── tests/                # Frontend test suite
│   └── e2e/                  # E2E test infrastructure
└── kubernetes/               # K8s/K3s manifests
```

## Development Status

### Completed Phases (12/12) ✅

1. ✅ **Phase 1**: Core Database Schema & Models
2. ✅ **Phase 2**: Authentication & Authorization
3. ✅ **Phase 3**: Core API Endpoints
4. ✅ **Phase 4**: Frontend Foundation
5. ✅ **Phase 5**: Analytics Dashboard
6. ✅ **Phase 6**: Advanced Search & Filtering
7. ✅ **Phase 7**: Data Export (CSV/JSON)
8. ✅ **Phase 8**: Enhanced Features
9. ✅ **Phase 9**: Testing & Quality Assurance (126 tests)
10. ✅ **Phase 10**: Production Readiness & Deployment
11. ✅ **Phase 11**: Documentation & CI/CD
12. ✅ **Phase 12**: Final Project Polish

### Test Coverage
- **Total Tests**: 126
- **Backend**: 61 tests (44% coverage)
  - 23 unit tests
  - 38 integration tests
- **Frontend**: 33 tests
  - 15 component tests
  - 18 utility tests
- **E2E**: 32 test cases (infrastructure ready)

## Recent Accomplishments

### 2026-01-15
- ✅ **SUCCESSFULLY DEPLOYED TO PRODUCTION (Docker Compose)**
  - Fixed critical Redis/PostgreSQL URL encoding issues (special characters in passwords)
  - Fixed Pydantic settings parsing for CORS_ORIGINS (JSON array format required)
  - Modified docker-compose.prod.yml to use env_file directive for proper environment loading
  - All backend services now healthy and operational
  - Verified ingestion system working in production (5 test articles successfully ingested)
- ✅ **DEPLOYED INGESTION SYSTEM TO PRODUCTION**
  - Fixed Docker dependency issues (slowapi, email-validator)
  - Rebuilt all containers with updated dependencies
  - All services running: backend (healthy), frontend (running), celery-worker (functional), celery-beat (functional), postgres (healthy), redis (healthy)
- ✅ **Comprehensive Ingestion Documentation (1650+ lines)**
  - Created INGESTION_SOURCES.md (800+ lines) - Complete source configuration guide
  - Created INGESTION_SETUP.md (850+ lines) - Setup and testing procedures
  - Documented 5 RSS feed sources and 4 YouTube channel sources
  - Documented automated Celery Beat schedule (4 periodic tasks)
- ✅ **End-to-End Ingestion Testing**
  - RSS feed ingestion: Successfully ingested 5 articles from ProPublica in ~5 seconds
  - YouTube channel ingestion: Successfully ingested 3 videos with transcripts in ~3 seconds
  - Total ingestion queue: 86 items (53 news articles, 30 NGO reports, 3 videos)
  - All items marked as PENDING awaiting human review
  - 100% success rate on all ingestion tasks
- ✅ **Celery Configuration Verified**
  - Celery worker: Connected to Redis and processing tasks
  - Celery beat: Scheduling periodic tasks correctly
  - Automated schedules working: RSS feeds (every 2 hours), YouTube channels (every 4 hours)
  - Task retry logic with exponential backoff verified
- ✅ **Production Readiness**
  - All Docker containers healthy and operational
  - Database ingestion queue functioning correctly
  - Real-time task monitoring working
  - Error handling and logging verified

### 2026-01-12
- ✅ Completed all 12 development phases
- ✅ Implemented 126 comprehensive tests
- ✅ Created complete documentation suite (2,142 lines across 6 files)
- ✅ Set up 4 GitHub Actions CI/CD workflows
- ✅ Configured production Docker Compose environment
- ✅ Created database management scripts (backup, restore, init)
- ✅ Implemented security middleware and health checks
- ✅ Created GitHub issue and PR templates
- ✅ Published SECURITY.md and CHANGELOG.md
- ✅ Project verified and marked production-ready

### 2026-01-11
- ✅ Implemented core database models and API endpoints
- ✅ Built React frontend with TypeScript and Tailwind
- ✅ Created analytics dashboard
- ✅ Implemented advanced search and filtering
- ✅ Added CSV/JSON export functionality
- ✅ Set up authentication with JWT and RBAC
- ✅ Created comprehensive test suites

## Quick Start Commands

### Development Environment
```bash
# Start all services (frontend, backend, PostgreSQL, Redis, Celery)
docker-compose up

# Access points:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run tests
pytest tests/ -v --cov=app

# Run development server
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run linting
npm run lint

# Type check
npm run type-check
```

### Database Management
```bash
# Backup database
cd backend
./scripts/backup_database.sh

# Restore database
./scripts/restore_database.sh /path/to/backup.sql.gz

# Initialize database (fresh install)
./scripts/init_database.sh
```

## Key Features

### Core Functionality
- Full CRUD operations for government accountability incidents
- JWT authentication with role-based access control (admin, editor, viewer)
- Real-time analytics dashboard with charts and visualizations
- Advanced multi-criteria search and filtering
- CSV and JSON export with filter support
- Hierarchical category system
- Geographic tracking (state-level)
- Multi-source verification and linking
- Timeline analysis and trend detection

### Automated Ingestion System
- **RSS Feed Ingestion**: Automatic monitoring of 5 news sources (ProPublica, The Intercept, BBC, EFF, NPR)
- **YouTube Channel Monitoring**: Automatic video ingestion from 4 channels with transcript extraction
- **Celery-Based Task Queue**: Background processing with Redis broker
- **Automated Scheduling**: Celery Beat schedules periodic ingestion (RSS every 2 hours, YouTube every 4 hours)
- **Human-in-the-Loop**: All ingested content goes to review queue (PENDING status) before publication
- **Retry Logic**: Automatic retry with exponential backoff for failed ingestion tasks
- **Content Extraction**: Full article text extraction and YouTube transcript fetching
- **Queue Management**: Automatic cleanup of old processed items
- **Source Configuration**: Easy-to-configure source lists in `backend/app/tasks/ingestion_tasks.py`
- **Comprehensive Documentation**: 1650+ lines of setup, testing, and troubleshooting guides

### Security Features
- HTTPS enforcement in production
- JWT authentication with refresh tokens
- Bcrypt password hashing (12 rounds)
- CORS protection with configurable origins
- Rate limiting middleware
- SQL injection prevention (SQLAlchemy ORM)
- XSS and CSRF protection
- Secure session cookies (HTTPOnly, Secure, SameSite)
- Input validation with Pydantic
- Security headers (X-Frame-Options, CSP, etc.)

### DevOps & Monitoring
- Docker containerization with multi-stage builds
- Health check endpoints (/health for liveness, /health/ready for readiness)
- Automated database backups with S3 support
- Database restore procedures with safety backups
- CI/CD pipelines for testing, building, and deployment
- Security vulnerability scanning with Trivy
- Automated dependency updates with Dependabot
- Structured logging for debugging and monitoring
- Error tracking integration ready (Sentry)

## Code Style & Standards

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Docstrings for classes and complex functions
- SQLAlchemy models in separate files
- Pydantic schemas for validation
- Service layer for business logic
- pytest for testing with fixtures

### Frontend (TypeScript/React)
- Functional components with hooks
- TypeScript for type safety
- Tailwind CSS for styling (utility-first)
- React Router for navigation
- Vitest for unit/component testing
- Playwright for E2E testing
- ESLint for code quality

### Git Workflow
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Create feature branches from main
- Pull requests required for merging
- All tests must pass before merge
- Code review required

## Important Configuration Files

### Environment Variables
- `backend/.env.example` - Development environment template
- `backend/.env.production.example` - Production environment template
- `frontend/.env.example` - Frontend development config

**Critical Production Settings:**
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ORIGINS` - Allowed frontend origins
- `ADMIN_EMAIL` - Default admin email
- `ADMIN_PASSWORD` - Default admin password (MUST CHANGE)

### Docker Compose
- `docker-compose.yml` - Development environment with hot reload
- `docker-compose.prod.yml` - Production environment with multiple workers

## Testing Strategy

### Backend Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_incidents.py -v

# Run with specific marker
pytest tests/ -m "unit" -v
```

### Frontend Testing
```bash
# Run unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run E2E tests (requires backend running)
npm run test:e2e

# Generate coverage report
npm run test:coverage
```

## Deployment

### Local Development
Uses `docker-compose.yml` with hot reload enabled for both frontend and backend.

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive guide. Three deployment options:

1. **Docker Compose Production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Kubernetes (K3s/K8s)**
   ```bash
   kubectl apply -f kubernetes/
   ```

3. **Manual Deployment**
   Follow step-by-step instructions in DEPLOYMENT.md

### Pre-Deployment Checklist
- [ ] Change default admin credentials
- [ ] Generate strong SECRET_KEY
- [ ] Configure production database passwords
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for production domain
- [ ] Enable automated backups
- [ ] Set up monitoring and alerting
- [ ] Review security checklist in SECURITY.md

## Security Considerations

### Default Credentials (MUST CHANGE)
⚠️ **CRITICAL**: Change immediately after first deployment
- **Default Email**: `admin@gadb.local`
- **Default Password**: `changeme123`

### Secrets Management
- Never commit `.env` files to version control
- Use environment variables for sensitive data
- Generate strong SECRET_KEY: `openssl rand -hex 32`
- Use strong random passwords for all services
- Rotate secrets regularly

### Security Best Practices
See [SECURITY.md](SECURITY.md) for complete security guidelines including:
- Vulnerability reporting procedures
- Security update process
- Deployment security checklist
- Best practices for developers and deployers

## Common Tasks

### Adding a New API Endpoint
1. Create Pydantic schema in `backend/app/schemas/`
2. Add service logic in `backend/app/services/`
3. Create API router in `backend/app/api/`
4. Register router in `backend/app/main.py`
5. Write tests in `backend/tests/`
6. Update API documentation if needed

### Adding a New Frontend Component
1. Create component in `frontend/src/components/`
2. Add TypeScript types in `frontend/src/types/`
3. Write component tests in `frontend/tests/components/`
4. Import and use in page components
5. Update related API client functions if needed

### Creating a Database Migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Troubleshooting

**Backend won't start:**
- Check PostgreSQL is running
- Verify environment variables
- Check database migrations: `alembic current`
- Review logs: `docker-compose logs backend`

**Frontend build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version (requires 18+)
- Verify API URL in `.env`

**Database connection issues:**
- Verify PostgreSQL is running
- Check DATABASE_URL in environment
- Ensure database exists
- Check firewall rules

**Test failures:**
- Ensure test database is clean
- Check test fixtures are loading
- Verify mock data is valid
- Run tests in isolation: `pytest tests/test_file.py::test_name`

## Documentation

### Main Documentation Files
- [README.md](README.md) - Project overview, features, quick start
- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [SECURITY.md](SECURITY.md) - Security policy and guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history and release notes
- [STATUS.md](STATUS.md) - Current project status
- [backend/INGESTION_SOURCES.md](backend/INGESTION_SOURCES.md) - Ingestion source configuration and monitoring
- [backend/INGESTION_SETUP.md](backend/INGESTION_SETUP.md) - Ingestion system setup, testing, and troubleshooting

### API Documentation
Auto-generated API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

**Note**: API docs are disabled in production by default for security.

## Support & Resources

- **Issues**: Report bugs via GitHub Issues
- **Pull Requests**: Follow PR template in `.github/pull_request_template.md`
- **Security**: Report vulnerabilities to security@yourdomain.com (see SECURITY.md)
- **Discussions**: Use GitHub Discussions for questions and ideas

## Future Enhancements (Roadmap)

### Short Term
- Add `data-testid` attributes for E2E tests
- Increase test coverage to >80%
- Create seed data for sample incidents
- Set up monitoring dashboards (Grafana/Prometheus)
- Configure Sentry error tracking

### Medium Term
- GraphQL API implementation
- Advanced visualization tools
- Machine learning pattern detection
- Real-time collaboration features
- Webhook integrations

### Long Term
- Mobile applications (iOS/Android)
- Public API with rate limiting tiers
- Advanced search with Elasticsearch
- Multi-language support
- Advanced analytics and reporting

## Notes for Claude Code

### Working with This Project
- **Always read relevant documentation first** (README, DEPLOYMENT, STATUS)
- **Run tests before committing** changes
- **Follow existing patterns** in codebase
- **Update documentation** when making changes
- **Use type hints** in Python and TypeScript
- **Write tests** for new features
- **Follow conventional commits** for git messages

### Key Patterns
- **Backend**: Service layer pattern, dependency injection, SQLAlchemy models
- **Frontend**: Functional components, custom hooks, context for state
- **Testing**: Fixtures for backend, React Testing Library for frontend
- **API**: RESTful design, pagination, filtering, proper HTTP status codes

### File Locations
- **Models**: `backend/app/models/`
- **API Routes**: `backend/app/api/`
- **Schemas**: `backend/app/schemas/`
- **Services**: `backend/app/services/`
- **Components**: `frontend/src/components/`
- **Pages**: `frontend/src/pages/`
- **Tests**: `backend/tests/` and `frontend/tests/`

---

**Last Updated**: 2026-01-12
**Project Status**: ✅ Production Ready
**Version**: 1.0.0
