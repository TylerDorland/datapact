"""Tests for DictionaryAggregator service."""

import pytest
import httpx
import respx

from dictionary_service.services.aggregator import DictionaryAggregator
from dictionary_service.config import settings


class TestDictionaryAggregator:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_full_dictionary(self, sample_contracts_response):
        """Test building full dictionary from contracts."""
        # Mock the contract service endpoint
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            dictionary = await aggregator.get_full_dictionary()

            # Check datasets
            assert len(dictionary["datasets"]) == 3
            assert dictionary["datasets"][0]["name"] == "orders"
            assert dictionary["datasets"][1]["name"] == "customers"

            # Check fields
            assert len(dictionary["fields"]) == 9  # 4 + 4 + 1

            # Check PII fields
            pii_count = len(dictionary["pii_fields"])
            assert pii_count == 3  # customer_email, email, name

            # Check teams
            assert "commerce" in dictionary["teams"]
            assert "crm" in dictionary["teams"]
            assert "analytics" in dictionary["teams"]

            # Check relationships
            assert len(dictionary["relationships"]) == 1
            assert dictionary["relationships"][0]["from_dataset"] == "orders"
            assert dictionary["relationships"][0]["to_dataset"] == "customers"

            # Check summary
            assert dictionary["summary"]["total_datasets"] == 3
            assert dictionary["summary"]["pii_field_count"] == 3
            assert dictionary["summary"]["active_datasets"] == 2
            assert dictionary["summary"]["deprecated_datasets"] == 1
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_dataset_details(self, sample_contracts_response):
        """Test getting details for a specific dataset."""
        contract = sample_contracts_response["contracts"][0]

        respx.get(f"{settings.contract_service_url}/api/v1/contracts/name/orders").mock(
            return_value=httpx.Response(200, json=contract)
        )

        aggregator = DictionaryAggregator()
        try:
            details = await aggregator.get_dataset_details("orders")

            assert details is not None
            assert details["name"] == "orders"
            assert details["publisher"]["team"] == "commerce"
            assert len(details["fields"]) == 4
            assert len(details["subscribers"]) == 2
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_dataset_details_not_found(self):
        """Test getting details for non-existent dataset."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts/name/nonexistent").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )

        aggregator = DictionaryAggregator()
        try:
            details = await aggregator.get_dataset_details("nonexistent")
            assert details is None
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_team_datasets(self, sample_contracts_response):
        """Test getting datasets for a specific team."""
        commerce_contracts = {
            "contracts": [c for c in sample_contracts_response["contracts"] if c["publisher_team"] == "commerce"]
        }

        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=commerce_contracts)
        )

        aggregator = DictionaryAggregator()
        try:
            datasets = await aggregator.get_team_datasets("commerce")

            assert len(datasets) == 1
            assert datasets[0]["name"] == "orders"
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_field_lineage(self, sample_contracts_response):
        """Test getting lineage for a field."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            lineage = await aggregator.get_field_lineage("orders", "customer_id")

            # Should have upstream reference to customers
            assert len(lineage["upstream"]) == 1
            assert lineage["upstream"][0]["dataset"] == "customers"

            # Should find similar field in customers dataset
            similar = [f for f in lineage["similar_fields"] if f["dataset"] == "customers"]
            assert len(similar) == 1
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_field_lineage_not_found(self, sample_contracts_response):
        """Test getting lineage for non-existent field."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            lineage = await aggregator.get_field_lineage("orders", "nonexistent_field")
            assert "error" in lineage
        finally:
            await aggregator.close()
