# Government Accountability Database (GADB)

A comprehensive, production-ready database system for tracking and documenting government accountability incidents, legal violations, authoritarian patterns, and civil liberties concerns.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-blue.svg)](https://react.dev)

## 🎯 Project Status

**Status**: ✅ **Production Ready**
**Version**: 1.0.0
**Completed Phases**: 10/10
**Test Coverage**: 126 tests (Backend: 61, Frontend: 33, E2E: 32)
**Deployment**: Docker Compose + Kubernetes ready

## ✨ Features

### Core Functionality
- 📝 **Incident Management**: Create, read, update, and delete government accountability incidents
- 📊 **Analytics Dashboard**: Real-time analytics with charts and visualizations
- 🔍 **Advanced Search**: Multi-criteria filtering (severity, status, location, date range)
- 📤 **Export**: CSV and JSON export with filters applied
- 🔐 **Authentication**: JWT-based authentication with role-based access control
- 📧 **Email Notifications**: Configurable SMTP notifications for important events
- 🏷️ **Categorization**: Hierarchical category system for incident organization
- 🗺️ **Geographic Tracking**: State and geographic scope tracking
- 📅 **Timeline Analysis**: Temporal incident tracking and trends
- 🔗 **Source Verification**: Multi-source linking with verification status

### Technical Features
- 🚀 **Production Ready**: Full Docker containerization with health checks
- 🔒 **Security Hardened**: HTTPS, CORS, rate limiting, secure sessions
- 📈 **Scalable**: Horizontal scaling support for backend and workers
- 💾 **Automated Backups**: Database backup scripts with S3 support
- 🔍 **Monitoring**: Health check endpoints, logging, Sentry integration
- 🧪 **Well Tested**: 126 comprehensive tests across all layers
- 📚 **API Documentation**: Auto-generated OpenAPI/Swagger docs
- 🐳 **Container Ready**: Multi-stage Docker builds optimized for production

## 🏗️ Architecture

### Tech Stack
**Backend**:
- FastAPI 0.104+ (Python 3.11+)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- Pydantic v2 (validation)
- JWT authentication
- Celery + Redis (task queue)

**Frontend**:
- React 19.2+
- TypeScript
- Tailwind CSS 4.0+
- Vite (build tool)
- Axios (HTTP client)
- React Router 7.0+

**Database & Cache**:
- PostgreSQL 14+ (production)
- SQLite (development/testing)
- Redis 7+ (caching + Celery)

**Testing**:
- pytest (backend unit/integration)
- Vitest (frontend unit/component)
- Playwright (E2E)
- 126 total tests

**DevOps**:
- Docker + Docker Compose
- Kubernetes ready (K3s/K8s)
- GitHub Actions (CI/CD)
- Nginx (reverse proxy)

### System Design
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  PostgreSQL │
│   (React)   │     │   (FastAPI)  │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Redis     │
                    │  (Cache +    │
                    │   Celery)    │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │Celery Workers│
                    │  (Background │
                    │    Tasks)    │
                    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.11+ and Node.js 20+ (local development)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourorg/govt_accountability.git
cd govt_accountability

# Start all services
docker-compose up -d

# Initialize database
docker exec gadb-backend /app/scripts/init_database.sh

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

Default admin credentials:
- **Email**: `admin@gadb.local`
- **Password**: `changeme123` (⚠️ Change immediately!)

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start development server
npm run dev
```

### Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# Check frontend
open http://localhost:5173
```

## 📁 Project Structure

```
govt_accountability/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── api/             # API endpoints (incidents, auth, analytics, exports)
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic layer
│   │   ├── utils/           # Utility functions (auth, email, etc.)
│   │   ├── config.py        # Application configuration
│   │   ├── database.py      # Database session management
│   │   └── main.py          # FastAPI application entry
│   ├── tests/               # Backend tests (pytest)
│   │   ├── test_api_*.py    # API endpoint tests
│   │   ├── test_integration_*.py  # Integration tests
│   │   └── conftest.py      # Test fixtures
│   ├── scripts/             # Utility scripts
│   │   ├── backup_database.sh
│   │   ├── restore_database.sh
│   │   └── init_database.sh
│   ├── alembic/             # Database migrations
│   ├── Dockerfile           # Production container
│   └── requirements.txt     # Python dependencies
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── pages/           # React page components
│   │   ├── components/      # Reusable UI components
│   │   ├── utils/           # Frontend utilities (api, export)
│   │   ├── types/           # TypeScript type definitions
│   │   └── App.tsx          # Main application component
│   ├── e2e/                 # Playwright E2E tests
│   ├── public/              # Static assets
│   ├── Dockerfile           # Multi-stage production build
│   ├── nginx.conf           # Nginx configuration
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── DEPLOYMENT.md            # Deployment guide
├── README.md                # This file
└── .env.example             # Environment template
```

## 🧪 Testing

### Run All Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Backend with coverage
pytest tests/ --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test -- --run

# Frontend with coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

### Test Coverage

- **Backend**: 23 unit tests + 38 integration tests = 61 tests (44% coverage)
- **Frontend**: 15 component tests + 18 utility tests = 33 tests
- **E2E**: 32 test cases (infrastructure ready)
- **Total**: 126 comprehensive tests

### Test Reports

```bash
# Backend coverage report
open backend/htmlcov/index.html

# Frontend coverage report
open frontend/coverage/index.html

# E2E test report
npx playwright show-report
```

## 🚢 Deployment

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

Quick production deployment:

```bash
# Configure production environment
cp backend/.env.production.example backend/.env
cp frontend/.env.production.example frontend/.env.production
# Edit both .env files with production values

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker exec gadb-backend-prod /app/scripts/init_database.sh
```

### Environment Variables

#### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS`: Allowed frontend origins
- `SMTP_*`: Email configuration
- See `.env.example` for full list

#### Frontend (.env.production)
- `VITE_API_URL`: Backend API URL
- `VITE_SENTRY_DSN`: Sentry error tracking (optional)

### Health Checks

- **Liveness**: `GET /health`
- **Readiness**: `GET /health/ready`

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
```

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

**Authentication**:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh access token

**Incidents**:
- `GET /api/incidents` - List incidents (with filters)
- `POST /api/incidents` - Create incident
- `GET /api/incidents/{id}` - Get incident details
- `PUT /api/incidents/{id}` - Update incident
- `DELETE /api/incidents/{id}` - Delete incident

**Analytics**:
- `GET /api/analytics/overview` - Analytics overview
- `GET /api/analytics/timeline` - Timeline data
- `GET /api/analytics/categories` - Category distribution

**Export**:
- `GET /api/export/incidents/csv` - Export incidents as CSV
- `GET /api/export/incidents/json` - Export incidents as JSON
- `GET /api/export/analytics/csv` - Export analytics as CSV

## 🔐 Security

### Security Features ✅

**Authentication & Authorization**:
- JWT-based authentication with refresh tokens (30 min expiry)
- Bcrypt password hashing (12 rounds)
- Role-based access control (RBAC): VIEWER → REVIEWER → EDITOR → ADMIN
- Forced password change on first login for default admin account
- Default password rejection (changeme123, admin, password, etc.)

**API Protection**:
- **Rate Limiting** (slowapi):
  - Authentication endpoints: 5 requests/minute (prevents brute force)
  - Write operations: 20 requests/minute
  - Read operations: 100 requests/minute
  - Automatic HTTP 429 responses with retry headers
- CORS protection with configurable origins
- SQL injection prevention (SQLAlchemy ORM parameterized queries)
- XSS protection (Content Security Policy headers)

**Data Protection**:
- HTTPS enforcement in production
- Secure session cookies (HTTPOnly, Secure, SameSite)
- Environment-based secrets management (.env files, never committed)
- Pre-commit hook to prevent accidental secret commits

**Credential Management**:
- Cryptographically secure credential generation (Python `secrets` module)
- Documented rotation procedures (see `backend/CREDENTIALS_ROTATION.md`)
- Separate credentials per environment (dev, staging, production)
- 90-day rotation policy recommended

**Security Automation**:
- Pre-commit git hooks scan for secrets and sensitive files
- Automatic detection of hardcoded passwords, API keys, private keys
- CI/CD security scanning (dependency vulnerability checks)
- Automated security testing (13+ security-focused tests)

### Security Checklist ✅

**Before First Deployment**:
- [ ] Run hook installation: `cd backend && ./scripts/install-hooks.sh`
- [ ] Generate new credentials: See `backend/CREDENTIALS_ROTATION.md`
- [ ] **CRITICAL**: Change default admin password on first login (enforced)
- [ ] Update `SECRET_KEY` and `JWT_SECRET_KEY` (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Configure CORS_ORIGINS for your frontend domain
- [ ] Enable HTTPS/SSL with valid certificates
- [ ] Review and update all `.env.production` files

**Production Hardening**:
- [ ] Set DEBUG=False in production
- [ ] Disable API docs in production (SHOW_DOCS=False)
- [ ] Configure firewall rules (allow only 80/443)
- [ ] Set up automated backups (daily minimum)
- [ ] Enable monitoring and alerting (Sentry, Prometheus)
- [ ] Keep dependencies updated (run `pip list --outdated`)
- [ ] Enable rate limiting (already configured)
- [ ] Test forced password change flow

**Ongoing Security**:
- [ ] Rotate credentials every 90 days
- [ ] Review access logs monthly
- [ ] Update dependencies weekly
- [ ] Run security scans before each deployment
- [ ] Monitor for unusual API activity

## 🔄 Backup & Restore

### Automated Backups

```bash
# Set up daily backups (cron)
0 2 * * * docker exec gadb-backend-prod /app/scripts/backup_database.sh
```

### Manual Operations

```bash
# Create backup
docker exec gadb-backend-prod /app/scripts/backup_database.sh

# Restore from backup
docker exec -it gadb-backend-prod /app/scripts/restore_database.sh /backups/backup_file.sql.gz

# List backups
docker exec gadb-backend-prod ls -lh /backups/
```

## 📈 Monitoring

### Metrics & Observability

- **Health Endpoints**: Liveness and readiness probes
- **Logging**: Structured JSON logging
- **Error Tracking**: Sentry integration (optional)
- **Performance**: Prometheus metrics (optional)

### View Logs

```bash
# Docker Compose logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Application logs
docker exec gadb-backend tail -f /app/logs/app.log
```

## 🛠️ Development

### Code Style

```bash
# Backend linting
cd backend
pylint app/
black app/
isort app/

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Adding New Features

1. Create feature branch
2. Implement backend models/API
3. Add frontend components
4. Write tests (backend + frontend)
5. Update documentation
6. Create pull request

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`, `npm test`)
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📋 Key Principles

- **Verifiable Sources**: Every claim must link to verifiable primary sources
- **Clear Verification Levels**: Explicit confidence/verification status on all data
- **Human-in-the-Loop**: Automated ingestion requires human verification
- **Privacy First**: No personal information tracking
- **Transparency**: Open source and auditable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guide
- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourorg/govt_accountability/issues)
- **Security**: Report security issues to security@yourdomain.com

## 🎯 Roadmap

### Completed ✅
- [x] Core database schema and models
- [x] REST API with authentication
- [x] Frontend dashboard and UI
- [x] Analytics and reporting
- [x] Search and filtering
- [x] Export functionality (CSV/JSON)
- [x] Comprehensive testing (126 tests)
- [x] Docker containerization
- [x] Production hardening
- [x] Deployment documentation

### Future Enhancements 🚀
- [ ] GraphQL API
- [ ] Advanced visualization tools
- [ ] Machine learning for pattern detection
- [ ] Mobile applications (iOS/Android)
- [ ] Public API with rate limiting
- [ ] Advanced graph database layer
- [ ] Real-time collaboration features
- [ ] API webhooks and integrations

---

**Built with** ❤️ **for government accountability and transparency**
