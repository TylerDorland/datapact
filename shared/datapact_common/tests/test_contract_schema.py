"""Tests for contract schema Pydantic models."""

import pytest
from pydantic import ValidationError

from datapact_common import (
    ContractDefinition,
    ContractField,
    DataType,
    Publisher,
    QualityMetric,
    MetricType,
)


class TestContractField:
    def test_valid_field(self):
        field = ContractField(
            name="user_id",
            data_type=DataType.UUID,
            description="Unique user identifier",
            nullable=False,
            is_primary_key=True,
        )
        assert field.name == "user_id"
        assert field.data_type == DataType.UUID
        assert field.nullable is False

    def test_field_with_constraints(self):
        field = ContractField(
            name="age",
            data_type=DataType.INTEGER,
            constraints=[
                {"type": "min", "value": 0, "message": "Age must be positive"},
                {"type": "max", "value": 150, "message": "Age must be reasonable"},
            ],
        )
        assert len(field.constraints) == 2

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError):
            ContractField(name="", data_type=DataType.STRING)


class TestContractDefinition:
    def test_valid_contract(self):
        contract = ContractDefinition(
            name="user_data",
            version="1.0.0",
            description="User data contract",
            publisher=Publisher(team="platform", owner="user-service"),
            schema=[
                ContractField(name="id", data_type=DataType.UUID),
                ContractField(name="email", data_type=DataType.STRING),
            ],
        )
        assert contract.name == "user_data"
        assert contract.version == "1.0.0"
        assert len(contract.schema_fields) == 2

    def test_invalid_name_pattern(self):
        with pytest.raises(ValidationError):
            ContractDefinition(
                name="Invalid-Name",  # uppercase and hyphen not allowed
                version="1.0.0",
                publisher=Publisher(team="test", owner="test"),
                schema=[ContractField(name="id", data_type=DataType.UUID)],
            )

    def test_invalid_version_format(self):
        with pytest.raises(ValidationError):
            ContractDefinition(
                name="test_data",
                version="1.0",  # must be semver
                publisher=Publisher(team="test", owner="test"),
                schema=[ContractField(name="id", data_type=DataType.UUID)],
            )

    def test_contract_with_quality_metrics(self):
        contract = ContractDefinition(
            name="orders",
            version="1.0.0",
            publisher=Publisher(team="commerce", owner="orders-service"),
            schema=[ContractField(name="order_id", data_type=DataType.UUID)],
            quality=[
                QualityMetric(metric_type=MetricType.FRESHNESS, threshold="15 minutes"),
                QualityMetric(metric_type=MetricType.COMPLETENESS, threshold="99.5%"),
            ],
        )
        assert len(contract.quality) == 2


class TestQualityMetric:
    def test_valid_metric(self):
        metric = QualityMetric(
            metric_type=MetricType.FRESHNESS,
            threshold="15 minutes",
            measurement_method="MAX(updated_at) - NOW()",
            alert_on_breach=True,
        )
        assert metric.metric_type == MetricType.FRESHNESS
        assert metric.threshold == "15 minutes"
