"""Tests for YAML parser utility."""

import pytest

from contract_service.utils.yaml_parser import (
    parse_contract_yaml,
    contract_to_yaml,
    ContractParseError,
)


class TestParseContractYaml:
    def test_parse_basic_contract(self):
        """Test parsing a basic contract YAML."""
        yaml_content = """
name: orders
version: 1.0.0
description: Order data
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: order_id
    type: uuid
    nullable: false
    primary_key: true
  - name: total
    type: decimal
"""
        result = parse_contract_yaml(yaml_content)

        assert result["name"] == "orders"
        assert result["version"] == "1.0.0"
        assert result["description"] == "Order data"
        assert result["publisher_team"] == "commerce"
        assert result["publisher_owner"] == "orders-service"
        assert len(result["fields"]) == 2

        # Check first field
        order_id_field = result["fields"][0]
        assert order_id_field["name"] == "order_id"
        assert order_id_field["data_type"] == "uuid"
        assert order_id_field["nullable"] is False
        assert order_id_field["is_primary_key"] is True

    def test_parse_contract_with_quality_metrics(self):
        """Test parsing contract with quality metrics."""
        yaml_content = """
name: orders
version: 1.0.0
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: id
    type: uuid
quality:
  - type: freshness
    threshold: 15 minutes
  - type: completeness
    threshold: 99.5%
    alert_on_breach: true
"""
        result = parse_contract_yaml(yaml_content)

        assert len(result["quality_metrics"]) == 2
        assert result["quality_metrics"][0]["metric_type"] == "freshness"
        assert result["quality_metrics"][0]["threshold"] == "15 minutes"
        assert result["quality_metrics"][1]["metric_type"] == "completeness"
        assert result["quality_metrics"][1]["alert_on_breach"] is True

    def test_parse_contract_with_access_config(self):
        """Test parsing contract with access configuration."""
        yaml_content = """
name: orders
version: 1.0.0
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: id
    type: uuid
access:
  endpoint: http://orders-service:8000
  methods:
    - GET
    - POST
  auth: api_key
  scopes:
    - read:orders
  rate_limit: 1000 req/min
"""
        result = parse_contract_yaml(yaml_content)

        assert "access_config" in result
        access = result["access_config"]
        assert access["endpoint_url"] == "http://orders-service:8000"
        assert access["methods"] == ["GET", "POST"]
        assert access["auth_type"] == "api_key"
        assert access["required_scopes"] == ["read:orders"]
        assert access["rate_limit"] == "1000 req/min"

    def test_parse_contract_with_subscribers(self):
        """Test parsing contract with subscribers."""
        yaml_content = """
name: orders
version: 1.0.0
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: id
    type: uuid
subscribers:
  - team: analytics
    use_case: Sales reporting
    fields:
      - id
      - total
  - team: marketing
    email: marketing@example.com
"""
        result = parse_contract_yaml(yaml_content)

        assert len(result["subscribers"]) == 2
        assert result["subscribers"][0]["team"] == "analytics"
        assert result["subscribers"][0]["use_case"] == "Sales reporting"
        assert result["subscribers"][0]["fields_used"] == ["id", "total"]
        assert result["subscribers"][1]["contact_email"] == "marketing@example.com"

    def test_parse_contract_with_pii_fields(self):
        """Test parsing contract with PII field markers."""
        yaml_content = """
name: customers
version: 1.0.0
publisher:
  team: crm
  owner: customer-service
schema:
  - name: id
    type: uuid
  - name: email
    type: string
    pii: true
  - name: ssn
    type: string
    pii: true
    nullable: false
"""
        result = parse_contract_yaml(yaml_content)

        assert result["fields"][0]["is_pii"] is False
        assert result["fields"][1]["is_pii"] is True
        assert result["fields"][2]["is_pii"] is True

    def test_parse_contract_with_foreign_keys(self):
        """Test parsing contract with foreign key references."""
        yaml_content = """
name: orders
version: 1.0.0
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: order_id
    type: uuid
    primary_key: true
  - name: customer_id
    type: uuid
    foreign_key: true
    references: customers.customer_id
"""
        result = parse_contract_yaml(yaml_content)

        customer_id = result["fields"][1]
        assert customer_id["is_foreign_key"] is True
        assert customer_id["foreign_key_reference"] == "customers.customer_id"

    def test_parse_contract_with_tags(self):
        """Test parsing contract with tags."""
        yaml_content = """
name: orders
version: 1.0.0
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: id
    type: uuid
tags:
  - ecommerce
  - transactions
  - core-data
"""
        result = parse_contract_yaml(yaml_content)

        assert result["tags"] == ["ecommerce", "transactions", "core-data"]

    def test_parse_invalid_yaml(self):
        """Test that invalid YAML raises error."""
        invalid_yaml = """
name: orders
  invalid indent
    more invalid
"""
        with pytest.raises(ContractParseError) as exc_info:
            parse_contract_yaml(invalid_yaml)

        assert "Invalid YAML" in str(exc_info.value)

    def test_parse_non_dict_yaml(self):
        """Test that non-dict YAML raises error."""
        list_yaml = """
- item1
- item2
"""
        with pytest.raises(ContractParseError) as exc_info:
            parse_contract_yaml(list_yaml)

        assert "must be a YAML object" in str(exc_info.value)

    def test_parse_alternate_field_names(self):
        """Test parsing with alternate field names (data_type vs type)."""
        yaml_content = """
name: orders
version: 1.0.0
publisher:
  team: commerce
  owner: orders-service
fields:
  - name: id
    data_type: uuid
    is_primary_key: true
    is_pii: false
"""
        result = parse_contract_yaml(yaml_content)

        assert result["fields"][0]["data_type"] == "uuid"
        assert result["fields"][0]["is_primary_key"] is True


class TestContractToYaml:
    def test_basic_contract_to_yaml(self):
        """Test converting a basic contract to YAML."""
        contract = {
            "name": "orders",
            "version": "1.0.0",
            "description": "Order data",
            "publisher_team": "commerce",
            "publisher_owner": "orders-service",
            "fields": [
                {
                    "name": "order_id",
                    "data_type": "uuid",
                    "nullable": False,
                    "is_primary_key": True,
                },
            ],
        }

        yaml_str = contract_to_yaml(contract)

        assert "name: orders" in yaml_str
        assert "version: 1.0.0" in yaml_str
        assert "team: commerce" in yaml_str

    def test_roundtrip_conversion(self):
        """Test that YAML -> dict -> YAML preserves data."""
        original_yaml = """
name: orders
version: 1.0.0
description: Order data
publisher:
  team: commerce
  owner: orders-service
schema:
  - name: order_id
    type: uuid
    nullable: false
    primary_key: true
quality:
  - type: freshness
    threshold: 15 minutes
tags:
  - ecommerce
"""
        # Parse to dict
        contract_dict = parse_contract_yaml(original_yaml)

        # Convert back to YAML
        converted_yaml = contract_to_yaml(contract_dict)

        # Parse the converted YAML
        reparsed = parse_contract_yaml(converted_yaml)

        # Check key fields match
        assert reparsed["name"] == contract_dict["name"]
        assert reparsed["version"] == contract_dict["version"]
        assert reparsed["publisher_team"] == contract_dict["publisher_team"]
        assert len(reparsed["fields"]) == len(contract_dict["fields"])
