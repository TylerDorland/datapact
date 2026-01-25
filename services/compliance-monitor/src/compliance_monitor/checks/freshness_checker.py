"""Freshness compliance checker."""

from typing import Any

from compliance_monitor.checks.base import BaseChecker


class FreshnessChecker(BaseChecker):
    """
    Checks data freshness against SLA threshold.

    Freshness is measured as time since last data update.
    """

    def check(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Check freshness metric against threshold.

        Args:
            data: Freshness data from /metrics endpoint containing:
                - seconds_since_update: Number of seconds since last update
                - is_fresh: Boolean indicating if data is considered fresh
                - last_update: ISO timestamp of last update

        Returns:
            Dict with status, message, and actual values
        """
        seconds_since_update = data.get("seconds_since_update")

        if seconds_since_update is None:
            return {
                "status": "warning",
                "message": "No freshness data available",
                "actual_value": None,
                "threshold_seconds": None,
            }

        try:
            threshold_seconds = self.parse_duration(self.threshold)
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Invalid threshold format: {e}",
                "actual_value": seconds_since_update,
                "threshold_seconds": None,
            }

        is_fresh = seconds_since_update <= threshold_seconds

        if is_fresh:
            return {
                "status": "pass",
                "message": f"Data is fresh (updated {seconds_since_update:.0f}s ago, threshold: {threshold_seconds}s)",
                "actual_value": seconds_since_update,
                "threshold_seconds": threshold_seconds,
                "last_update": data.get("last_update"),
            }
        else:
            return {
                "status": "fail",
                "message": f"Data is stale (updated {seconds_since_update:.0f}s ago, threshold: {threshold_seconds}s)",
                "actual_value": seconds_since_update,
                "threshold_seconds": threshold_seconds,
                "last_update": data.get("last_update"),
            }
