"""Configuration settings for Compliance Monitor."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Redis for Celery
    redis_url: str = "redis://localhost:6379/0"

    # Contract Service URL
    contract_service_url: str = "http://contract-service:8000"

    # Notification Service URL (for Phase 5)
    notification_service_url: str = "http://notification-service:8000"

    # Environment
    environment: str = "development"
    debug: bool = True

    # Check intervals (in seconds)
    schema_check_interval: int = 300  # 5 minutes
    quality_check_interval: int = 900  # 15 minutes
    availability_check_interval: int = 60  # 1 minute

    # Timeouts
    http_timeout: int = 30

    # Alerting
    slack_webhook_url: str | None = None
    alert_email_from: str = "alerts@datapact.io"
    smtp_host: str = "localhost"
    smtp_port: int = 1025


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
