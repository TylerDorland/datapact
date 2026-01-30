"""Configuration settings for Template Data Service."""

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://datapact:datapact_dev@localhost:5432/template_data"

    @field_validator("database_url", mode="after")
    @classmethod
    def convert_sslmode_for_asyncpg(cls, v: str) -> str:
        """Convert sslmode to ssl for asyncpg compatibility."""
        return v.replace("sslmode=", "ssl=")

    # Environment
    environment: str = "development"
    debug: bool = True

    # Service identification
    service_name: str = "template-data-service"
    contract_name: str = "example_dataset"

    # Contract Service URL
    contract_service_url: str = "http://contract-service:8000"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
