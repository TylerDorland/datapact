"""Schema validation against contract definition."""

from typing import Any


class SchemaValidator:
    """Validates a service's actual schema against its contract."""

    # Type mapping from contract types to database types
    TYPE_MAPPING = {
        "string": ["varchar", "text", "char", "character varying", "character"],
        "integer": ["int", "integer", "bigint", "smallint", "serial", "bigserial", "int4", "int8"],
        "float": ["float", "real", "double precision", "float4", "float8"],
        "decimal": ["decimal", "numeric"],
        "boolean": ["bool", "boolean"],
        "date": ["date"],
        "datetime": ["timestamp", "timestamp without time zone"],
        "timestamp": ["timestamp", "timestamp with time zone", "timestamptz"],
        "uuid": ["uuid"],
        "json": ["json", "jsonb"],
        "array": ["array", "[]"],
    }

    def __init__(self, contract_data: dict[str, Any]):
        """
        Initialize validator with contract data.

        Args:
            contract_data: The contract definition from the Contract Service
        """
        self.contract_data = contract_data
        self.contract_name = contract_data.get("name", "unknown")
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, actual_schema: dict[str, Any]) -> bool:
        """
        Compare actual schema from /schema endpoint against contract.

        Args:
            actual_schema: Schema response from data service /schema endpoint

        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []

        # Get expected fields from contract
        expected_fields = {
            f["name"]: f for f in self.contract_data.get("fields", [])
        }

        # Get actual columns from the schema response
        actual_tables = actual_schema.get("tables", {})

        # Flatten all columns across tables for comparison
        actual_columns = {}
        for table_name, table_info in actual_tables.items():
            for col in table_info.get("columns", []):
                actual_columns[col["name"]] = {
                    **col,
                    "table": table_name,
                }

        # Check for missing fields
        for field_name, field_def in expected_fields.items():
            if field_name not in actual_columns:
                self.errors.append(f"Missing required field: {field_name}")
                continue

            actual_col = actual_columns[field_name]

            # Type checking
            expected_type = field_def.get("data_type", "string")
            actual_type = actual_col.get("type", "")

            if not self._types_compatible(expected_type, actual_type):
                self.errors.append(
                    f"Type mismatch for '{field_name}': "
                    f"expected {expected_type}, got {actual_type}"
                )

            # Nullable checking
            field_nullable = field_def.get("nullable", True)
            col_nullable = actual_col.get("nullable", True)

            if not field_nullable and col_nullable:
                self.errors.append(
                    f"Field '{field_name}' should be NOT NULL but is nullable"
                )

        # Check for extra fields (warning, not error)
        for col_name in actual_columns:
            if col_name not in expected_fields:
                self.warnings.append(f"Undocumented field in schema: {col_name}")

        return len(self.errors) == 0

    def _types_compatible(self, contract_type: str, db_type: str) -> bool:
        """
        Check if database type is compatible with contract type.

        Args:
            contract_type: Type specified in contract (e.g., "string", "uuid")
            db_type: Actual database type (e.g., "VARCHAR(255)", "uuid")

        Returns:
            True if types are compatible
        """
        db_type_lower = db_type.lower()
        expected_types = self.TYPE_MAPPING.get(contract_type, [])

        return any(t in db_type_lower for t in expected_types)

    def get_result(self) -> dict[str, Any]:
        """Return validation result as dict."""
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "contract_name": self.contract_name,
        }
