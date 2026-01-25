"""Main FastAPI application for Dictionary Service."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dictionary_service.config import settings
from dictionary_service.api.routes import dictionary_router, search_router, erd_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="DataPact Dictionary Service",
    description="Aggregates contracts into a searchable data dictionary with ERD generation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dictionary_router, prefix="/api/v1/dictionary", tags=["dictionary"])
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])
app.include_router(erd_router, prefix="/api/v1/erd", tags=["erd"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dictionary-service"}
