"""Tests for notification management API."""

import pytest
from httpx import AsyncClient

from notification_service.models.notification import Notification, NotificationStatus


@pytest.mark.asyncio
async def test_list_notifications(
    client: AsyncClient,
    sample_notification: Notification,
):
    """Test listing notifications for a user."""
    response = await client.get(
        "/api/v1/notifications",
        params={"email": sample_notification.recipient_email},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["recipient_email"] == sample_notification.recipient_email


@pytest.mark.asyncio
async def test_list_notifications_with_status_filter(
    client: AsyncClient,
    sample_notification: Notification,
):
    """Test filtering notifications by status."""
    response = await client.get(
        "/api/v1/notifications",
        params={
            "email": sample_notification.recipient_email,
            "status": "pending",
        },
    )

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_get_notification(
    client: AsyncClient,
    sample_notification: Notification,
):
    """Test getting a single notification."""
    response = await client.get(
        f"/api/v1/notifications/{sample_notification.id}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_notification.id)
    assert data["subject"] == sample_notification.subject


@pytest.mark.asyncio
async def test_get_notification_not_found(client: AsyncClient):
    """Test getting a non-existent notification."""
    response = await client.get(
        "/api/v1/notifications/00000000-0000-0000-0000-000000000000",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_mark_notification_read(
    client: AsyncClient,
    sample_notification: Notification,
):
    """Test marking a notification as read."""
    response = await client.post(
        f"/api/v1/notifications/{sample_notification.id}/mark-read",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["read_at"] is not None


@pytest.mark.asyncio
async def test_mark_all_read(
    client: AsyncClient,
    sample_notification: Notification,
):
    """Test marking all notifications as read."""
    response = await client.post(
        "/api/v1/notifications/mark-all-read",
        params={"email": sample_notification.recipient_email},
    )

    assert response.status_code == 200
    data = response.json()
    assert "marked_read" in data


@pytest.mark.asyncio
async def test_get_notification_stats(
    client: AsyncClient,
    sample_notification: Notification,
):
    """Test getting notification statistics."""
    response = await client.get(
        f"/api/v1/notifications/stats/{sample_notification.recipient_email}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_notification.recipient_email
    assert "total" in data
    assert "unread" in data
    assert "by_status" in data
    assert "by_type" in data


# Preferences tests


@pytest.mark.asyncio
async def test_get_preferences(client: AsyncClient, sample_preference):
    """Test getting notification preferences."""
    response = await client.get(
        f"/api/v1/notifications/preferences/{sample_preference.email}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_preference.email
    assert data["email_enabled"] == sample_preference.email_enabled


@pytest.mark.asyncio
async def test_get_preferences_creates_default(client: AsyncClient):
    """Test that getting preferences for new user creates defaults."""
    response = await client.get(
        "/api/v1/notifications/preferences/newuser@example.com",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["email_enabled"] is True  # Default


@pytest.mark.asyncio
async def test_create_preferences(client: AsyncClient):
    """Test creating notification preferences."""
    response = await client.post(
        "/api/v1/notifications/preferences",
        json={
            "email": "another@example.com",
            "email_enabled": True,
            "schema_drift_enabled": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "another@example.com"
    assert data["schema_drift_enabled"] is False


@pytest.mark.asyncio
async def test_create_preferences_duplicate(client: AsyncClient, sample_preference):
    """Test that duplicate preferences are rejected."""
    response = await client.post(
        "/api/v1/notifications/preferences",
        json={
            "email": sample_preference.email,
        },
    )

    assert response.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_update_preferences(client: AsyncClient, sample_preference):
    """Test updating notification preferences."""
    response = await client.put(
        f"/api/v1/notifications/preferences/{sample_preference.email}",
        json={
            "email_enabled": False,
            "digest_enabled": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email_enabled"] is False
    assert data["digest_enabled"] is True


@pytest.mark.asyncio
async def test_delete_preferences(client: AsyncClient, sample_preference):
    """Test deleting notification preferences."""
    response = await client.delete(
        f"/api/v1/notifications/preferences/{sample_preference.email}",
    )

    assert response.status_code == 204

    # Verify deletion
    response = await client.get(
        f"/api/v1/notifications/preferences/{sample_preference.email}",
    )
    # Should create new default preferences
    assert response.status_code == 200
