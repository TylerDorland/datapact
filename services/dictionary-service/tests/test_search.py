"""Tests for SearchService."""

import pytest
import httpx
import respx

from dictionary_service.services.aggregator import DictionaryAggregator
from dictionary_service.services.search_service import SearchService, SearchScope
from dictionary_service.config import settings


class TestSearchService:
    @respx.mock
    @pytest.mark.asyncio
    async def test_search_all(self, sample_contracts_response):
        """Test searching across all scopes."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            results = await search_service.search("customer")

            assert results["total"] > 0
            assert results["query"] == "customer"

            # Should find customer fields and customers dataset
            field_results = [r for r in results["results"] if r["type"] == "field"]
            dataset_results = [r for r in results["results"] if r["type"] == "dataset"]

            assert len(field_results) > 0
            assert len(dataset_results) > 0
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_fields_only(self, sample_contracts_response):
        """Test searching fields only."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            results = await search_service.search("email", scope=SearchScope.FIELDS)

            # Should only find fields
            assert all(r["type"] == "field" for r in results["results"])
            assert results["total"] >= 2  # customer_email, email
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_with_pii_filter(self, sample_contracts_response):
        """Test searching with PII filter."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            results = await search_service.search("", scope=SearchScope.FIELDS, is_pii=True)

            # Should only find PII fields
            for result in results["results"]:
                assert result["data"]["is_pii"] is True
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_with_team_filter(self, sample_contracts_response):
        """Test searching with team filter."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            results = await search_service.search("id", team="commerce")

            # Should only find items from commerce team
            for result in results["results"]:
                if result["type"] == "field":
                    assert result["data"]["publisher_team"] == "commerce"
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_pagination(self, sample_contracts_response):
        """Test search pagination."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)

            # Get first page
            page1 = await search_service.search("", limit=2, offset=0)

            # Get second page
            page2 = await search_service.search("", limit=2, offset=2)

            assert page1["offset"] == 0
            assert page2["offset"] == 2
            assert len(page1["results"]) <= 2
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_suggest(self, sample_contracts_response):
        """Test autocomplete suggestions."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            suggestions = await search_service.suggest("cust")

            # Should suggest customer-related items
            assert "suggestions" in suggestions
            assert any("customer" in f.lower() for f in suggestions["suggestions"]["fields"])
            assert "customers" in suggestions["suggestions"]["datasets"]
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_pii_fields(self, sample_contracts_response):
        """Test getting all PII fields."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            pii_fields = await search_service.get_pii_fields()

            assert len(pii_fields) == 3
            assert all(f["is_pii"] for f in pii_fields)
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_fields_by_type(self, sample_contracts_response):
        """Test getting fields by data type."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            search_service = SearchService(aggregator)
            uuid_fields = await search_service.get_fields_by_type("uuid")

            assert len(uuid_fields) >= 2
            assert all(f["data_type"] == "uuid" for f in uuid_fields)
        finally:
            await aggregator.close()
