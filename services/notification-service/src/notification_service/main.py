"""FastAPI application for Notification Service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from notification_service.api.routes import (
    events_router,
    notifications_router,
    watchers_router,
)
from notification_service.config import settings
from notification_service.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="DataPact Notification Service",
    description="Notification and alerting service for DataPact events",
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

# Include routers
app.include_router(events_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(watchers_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "0.1.0",
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "service": "DataPact Notification Service",
        "version": "0.1.0",
        "docs": "/docs",
    }
