"""Custom exceptions for DataPact."""


class DataPactError(Exception):
    """Base exception for all DataPact errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ContractNotFoundError(DataPactError):
    """Raised when a contract is not found."""

    def __init__(self, contract_id: str | None = None, contract_name: str | None = None):
        identifier = contract_id or contract_name or "unknown"
        super().__init__(f"Contract not found: {identifier}")
        self.contract_id = contract_id
        self.contract_name = contract_name


class ContractValidationError(DataPactError):
    """Raised when contract validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message, details={"errors": errors or []})
        self.errors = errors or []


class SchemaValidationError(DataPactError):
    """Raised when schema validation fails."""

    def __init__(self, message: str, field_errors: dict[str, str] | None = None):
        super().__init__(message, details={"field_errors": field_errors or {}})
        self.field_errors = field_errors or {}


class ComplianceCheckError(DataPactError):
    """Raised when a compliance check fails."""

    def __init__(self, contract_name: str, check_type: str, message: str):
        super().__init__(
            f"Compliance check failed for {contract_name} ({check_type}): {message}"
        )
        self.contract_name = contract_name
        self.check_type = check_type
