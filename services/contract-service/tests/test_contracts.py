"""Tests for contract CRUD operations."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_contract(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test creating a new contract."""
    response = await client.post("/api/v1/contracts", json=sample_contract)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "test_orders"
    assert data["version"] == "1.0.0"
    assert len(data["fields"]) == 4
    assert len(data["quality_metrics"]) == 2
    assert data["publisher_team"] == "commerce"


@pytest.mark.asyncio
async def test_get_contract(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test retrieving a contract by ID."""
    # Create first
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    assert create_resp.status_code == 201
    contract_id = create_resp.json()["id"]

    # Then retrieve
    response = await client.get(f"/api/v1/contracts/{contract_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "test_orders"


@pytest.mark.asyncio
async def test_get_contract_by_name(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test retrieving a contract by name."""
    # Create first
    await client.post("/api/v1/contracts", json=sample_contract)

    # Then retrieve by name
    response = await client.get("/api/v1/contracts/name/test_orders")
    assert response.status_code == 200
    assert response.json()["name"] == "test_orders"


@pytest.mark.asyncio
async def test_contract_not_found(client: AsyncClient):
    """Test 404 for non-existent contract."""
    response = await client.get("/api/v1/contracts/name/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_contract_name(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test that duplicate contract names are rejected."""
    # Create first contract
    response1 = await client.post("/api/v1/contracts", json=sample_contract)
    assert response1.status_code == 201

    # Try to create another with same name
    response2 = await client.post("/api/v1/contracts", json=sample_contract)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_list_contracts(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test listing contracts with pagination."""
    # Create a contract
    await client.post("/api/v1/contracts", json=sample_contract)

    # Create another with different name
    contract2 = sample_contract.copy()
    contract2["name"] = "test_customers"
    await client.post("/api/v1/contracts", json=contract2)

    # List all
    response = await client.get("/api/v1/contracts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["contracts"]) == 2


@pytest.mark.asyncio
async def test_list_contracts_filter_by_status(
    client: AsyncClient, sample_contract: dict[str, Any]
):
    """Test filtering contracts by status."""
    await client.post("/api/v1/contracts", json=sample_contract)

    response = await client.get("/api/v1/contracts?status=active")
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_update_contract(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test updating a contract creates a new version."""
    # Create first
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Update
    update_data = {
        "version": "1.1.0",
        "description": "Updated description",
        "change_summary": "Added new description",
    }
    response = await client.put(f"/api/v1/contracts/{contract_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["version"] == "1.1.0"
    assert response.json()["description"] == "Updated description"


@pytest.mark.asyncio
async def test_deprecate_contract(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test deprecating a contract (soft delete)."""
    # Create first
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Deprecate
    response = await client.delete(f"/api/v1/contracts/{contract_id}")
    assert response.status_code == 204

    # Verify status changed
    get_resp = await client.get(f"/api/v1/contracts/{contract_id}")
    assert get_resp.json()["status"] == "deprecated"


@pytest.mark.asyncio
async def test_contract_versions(client: AsyncClient, sample_contract: dict[str, Any]):
    """Test retrieving contract version history."""
    # Create
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Update twice
    await client.put(
        f"/api/v1/contracts/{contract_id}",
        json={"version": "1.1.0", "change_summary": "First update"},
    )
    await client.put(
        f"/api/v1/contracts/{contract_id}",
        json={"version": "1.2.0", "change_summary": "Second update"},
    )

    # Get versions
    response = await client.get(f"/api/v1/contracts/{contract_id}/versions")
    assert response.status_code == 200
    versions = response.json()
    assert len(versions) == 2  # Two updates = two version snapshots


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "contract-service"
