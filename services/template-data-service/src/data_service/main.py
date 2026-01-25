"""Main FastAPI application for Template Data Service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_service.api.routes import data, health, metrics, schema
from data_service.config import settings
from data_service.database import engine
from data_service.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown."""
    # Startup: create tables if in development mode
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="DataPact Template Data Service",
    description="Reference implementation for contract-compliant data services",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Contract compliance endpoints
app.include_router(health.router, tags=["health"])
app.include_router(schema.router, tags=["schema"])
app.include_router(metrics.router, tags=["metrics"])

# Data endpoints
app.include_router(data.router, tags=["data"])


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": settings.service_name,
        "contract": settings.contract_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "schema": "/schema",
        "metrics": "/metrics",
    }
