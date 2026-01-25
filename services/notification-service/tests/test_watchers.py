"""Tests for watcher management API."""

from uuid import uuid4

import pytest
from httpx import AsyncClient

from notification_service.models.watcher import Watcher


@pytest.mark.asyncio
async def test_create_watcher(client: AsyncClient):
    """Test creating a watcher."""
    contract_id = str(uuid4())
    response = await client.post(
        "/api/v1/watchers",
        json={
            "contract_id": contract_id,
            "watcher_email": "watcher@example.com",
            "watch_schema_drift": True,
            "watch_quality_breach": True,
            "reason": "Consuming this data for analytics",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["contract_id"] == contract_id
    assert data["watcher_email"] == "watcher@example.com"
    assert data["watch_schema_drift"] is True


@pytest.mark.asyncio
async def test_create_watcher_by_team(client: AsyncClient):
    """Test creating a watcher for a team."""
    response = await client.post(
        "/api/v1/watchers",
        json={
            "publisher_team": "data-platform",
            "watcher_email": "teamwatcher@example.com",
            "watch_schema_drift": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["publisher_team"] == "data-platform"


@pytest.mark.asyncio
async def test_create_watcher_by_tag(client: AsyncClient):
    """Test creating a watcher for a tag."""
    response = await client.post(
        "/api/v1/watchers",
        json={
            "tag": "pii",
            "watcher_email": "security@example.com",
            "watch_schema_drift": True,
            "watch_contract_updated": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tag"] == "pii"


@pytest.mark.asyncio
async def test_create_watcher_no_target(client: AsyncClient):
    """Test that watcher without target is rejected."""
    response = await client.post(
        "/api/v1/watchers",
        json={
            "watcher_email": "watcher@example.com",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_watchers(client: AsyncClient, sample_watcher: Watcher):
    """Test listing watchers."""
    response = await client.get("/api/v1/watchers")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_watchers_by_email(client: AsyncClient, sample_watcher: Watcher):
    """Test listing watchers filtered by email."""
    response = await client.get(
        "/api/v1/watchers",
        params={"email": sample_watcher.watcher_email},
    )

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["watcher_email"] == sample_watcher.watcher_email


@pytest.mark.asyncio
async def test_get_watcher(client: AsyncClient, sample_watcher: Watcher):
    """Test getting a single watcher."""
    response = await client.get(f"/api/v1/watchers/{sample_watcher.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_watcher.id)
    assert data["watcher_email"] == sample_watcher.watcher_email


@pytest.mark.asyncio
async def test_get_watcher_not_found(client: AsyncClient):
    """Test getting a non-existent watcher."""
    response = await client.get(
        "/api/v1/watchers/00000000-0000-0000-0000-000000000000",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_watcher(client: AsyncClient, sample_watcher: Watcher):
    """Test updating a watcher."""
    response = await client.put(
        f"/api/v1/watchers/{sample_watcher.id}",
        json={
            "watch_schema_drift": False,
            "watch_pr_blocked": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["watch_schema_drift"] is False
    assert data["watch_pr_blocked"] is True


@pytest.mark.asyncio
async def test_delete_watcher(client: AsyncClient, sample_watcher: Watcher):
    """Test deleting a watcher."""
    response = await client.delete(f"/api/v1/watchers/{sample_watcher.id}")

    assert response.status_code == 204

    # Verify deletion
    response = await client.get(f"/api/v1/watchers/{sample_watcher.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_watchers_by_email(client: AsyncClient, sample_watcher: Watcher):
    """Test getting watchers by email convenience endpoint."""
    response = await client.get(
        f"/api/v1/watchers/by-email/{sample_watcher.watcher_email}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["watcher_email"] == sample_watcher.watcher_email


@pytest.mark.asyncio
async def test_get_watchers_by_contract(client: AsyncClient, sample_watcher: Watcher):
    """Test getting watchers by contract ID."""
    response = await client.get(
        f"/api/v1/watchers/by-contract/{sample_watcher.contract_id}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["contract_id"] == str(sample_watcher.contract_id)
