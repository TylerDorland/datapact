"""Notification channels."""

from notification_service.channels.base import BaseChannel
from notification_service.channels.email import EmailChannel

__all__ = ["BaseChannel", "EmailChannel"]
