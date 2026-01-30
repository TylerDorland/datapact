"""Configuration for Notification Service."""

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://datapact:datapact_dev@localhost:5432/contracts"

    @field_validator("database_url", mode="after")
    @classmethod
    def convert_sslmode_for_asyncpg(cls, v: str) -> str:
        """Convert sslmode to ssl for asyncpg compatibility."""
        return v.replace("sslmode=", "ssl=")

    # Redis for Celery
    redis_url: str = "redis://localhost:6379/1"

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
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Contract Service
    contract_service_url: str = "http://contract-service:8000"

    # SMTP Configuration
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = False
    smtp_from_email: str = "datapact@example.com"
    smtp_from_name: str = "DataPact"

    # Azure Communication Services (alternative to SMTP)
    email_provider: str = "smtp"  # "smtp" or "azure"
    acs_connection_string: str | None = None
    acs_sender_address: str = "DoNotReply@yourdomain.com"

    # Notification Settings
    notification_rate_limit_per_hour: int = 100
    notification_dedup_window_minutes: int = 60
    notification_batch_size: int = 50

    # Frontend URL for links in emails
    frontend_url: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
