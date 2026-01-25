"""Pytest fixtures for Dictionary Service tests."""

import pytest


@pytest.fixture
def sample_contracts_response():
    """Sample contracts response from Contract Service."""
    return {
        "contracts": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "orders",
                "version": "1.0.0",
                "description": "Order data from e-commerce platform",
                "status": "active",
                "publisher_team": "commerce",
                "publisher_owner": "orders-service",
                "contact_email": "commerce@example.com",
                "tags": ["ecommerce", "transactions"],
                "fields": [
                    {
                        "name": "order_id",
                        "data_type": "uuid",
                        "description": "Unique order identifier",
                        "nullable": False,
                        "is_pii": False,
                        "is_primary_key": True,
                        "is_foreign_key": False,
                    },
                    {
                        "name": "customer_id",
                        "data_type": "uuid",
                        "description": "Reference to customer",
                        "nullable": False,
                        "is_pii": False,
                        "is_primary_key": False,
                        "is_foreign_key": True,
                        "foreign_key_reference": "customers.customer_id",
                    },
                    {
                        "name": "total",
                        "data_type": "decimal",
                        "description": "Order total amount",
                        "nullable": False,
                        "is_pii": False,
                    },
                    {
                        "name": "customer_email",
                        "data_type": "string",
                        "description": "Customer email address",
                        "nullable": True,
                        "is_pii": True,
                    },
                ],
                "subscribers": [
                    {"team": "analytics", "use_case": "Sales reporting"},
                    {"team": "marketing", "use_case": "Customer segmentation"},
                ],
                "quality_metrics": [
                    {"metric_type": "freshness", "threshold": "15 minutes"},
                ],
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "name": "customers",
                "version": "2.1.0",
                "description": "Customer master data",
                "status": "active",
                "publisher_team": "crm",
                "publisher_owner": "customer-service",
                "contact_email": "crm@example.com",
                "tags": ["master-data", "customers"],
                "fields": [
                    {
                        "name": "customer_id",
                        "data_type": "uuid",
                        "description": "Unique customer identifier",
                        "nullable": False,
                        "is_pii": False,
                        "is_primary_key": True,
                    },
                    {
                        "name": "email",
                        "data_type": "string",
                        "description": "Customer email",
                        "nullable": False,
                        "is_pii": True,
                    },
                    {
                        "name": "name",
                        "data_type": "string",
                        "description": "Customer full name",
                        "nullable": False,
                        "is_pii": True,
                    },
                    {
                        "name": "created_at",
                        "data_type": "timestamp",
                        "description": "Account creation timestamp",
                        "nullable": False,
                        "is_pii": False,
                    },
                ],
                "subscribers": [
                    {"team": "commerce", "use_case": "Order processing"},
                ],
                "quality_metrics": [],
            },
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "name": "legacy_users",
                "version": "0.9.0",
                "description": "Deprecated user data",
                "status": "deprecated",
                "publisher_team": "platform",
                "publisher_owner": "legacy-service",
                "tags": ["deprecated"],
                "fields": [
                    {
                        "name": "user_id",
                        "data_type": "integer",
                        "nullable": False,
                        "is_primary_key": True,
                    },
                ],
                "subscribers": [],
                "quality_metrics": [],
            },
        ],
        "total": 3,
    }


@pytest.fixture
def sample_dictionary(sample_contracts_response):
    """Sample dictionary built from contracts."""
    return {
        "datasets": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "orders",
                "description": "Order data from e-commerce platform",
                "publisher_team": "commerce",
                "publisher_owner": "orders-service",
                "status": "active",
                "version": "1.0.0",
                "subscriber_count": 2,
                "field_count": 4,
                "tags": ["ecommerce", "transactions"],
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "name": "customers",
                "description": "Customer master data",
                "publisher_team": "crm",
                "publisher_owner": "customer-service",
                "status": "active",
                "version": "2.1.0",
                "subscriber_count": 1,
                "field_count": 4,
                "tags": ["master-data", "customers"],
            },
        ],
        "fields": [
            {"name": "order_id", "dataset": "orders", "data_type": "uuid", "is_pii": False},
            {"name": "customer_id", "dataset": "orders", "data_type": "uuid", "is_pii": False},
            {"name": "total", "dataset": "orders", "data_type": "decimal", "is_pii": False},
            {"name": "customer_email", "dataset": "orders", "data_type": "string", "is_pii": True},
            {"name": "customer_id", "dataset": "customers", "data_type": "uuid", "is_pii": False},
            {"name": "email", "dataset": "customers", "data_type": "string", "is_pii": True},
            {"name": "name", "dataset": "customers", "data_type": "string", "is_pii": True},
            {"name": "created_at", "dataset": "customers", "data_type": "timestamp", "is_pii": False},
        ],
        "teams": ["analytics", "commerce", "crm", "marketing"],
        "pii_fields": [
            {"name": "customer_email", "dataset": "orders", "data_type": "string", "is_pii": True},
            {"name": "email", "dataset": "customers", "data_type": "string", "is_pii": True},
            {"name": "name", "dataset": "customers", "data_type": "string", "is_pii": True},
        ],
        "relationships": [
            {
                "from_dataset": "orders",
                "from_field": "customer_id",
                "to_dataset": "customers",
                "to_field": "customer_id",
                "type": "foreign_key",
            },
        ],
        "summary": {
            "total_datasets": 2,
            "total_fields": 8,
            "total_teams": 4,
            "pii_field_count": 3,
            "relationship_count": 1,
            "active_datasets": 2,
            "deprecated_datasets": 0,
        },
    }
