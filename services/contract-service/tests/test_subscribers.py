"""Tests for subscriber management."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_subscriber(
    client: AsyncClient,
    sample_contract: dict[str, Any],
    sample_subscriber: dict[str, Any],
):
    """Test adding a subscriber to a contract."""
    # Create contract first
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Add subscriber
    response = await client.post(
        f"/api/v1/contracts/{contract_id}/subscribers",
        json=sample_subscriber,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["team"] == "analytics"
    assert data["use_case"] == "Order analytics dashboard"


@pytest.mark.asyncio
async def test_list_subscribers(
    client: AsyncClient,
    sample_contract: dict[str, Any],
    sample_subscriber: dict[str, Any],
):
    """Test listing subscribers for a contract."""
    # Create contract
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Add subscriber
    await client.post(
        f"/api/v1/contracts/{contract_id}/subscribers",
        json=sample_subscriber,
    )

    # List subscribers
    response = await client.get(f"/api/v1/contracts/{contract_id}/subscribers")
    assert response.status_code == 200
    subscribers = response.json()
    assert len(subscribers) == 1
    assert subscribers[0]["team"] == "analytics"


@pytest.mark.asyncio
async def test_remove_subscriber(
    client: AsyncClient,
    sample_contract: dict[str, Any],
    sample_subscriber: dict[str, Any],
):
    """Test removing a subscriber from a contract."""
    # Create contract
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Add subscriber
    sub_resp = await client.post(
        f"/api/v1/contracts/{contract_id}/subscribers",
        json=sample_subscriber,
    )
    subscriber_id = sub_resp.json()["id"]

    # Remove subscriber
    response = await client.delete(
        f"/api/v1/contracts/{contract_id}/subscribers/{subscriber_id}"
    )
    assert response.status_code == 204

    # Verify removed
    list_resp = await client.get(f"/api/v1/contracts/{contract_id}/subscribers")
    assert len(list_resp.json()) == 0


@pytest.mark.asyncio
async def test_duplicate_subscriber_rejected(
    client: AsyncClient,
    sample_contract: dict[str, Any],
    sample_subscriber: dict[str, Any],
):
    """Test that duplicate team subscriptions are rejected."""
    # Create contract
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Add subscriber
    await client.post(
        f"/api/v1/contracts/{contract_id}/subscribers",
        json=sample_subscriber,
    )

    # Try to add same team again
    response = await client.post(
        f"/api/v1/contracts/{contract_id}/subscribers",
        json=sample_subscriber,
    )
    assert response.status_code == 409
