"""Tests for schema validation."""

import pytest

from compliance_monitor.checks.schema_validator import SchemaValidator


@pytest.fixture
def sample_contract():
    """Sample contract data for testing."""
    return {
        "name": "test_dataset",
        "version": "1.0.0",
        "fields": [
            {"name": "id", "data_type": "uuid", "nullable": False},
            {"name": "name", "data_type": "string", "nullable": False},
            {"name": "value", "data_type": "decimal", "nullable": True},
            {"name": "created_at", "data_type": "timestamp", "nullable": False},
        ],
    }


class TestSchemaValidator:
    def test_valid_schema(self, sample_contract):
        """Test that a matching schema passes validation."""
        actual_schema = {
            "tables": {
                "test_table": {
                    "columns": [
                        {"name": "id", "type": "uuid", "nullable": False},
                        {"name": "name", "type": "varchar(255)", "nullable": False},
                        {"name": "value", "type": "numeric(10,2)", "nullable": True},
                        {"name": "created_at", "type": "timestamp with time zone", "nullable": False},
                    ]
                }
            }
        }

        validator = SchemaValidator(sample_contract)
        assert validator.validate(actual_schema) is True
        assert len(validator.errors) == 0

    def test_missing_field(self, sample_contract):
        """Test that missing fields are detected."""
        actual_schema = {
            "tables": {
                "test_table": {
                    "columns": [
                        {"name": "id", "type": "uuid", "nullable": False},
                        {"name": "name", "type": "varchar(255)", "nullable": False},
                        # missing 'value' and 'created_at'
                    ]
                }
            }
        }

        validator = SchemaValidator(sample_contract)
        assert validator.validate(actual_schema) is False
        assert len(validator.errors) == 2
        assert "Missing required field: value" in validator.errors
        assert "Missing required field: created_at" in validator.errors

    def test_type_mismatch(self, sample_contract):
        """Test that type mismatches are detected."""
        actual_schema = {
            "tables": {
                "test_table": {
                    "columns": [
                        {"name": "id", "type": "integer", "nullable": False},  # Wrong type
                        {"name": "name", "type": "varchar(255)", "nullable": False},
                        {"name": "value", "type": "numeric(10,2)", "nullable": True},
                        {"name": "created_at", "type": "timestamp", "nullable": False},
                    ]
                }
            }
        }

        validator = SchemaValidator(sample_contract)
        assert validator.validate(actual_schema) is False
        assert any("Type mismatch" in e and "id" in e for e in validator.errors)

    def test_nullable_mismatch(self, sample_contract):
        """Test that nullable mismatches are detected."""
        actual_schema = {
            "tables": {
                "test_table": {
                    "columns": [
                        {"name": "id", "type": "uuid", "nullable": True},  # Should be NOT NULL
                        {"name": "name", "type": "varchar(255)", "nullable": False},
                        {"name": "value", "type": "numeric(10,2)", "nullable": True},
                        {"name": "created_at", "type": "timestamp", "nullable": False},
                    ]
                }
            }
        }

        validator = SchemaValidator(sample_contract)
        assert validator.validate(actual_schema) is False
        assert any("NOT NULL" in e and "id" in e for e in validator.errors)

    def test_extra_fields_warning(self, sample_contract):
        """Test that extra fields generate warnings, not errors."""
        actual_schema = {
            "tables": {
                "test_table": {
                    "columns": [
                        {"name": "id", "type": "uuid", "nullable": False},
                        {"name": "name", "type": "varchar(255)", "nullable": False},
                        {"name": "value", "type": "numeric(10,2)", "nullable": True},
                        {"name": "created_at", "type": "timestamp", "nullable": False},
                        {"name": "extra_field", "type": "text", "nullable": True},  # Extra field
                    ]
                }
            }
        }

        validator = SchemaValidator(sample_contract)
        assert validator.validate(actual_schema) is True  # Still valid
        assert len(validator.warnings) == 1
        assert "Undocumented field" in validator.warnings[0]

    def test_type_compatibility(self, sample_contract):
        """Test that compatible types are accepted."""
        # Test various string types
        validator = SchemaValidator(sample_contract)
        assert validator._types_compatible("string", "VARCHAR(255)") is True
        assert validator._types_compatible("string", "text") is True
        assert validator._types_compatible("string", "character varying") is True

        # Test various integer types
        assert validator._types_compatible("integer", "int") is True
        assert validator._types_compatible("integer", "bigint") is True
        assert validator._types_compatible("integer", "serial") is True

        # Test incompatible types
        assert validator._types_compatible("uuid", "integer") is False
        assert validator._types_compatible("string", "integer") is False
