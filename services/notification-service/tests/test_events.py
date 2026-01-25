"""Tests for event ingestion API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_receive_schema_drift_event(
    client: AsyncClient,
    sample_schema_drift_event: dict,
    sample_preference,
):
    """Test receiving a schema drift event."""
    response = await client.post(
        "/api/v1/events/schema-drift",
        json=sample_schema_drift_event,
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["event_id"] == sample_schema_drift_event["event_id"]
    assert "notifications_queued" in data


@pytest.mark.asyncio
async def test_receive_quality_breach_event(
    client: AsyncClient,
    sample_quality_breach_event: dict,
    sample_preference,
):
    """Test receiving a quality breach event."""
    response = await client.post(
        "/api/v1/events/quality-breach",
        json=sample_quality_breach_event,
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["event_id"] == sample_quality_breach_event["event_id"]


@pytest.mark.asyncio
async def test_receive_pr_blocked_event(client: AsyncClient, sample_preference):
    """Test receiving a PR blocked event."""
    event_data = {
        "event_type": "pr_blocked",
        "contract_name": "test_dataset",
        "repository": "org/repo",
        "pr_number": 123,
        "pr_title": "Update schema",
        "pr_author": "developer",
        "reason": "Schema changes without contract update",
        "errors": ["Missing contract.yaml update"],
    }

    response = await client.post(
        "/api/v1/events/pr-blocked",
        json=event_data,
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"


@pytest.mark.asyncio
async def test_receive_contract_updated_event(client: AsyncClient, sample_preference):
    """Test receiving a contract updated event."""
    event_data = {
        "event_type": "contract_updated",
        "contract_name": "test_dataset",
        "previous_version": "1.0.0",
        "new_version": "1.1.0",
        "change_type": "field_added",
        "change_summary": "Added new field for user preferences",
        "added_fields": ["preferences"],
    }

    response = await client.post(
        "/api/v1/events/contract-updated",
        json=event_data,
    )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_receive_deprecation_warning_event(client: AsyncClient, sample_preference):
    """Test receiving a deprecation warning event."""
    event_data = {
        "event_type": "deprecation_warning",
        "contract_name": "test_dataset",
        "deprecation_date": "2024-06-01T00:00:00Z",
        "removal_date": "2024-09-01T00:00:00Z",
        "reason": "Migrating to new data model",
        "replacement_contract": "test_dataset_v2",
    }

    response = await client.post(
        "/api/v1/events/deprecation-warning",
        json=event_data,
    )

    assert response.status_code == 202


@pytest.mark.asyncio
async def test_invalid_event_data(client: AsyncClient):
    """Test that invalid event data is rejected."""
    # Missing required field 'contract_name'
    response = await client.post(
        "/api/v1/events/schema-drift",
        json={
            "event_type": "schema_drift",
            "errors": ["Some error"],
        },
    )

    assert response.status_code == 422  # Validation error
