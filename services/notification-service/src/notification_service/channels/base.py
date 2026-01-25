"""Base notification channel."""

from abc import ABC, abstractmethod
from typing import Any

from notification_service.models.notification import Notification


class BaseChannel(ABC):
    """Abstract base class for notification channels."""

    @abstractmethod
    async def send(self, notification: Notification) -> tuple[bool, str | None]:
        """
        Send a notification.

        Args:
            notification: The notification to send

        Returns:
            Tuple of (success, error_message)
        """
        pass

    @abstractmethod
    async def send_batch(
        self, notifications: list[Notification]
    ) -> list[tuple[Notification, bool, str | None]]:
        """
        Send a batch of notifications.

        Args:
            notifications: List of notifications to send

        Returns:
            List of (notification, success, error_message) tuples
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections."""
        pass
