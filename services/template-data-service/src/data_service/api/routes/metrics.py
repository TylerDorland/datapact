"""Metrics endpoint for compliance monitoring."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.database import get_db
from data_service.metrics.collector import MetricsCollector

router = APIRouter()


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """
    Return quality metrics for compliance monitoring.
    This endpoint is polled by the Compliance Monitor.
    """
    collector = MetricsCollector(db)
    return await collector.get_all_metrics()
