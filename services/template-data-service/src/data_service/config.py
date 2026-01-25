"""Configuration settings for Template Data Service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://datapact:datapact_dev@localhost:5432/template_data"

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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
