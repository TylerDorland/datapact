"""Configuration settings for Contract Service."""

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://datapact:datapact_dev@localhost:5432/contracts"

    @field_validator("database_url", mode="after")
    @classmethod
    def convert_sslmode_for_asyncpg(cls, v: str) -> str:
        """Convert sslmode to ssl for asyncpg compatibility."""
        # asyncpg uses 'ssl' instead of 'sslmode'
        return v.replace("sslmode=", "ssl=")

    # Redis (for future use with Celery)
    redis_url: str = "redis://localhost:6379/0"

    # Environment
    environment: str = "development"
    debug: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8001"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from JSON array or comma-separated string."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                # JSON array format
                return json.loads(v)
            # Comma-separated format
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # GitHub Integration (optional)
    github_webhook_secret: str | None = None
    github_token: str | None = None
    github_app_id: str | None = None
    github_app_private_key: str | None = None
    github_app_installation_id: str | None = None

    # Contract file patterns to look for in repositories
    contract_file_patterns: list[str] = [
        "contract.yaml",
        "contract.yml",
        "datapact.yaml",
        "datapact.yml",
    ]

    # Schema file patterns that trigger contract enforcement
    schema_file_patterns: list[str] = [
        "alembic/versions/",
        "migrations/",
        "schema.sql",
        "models.py",
        "models/",
    ]

    # Service URLs
    notification_service_url: str = "http://notification-service:8000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
