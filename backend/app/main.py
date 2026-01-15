"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.api import categories, incidents, ingestion, auth, analytics, exports
from app.utils.rate_limit import limiter
import secrets

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Government Accountability Database API",
    version="0.1.0",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
)

# Rate Limiting - Configure SlowAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Middleware - Add trusted host middleware for production
if not settings.debug:
    allowed_hosts = getattr(settings, 'allowed_hosts', ['*'])
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts if allowed_hosts != ['*'] else ['*']
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Session middleware for enhanced security
app.add_middleware(
    SessionMiddleware,
    secret_key=getattr(settings, 'secret_key', secrets.token_urlsafe(32))
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Government Accountability Database API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for container orchestration and monitoring.
    Returns basic health status for liveness probes.
    """
    return {"status": "healthy", "service": "gadb-api"}


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probes.
    Checks database connectivity and other dependencies.
    """
    from app.database import get_db
    from sqlalchemy import text

    try:
        # Check database connectivity
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        return {"status": "unhealthy", "database": db_status}, 503

    return {
        "status": "ready",
        "database": db_status,
        "service": "gadb-api"
    }


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(analytics.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
