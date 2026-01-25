"""API routes for Notification Service."""

from notification_service.api.routes.events import router as events_router
from notification_service.api.routes.notifications import router as notifications_router
from notification_service.api.routes.watchers import router as watchers_router

__all__ = ["events_router", "notifications_router", "watchers_router"]
