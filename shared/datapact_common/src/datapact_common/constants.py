"""Shared constants for DataPact."""

# API versioning
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Contract statuses
CONTRACT_STATUS_ACTIVE = "active"
CONTRACT_STATUS_DEPRECATED = "deprecated"
CONTRACT_STATUS_DRAFT = "draft"

VALID_CONTRACT_STATUSES = [
    CONTRACT_STATUS_ACTIVE,
    CONTRACT_STATUS_DEPRECATED,
    CONTRACT_STATUS_DRAFT,
]

# Compliance check statuses
CHECK_STATUS_PASS = "pass"
CHECK_STATUS_FAIL = "fail"
CHECK_STATUS_WARNING = "warning"
CHECK_STATUS_ERROR = "error"

# Check types
CHECK_TYPE_SCHEMA = "schema"
CHECK_TYPE_FRESHNESS = "freshness"
CHECK_TYPE_COMPLETENESS = "completeness"
CHECK_TYPE_AVAILABILITY = "availability"

# Default pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# Service names
SERVICE_CONTRACT = "contract-service"
SERVICE_COMPLIANCE = "compliance-monitor"
SERVICE_DICTIONARY = "dictionary-service"
SERVICE_NOTIFICATION = "notification-service"
