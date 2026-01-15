"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "GADB"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./gadb.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API Keys
    anthropic_api_key: str = ""

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://192.168.0.18:30091"
    ]

    # Wayback Machine
    wayback_machine_api: str = "https://archive.org/wayback/available"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
