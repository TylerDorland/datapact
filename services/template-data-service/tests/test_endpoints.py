"""Tests for Template Data Service endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient

from data_service.models import ExampleData


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "template-data-service"
    assert data["contract"] == "example_dataset"


@pytest.mark.asyncio
async def test_schema_endpoint(client: AsyncClient):
    """Test schema endpoint returns database structure."""
    response = await client.get("/schema")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "template-data-service"
    assert data["contract_name"] == "example_dataset"
    assert "tables" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """Test metrics endpoint returns quality metrics."""
    response = await client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "timestamp" in data
    assert "freshness" in data
    assert "completeness" in data
    assert "row_count" in data
    assert "availability" in data


@pytest.mark.asyncio
async def test_metrics_with_data(client: AsyncClient, seeded_data: list[ExampleData]):
    """Test metrics endpoint with seeded data."""
    response = await client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["row_count"] == 5
    assert data["freshness"]["is_fresh"] is True
    assert data["completeness"]["total_rows"] == 5


@pytest.mark.asyncio
async def test_create_data(client: AsyncClient, sample_data: dict[str, Any]):
    """Test creating a new data entry."""
    response = await client.post("/data", json=sample_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Item"
    assert data["category"] == "test"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_data(client: AsyncClient, seeded_data: list[ExampleData]):
    """Test listing data entries."""
    response = await client.get("/data")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_list_data_filter_by_category(
    client: AsyncClient, seeded_data: list[ExampleData]
):
    """Test filtering data by category."""
    response = await client.get("/data?category=category_a")
    assert response.status_code == 200

    data = response.json()
    # Items 0, 2, 4 have category_a
    assert len(data) == 3
    for item in data:
        assert item["category"] == "category_a"


@pytest.mark.asyncio
async def test_list_data_filter_by_active(
    client: AsyncClient, seeded_data: list[ExampleData]
):
    """Test filtering data by active status."""
    response = await client.get("/data?is_active=true")
    assert response.status_code == 200

    data = response.json()
    # Items 0, 1, 2 are active
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_data_by_id(client: AsyncClient, sample_data: dict[str, Any]):
    """Test getting a specific data entry."""
    # Create first
    create_resp = await client.post("/data", json=sample_data)
    data_id = create_resp.json()["id"]

    # Get by ID
    response = await client.get(f"/data/{data_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"


@pytest.mark.asyncio
async def test_get_data_not_found(client: AsyncClient):
    """Test 404 for non-existent data entry."""
    response = await client.get("/data/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_data(client: AsyncClient, sample_data: dict[str, Any]):
    """Test deleting a data entry."""
    # Create first
    create_resp = await client.post("/data", json=sample_data)
    data_id = create_resp.json()["id"]

    # Delete
    response = await client.delete(f"/data/{data_id}")
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(f"/data/{data_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_data_stats(client: AsyncClient, seeded_data: list[ExampleData]):
    """Test getting data statistics."""
    response = await client.get("/data/stats/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_count"] == 5
    # Values: 0, 10, 20, 30, 40 = 100 total
    assert data["total_value"] == 100.0
    assert data["average_value"] == 20.0


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns service info."""
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "template-data-service"
    assert data["contract"] == "example_dataset"
    assert "/health" in data["health"]
