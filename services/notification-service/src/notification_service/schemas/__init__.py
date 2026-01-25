"""Pydantic schemas for Notification Service."""

from notification_service.schemas.events import (
    EventType,
    BaseEvent,
    SchemaDriftEvent,
    QualityBreachEvent,
    PRBlockedEvent,
    ContractUpdatedEvent,
    DeprecationWarningEvent,
)
from notification_service.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
)
from notification_service.schemas.watcher import (
    WatcherCreate,
    WatcherUpdate,
    WatcherResponse,
)

__all__ = [
    "EventType",
    "BaseEvent",
    "SchemaDriftEvent",
    "QualityBreachEvent",
    "PRBlockedEvent",
    "ContractUpdatedEvent",
    "DeprecationWarningEvent",
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "WatcherCreate",
    "WatcherUpdate",
    "WatcherResponse",
]
