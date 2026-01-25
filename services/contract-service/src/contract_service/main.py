"""Main FastAPI application for Contract Service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contract_service.api.routes import contracts, fields, subscribers, validation, webhooks
from contract_service.config import settings
from contract_service.database import engine
from contract_service.models import Base


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
    title="DataPact Contract Service",
    description="Central registry for data contracts",
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
app.include_router(
    contracts.router,
    prefix="/api/v1/contracts",
    tags=["contracts"],
)
app.include_router(
    fields.router,
    prefix="/api/v1/contracts",
    tags=["fields"],
)
app.include_router(
    subscribers.router,
    prefix="/api/v1/contracts",
    tags=["subscribers"],
)
app.include_router(
    validation.router,
    prefix="/api/v1/contracts",
    tags=["validation"],
)
app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["webhooks"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "contract-service"}


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "DataPact Contract Service",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
