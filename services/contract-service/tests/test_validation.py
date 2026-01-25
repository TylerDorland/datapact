"""Tests for validation and compliance endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_record_compliance_check(
    client: AsyncClient,
    sample_contract: dict[str, Any],
):
    """Test recording a compliance check result."""
    # Create contract first
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Record compliance check
    check_data = {
        "check_type": "schema",
        "status": "pass",
        "details": {"fields_checked": 4, "errors": []},
    }
    response = await client.post(
        f"/api/v1/contracts/{contract_id}/compliance",
        json=check_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["check_type"] == "schema"
    assert data["status"] == "pass"


@pytest.mark.asyncio
async def test_validate_contract_placeholder(
    client: AsyncClient,
    sample_contract: dict[str, Any],
):
    """Test the validate endpoint returns placeholder response."""
    # Create contract
    create_resp = await client.post("/api/v1/contracts", json=sample_contract)
    contract_id = create_resp.json()["id"]

    # Call validate
    response = await client.post(f"/api/v1/contracts/{contract_id}/validate")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
