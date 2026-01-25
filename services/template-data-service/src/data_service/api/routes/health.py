"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

from data_service.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Standard health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.service_name,
        "contract": settings.contract_name,
    }
