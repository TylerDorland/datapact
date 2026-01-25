"""Notification management API routes."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.database import get_session
from notification_service.models.notification import (
    Notification,
    NotificationPreference,
    NotificationStatus,
)
from notification_service.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    email: str = Query(..., description="Recipient email address"),
    status_filter: NotificationStatus | None = Query(None, alias="status"),
    event_type: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """List notifications for a user."""
    query = select(Notification).where(Notification.recipient_email == email)

    if status_filter:
        query = query.where(Notification.status == status_filter)

    if event_type:
        query = query.where(Notification.event_type == event_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # Get paginated results
    query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    notifications = result.scalars().all()

    return {
        "items": notifications,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Notification:
    """Get a single notification by ID."""
    result = await session.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.post("/{notification_id}/mark-read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Notification:
    """Mark a notification as read."""
    result = await session.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.read_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(notification)

    return notification


@router.post("/mark-all-read")
async def mark_all_read(
    email: str = Query(..., description="Recipient email address"),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    """Mark all notifications as read for a user."""
    result = await session.execute(
        select(Notification).where(
            Notification.recipient_email == email,
            Notification.read_at.is_(None),
        )
    )
    notifications = result.scalars().all()

    now = datetime.now(timezone.utc)
    for notification in notifications:
        notification.read_at = now

    await session.commit()

    return {"marked_read": len(notifications)}


# Preferences endpoints


@router.get("/preferences/{email}", response_model=NotificationPreferenceResponse)
async def get_preferences(
    email: str,
    session: AsyncSession = Depends(get_session),
) -> NotificationPreference:
    """Get notification preferences for a user."""
    result = await session.execute(
        select(NotificationPreference).where(NotificationPreference.email == email)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        # Return default preferences
        preferences = NotificationPreference(email=email)
        session.add(preferences)
        await session.commit()
        await session.refresh(preferences)

    return preferences


@router.post("/preferences", response_model=NotificationPreferenceResponse)
async def create_preferences(
    data: NotificationPreferenceCreate,
    session: AsyncSession = Depends(get_session),
) -> NotificationPreference:
    """Create notification preferences for a user."""
    # Check if already exists
    result = await session.execute(
        select(NotificationPreference).where(NotificationPreference.email == data.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Preferences already exist for this email",
        )

    preferences = NotificationPreference(**data.model_dump())
    session.add(preferences)
    await session.commit()
    await session.refresh(preferences)

    return preferences


@router.put("/preferences/{email}", response_model=NotificationPreferenceResponse)
async def update_preferences(
    email: str,
    data: NotificationPreferenceUpdate,
    session: AsyncSession = Depends(get_session),
) -> NotificationPreference:
    """Update notification preferences for a user."""
    result = await session.execute(
        select(NotificationPreference).where(NotificationPreference.email == email)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    await session.commit()
    await session.refresh(preferences)

    return preferences


@router.delete("/preferences/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preferences(
    email: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete notification preferences for a user."""
    result = await session.execute(
        select(NotificationPreference).where(NotificationPreference.email == email)
    )
    preferences = result.scalar_one_or_none()

    if preferences:
        await session.delete(preferences)
        await session.commit()


# Stats endpoint


@router.get("/stats/{email}")
async def get_notification_stats(
    email: str,
    days: int = Query(7, ge=1, le=90),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Get notification statistics for a user."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Total notifications
    total_query = select(func.count()).where(
        Notification.recipient_email == email,
        Notification.created_at >= cutoff,
    )
    total = (await session.execute(total_query)).scalar() or 0

    # By status
    status_query = (
        select(Notification.status, func.count())
        .where(
            Notification.recipient_email == email,
            Notification.created_at >= cutoff,
        )
        .group_by(Notification.status)
    )
    status_result = await session.execute(status_query)
    by_status = {str(row[0].value): row[1] for row in status_result.all()}

    # By event type
    type_query = (
        select(Notification.event_type, func.count())
        .where(
            Notification.recipient_email == email,
            Notification.created_at >= cutoff,
        )
        .group_by(Notification.event_type)
    )
    type_result = await session.execute(type_query)
    by_type = {row[0]: row[1] for row in type_result.all()}

    # Unread count
    unread_query = select(func.count()).where(
        Notification.recipient_email == email,
        Notification.read_at.is_(None),
    )
    unread = (await session.execute(unread_query)).scalar() or 0

    return {
        "email": email,
        "period_days": days,
        "total": total,
        "unread": unread,
        "by_status": by_status,
        "by_type": by_type,
    }
