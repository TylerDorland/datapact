"""Configuration for Dictionary Service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Service info
    service_name: str = "dictionary-service"
    environment: str = "development"

    # Contract Service connection
    contract_service_url: str = "http://contract-service:8000"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Cache settings
    cache_ttl_seconds: int = 300  # 5 minutes

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()
