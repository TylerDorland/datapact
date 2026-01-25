"""Event ingestion API routes."""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.database import get_session
from notification_service.schemas.events import (
    EventType,
    SchemaDriftEvent,
    QualityBreachEvent,
    PRBlockedEvent,
    ContractUpdatedEvent,
    DeprecationWarningEvent,
    AvailabilityFailureEvent,
)
from notification_service.services.router import NotificationRouter
from notification_service.tasks.send_notification import process_event, send_notification

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/schema-drift", status_code=status.HTTP_202_ACCEPTED)
async def receive_schema_drift_event(
    event: SchemaDriftEvent,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Receive a schema drift event and trigger notifications.

    This endpoint is called by the compliance monitor when schema drift is detected.
    """
    router_service = NotificationRouter(session)
    notifications = await router_service.route_event(event)

    # Queue notifications for sending
    for notification in notifications:
        background_tasks.add_task(send_notification.delay, str(notification.id))

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "notifications_queued": len(notifications),
    }


@router.post("/quality-breach", status_code=status.HTTP_202_ACCEPTED)
async def receive_quality_breach_event(
    event: QualityBreachEvent,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Receive a quality SLA breach event and trigger notifications.

    This endpoint is called by the compliance monitor when quality thresholds are breached.
    """
    router_service = NotificationRouter(session)
    notifications = await router_service.route_event(event)

    for notification in notifications:
        background_tasks.add_task(send_notification.delay, str(notification.id))

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "notifications_queued": len(notifications),
    }


@router.post("/pr-blocked", status_code=status.HTTP_202_ACCEPTED)
async def receive_pr_blocked_event(
    event: PRBlockedEvent,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Receive a PR blocked event and trigger notifications.

    This endpoint is called by the GitHub integration when a PR is blocked.
    """
    router_service = NotificationRouter(session)
    notifications = await router_service.route_event(event)

    for notification in notifications:
        background_tasks.add_task(send_notification.delay, str(notification.id))

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "notifications_queued": len(notifications),
    }


@router.post("/contract-updated", status_code=status.HTTP_202_ACCEPTED)
async def receive_contract_updated_event(
    event: ContractUpdatedEvent,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Receive a contract updated event and trigger notifications.

    This endpoint is called by the contract service when a contract is updated.
    """
    router_service = NotificationRouter(session)
    notifications = await router_service.route_event(event)

    for notification in notifications:
        background_tasks.add_task(send_notification.delay, str(notification.id))

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "notifications_queued": len(notifications),
    }


@router.post("/deprecation-warning", status_code=status.HTTP_202_ACCEPTED)
async def receive_deprecation_warning_event(
    event: DeprecationWarningEvent,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Receive a deprecation warning event and trigger notifications.

    This endpoint is called when a contract is deprecated.
    """
    router_service = NotificationRouter(session)
    notifications = await router_service.route_event(event)

    for notification in notifications:
        background_tasks.add_task(send_notification.delay, str(notification.id))

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "notifications_queued": len(notifications),
    }


@router.post("/availability-failure", status_code=status.HTTP_202_ACCEPTED)
async def receive_availability_failure_event(
    event: AvailabilityFailureEvent,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Receive an availability failure event and trigger notifications.

    This endpoint is called when a service becomes unavailable.
    """
    router_service = NotificationRouter(session)
    notifications = await router_service.route_event(event)

    for notification in notifications:
        background_tasks.add_task(send_notification.delay, str(notification.id))

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "notifications_queued": len(notifications),
    }
