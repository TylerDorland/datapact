"""Configuration settings for Contract Service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://datapact:datapact_dev@localhost:5432/contracts"

    # Redis (for future use with Celery)
    redis_url: str = "redis://localhost:6379/0"

    # Environment
    environment: str = "development"
    debug: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8001"]

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
