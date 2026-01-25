"""Metrics collector for compliance monitoring."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.models import ExampleData


class MetricsCollector:
    """Collects quality metrics for compliance monitoring."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_freshness_metrics(self) -> dict[str, Any]:
        """Calculate data freshness based on updated_at timestamps."""
        result = await self.db.execute(
            select(
                func.max(ExampleData.updated_at).label("last_update"),
            )
        )
        row = result.fetchone()

        if row and row.last_update:
            now = datetime.utcnow()
            time_since_update = now - row.last_update
            is_fresh = time_since_update < timedelta(minutes=15)

            return {
                "last_update": row.last_update.isoformat(),
                "seconds_since_update": time_since_update.total_seconds(),
                "is_fresh": is_fresh,
            }

        return {
            "last_update": None,
            "seconds_since_update": None,
            "is_fresh": False,
        }

    async def get_completeness_metrics(self) -> dict[str, Any]:
        """Calculate completeness for required fields."""
        # Count total rows and non-null values for required fields
        result = await self.db.execute(
            select(
                func.count(ExampleData.id).label("total_rows"),
                func.count(ExampleData.name).label("name_count"),
                func.count(ExampleData.value).label("value_count"),
                func.count(ExampleData.category).label("category_count"),
            )
        )
        row = result.fetchone()

        if row and row.total_rows > 0:
            total = row.total_rows
            return {
                "total_rows": total,
                "field_completeness": {
                    "name": (row.name_count / total) * 100,
                    "value": (row.value_count / total) * 100,
                    "category": (row.category_count / total) * 100,
                },
                "overall_completeness": (
                    (row.name_count + row.value_count + row.category_count)
                    / (total * 3)
                    * 100
                ),
            }

        return {
            "total_rows": 0,
            "field_completeness": {},
            "overall_completeness": 100.0,  # Empty table is 100% complete
        }

    async def get_row_count(self) -> int:
        """Get total row count."""
        result = await self.db.execute(select(func.count(ExampleData.id)))
        return result.scalar() or 0

    async def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics in a single call."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "freshness": await self.get_freshness_metrics(),
            "completeness": await self.get_completeness_metrics(),
            "row_count": await self.get_row_count(),
            "availability": {
                "status": "up",
                "uptime_percentage": 99.9,  # Would come from actual monitoring
            },
        }
