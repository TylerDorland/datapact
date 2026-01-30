"""Configuration for Dictionary Service."""

import json
from typing import Any

from pydantic import field_validator
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

    # Cache settings
    cache_ttl_seconds: int = 300  # 5 minutes

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()
