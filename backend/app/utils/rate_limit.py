"""Rate limiting utilities for API endpoints."""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter - shared across all modules
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Rate limit strings for different endpoint types
AUTH_RATE_LIMIT = "5/minute"  # Authentication endpoints (login, register, password reset)
WRITE_RATE_LIMIT = "20/minute"  # Write operations (POST, PUT, PATCH, DELETE)
READ_RATE_LIMIT = "100/minute"  # Read operations (GET)
