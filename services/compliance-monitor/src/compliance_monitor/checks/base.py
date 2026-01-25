"""Base class for compliance checkers."""

from abc import ABC, abstractmethod
from typing import Any


class BaseChecker(ABC):
    """Abstract base class for compliance checkers."""

    def __init__(self, threshold: str):
        """
        Initialize checker with threshold string.

        Args:
            threshold: Threshold value as string (e.g., "15 minutes", "99.5%")
        """
        self.threshold = threshold
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @abstractmethod
    def check(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Perform the compliance check.

        Args:
            data: The data to check against the threshold

        Returns:
            Dict with status, message, and actual_value
        """
        pass

    def parse_percentage(self, threshold: str) -> float:
        """Parse a percentage threshold string to a float."""
        value = threshold.replace("%", "").strip()
        return float(value)

    def parse_duration(self, threshold: str) -> int:
        """
        Parse a duration threshold string to seconds.

        Supports formats like:
        - "15 minutes"
        - "1 hour"
        - "30 seconds"
        - "2 hours"
        """
        parts = threshold.lower().strip().split()
        if len(parts) != 2:
            raise ValueError(f"Invalid duration format: {threshold}")

        value = int(parts[0])
        unit = parts[1].rstrip("s")  # Remove trailing 's' for plurals

        multipliers = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }

        if unit not in multipliers:
            raise ValueError(f"Unknown time unit: {unit}")

        return value * multipliers[unit]

    def get_result(self) -> dict[str, Any]:
        """Return the check result as a dictionary."""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": len(self.errors) == 0,
        }
