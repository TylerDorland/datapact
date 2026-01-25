"""Tests for ERDGenerator service."""

import pytest
import httpx
import respx

from dictionary_service.services.aggregator import DictionaryAggregator
from dictionary_service.services.erd_generator import ERDGenerator
from dictionary_service.config import settings


class TestERDGenerator:
    @respx.mock
    @pytest.mark.asyncio
    async def test_generate_mermaid(self, sample_contracts_response):
        """Test generating Mermaid ERD syntax."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            erd_generator = ERDGenerator(aggregator)
            mermaid = await erd_generator.generate_mermaid()

            # Check for ERD diagram declaration
            assert "erDiagram" in mermaid

            # Check for dataset entities
            assert "orders" in mermaid
            assert "customers" in mermaid

            # Check for field definitions
            assert "order_id" in mermaid
            assert "customer_id" in mermaid

            # Check for PK/FK markers
            assert "PK" in mermaid
            assert "FK" in mermaid

            # Check for relationship
            assert "}o--||" in mermaid  # Many-to-one relationship
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_generate_mermaid_with_team_filter(self, sample_contracts_response):
        """Test generating Mermaid ERD with team filter."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            erd_generator = ERDGenerator(aggregator)
            mermaid = await erd_generator.generate_mermaid(team="commerce")

            # Should include orders (commerce team)
            assert "orders" in mermaid

            # Should not include customers (crm team)
            assert "customers {" not in mermaid
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_generate_json(self, sample_contracts_response):
        """Test generating JSON ERD structure."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        # Mock individual contract details for subscriber lookup
        for contract in sample_contracts_response["contracts"]:
            respx.get(
                f"{settings.contract_service_url}/api/v1/contracts/name/{contract['name']}"
            ).mock(return_value=httpx.Response(200, json=contract))

        aggregator = DictionaryAggregator()
        try:
            erd_generator = ERDGenerator(aggregator)
            erd_json = await erd_generator.generate_json()

            # Check structure
            assert "nodes" in erd_json
            assert "edges" in erd_json
            assert "metadata" in erd_json

            # Check nodes
            assert len(erd_json["nodes"]) == 3
            node_ids = {n["id"] for n in erd_json["nodes"]}
            assert "orders" in node_ids
            assert "customers" in node_ids

            # Check edges
            fk_edges = [e for e in erd_json["edges"] if e["type"] == "foreign_key"]
            assert len(fk_edges) >= 1

            # Check node structure
            orders_node = next(n for n in erd_json["nodes"] if n["id"] == "orders")
            assert orders_node["publisher_team"] == "commerce"
            assert len(orders_node["fields"]) == 4
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_generate_json_without_subscribers(self, sample_contracts_response):
        """Test generating JSON ERD without subscriber edges."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            erd_generator = ERDGenerator(aggregator)
            erd_json = await erd_generator.generate_json(include_subscribers=False)

            # Should only have foreign key edges, no subscription edges
            sub_edges = [e for e in erd_json["edges"] if e["type"] == "subscription"]
            assert len(sub_edges) == 0
        finally:
            await aggregator.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_generate_plantuml(self, sample_contracts_response):
        """Test generating PlantUML ERD syntax."""
        respx.get(f"{settings.contract_service_url}/api/v1/contracts").mock(
            return_value=httpx.Response(200, json=sample_contracts_response)
        )

        aggregator = DictionaryAggregator()
        try:
            erd_generator = ERDGenerator(aggregator)
            plantuml = await erd_generator.generate_plantuml()

            # Check for PlantUML markers
            assert "@startuml" in plantuml
            assert "@enduml" in plantuml

            # Check for entity definitions
            assert "entity" in plantuml
            assert "orders" in plantuml
            assert "customers" in plantuml

            # Check for field definitions
            assert "order_id" in plantuml
            assert "uuid" in plantuml
        finally:
            await aggregator.close()

    def test_sanitize_name(self):
        """Test name sanitization for diagram syntax."""
        aggregator = DictionaryAggregator()
        erd_generator = ERDGenerator(aggregator)

        assert erd_generator._sanitize_name("my-dataset") == "my_dataset"
        assert erd_generator._sanitize_name("my dataset") == "my_dataset"
        assert erd_generator._sanitize_name("my.dataset") == "my_dataset"

    def test_map_type(self):
        """Test type mapping for ERD display."""
        aggregator = DictionaryAggregator()
        erd_generator = ERDGenerator(aggregator)

        assert erd_generator._map_type("string") == "string"
        assert erd_generator._map_type("integer") == "int"
        assert erd_generator._map_type("boolean") == "bool"
        assert erd_generator._map_type("unknown") == "unknown"
