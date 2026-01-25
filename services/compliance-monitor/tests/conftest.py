"""Pytest fixtures for Compliance Monitor tests."""

import pytest


@pytest.fixture
def sample_contract_data():
    """Sample contract data as returned by Contract Service."""
    return {
        "id": "12345678-1234-1234-1234-123456789012",
        "name": "test_orders",
        "version": "1.0.0",
        "description": "Test orders dataset",
        "status": "active",
        "publisher_team": "commerce",
        "publisher_owner": "orders-service",
        "contact_email": "orders@example.com",
        "fields": [
            {
                "name": "order_id",
                "data_type": "uuid",
                "nullable": False,
                "is_primary_key": True,
            },
            {
                "name": "total",
                "data_type": "decimal",
                "nullable": False,
            },
            {
                "name": "status",
                "data_type": "string",
                "nullable": False,
            },
        ],
        "quality_metrics": [
            {
                "metric_type": "freshness",
                "threshold": "15 minutes",
                "alert_on_breach": True,
            },
            {
                "metric_type": "completeness",
                "threshold": "99.5%",
                "alert_on_breach": True,
            },
        ],
        "access_config": {
            "endpoint_url": "http://orders-service:8000",
            "methods": ["GET"],
            "auth_type": "none",
        },
    }


@pytest.fixture
def sample_schema_response():
    """Sample schema response from a data service."""
    return {
        "service": "orders-service",
        "contract_name": "test_orders",
        "tables": {
            "orders": {
                "columns": [
                    {"name": "order_id", "type": "uuid", "nullable": False, "primary_key": True},
                    {"name": "total", "type": "numeric(10,2)", "nullable": False},
                    {"name": "status", "type": "varchar(50)", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                ],
                "foreign_keys": [],
            }
        },
    }


@pytest.fixture
def sample_metrics_response():
    """Sample metrics response from a data service."""
    return {
        "timestamp": "2024-01-01T12:00:00Z",
        "freshness": {
            "last_update": "2024-01-01T11:55:00Z",
            "seconds_since_update": 300,
            "is_fresh": True,
        },
        "completeness": {
            "total_rows": 1000,
            "field_completeness": {
                "order_id": 100.0,
                "total": 100.0,
                "status": 99.8,
            },
            "overall_completeness": 99.93,
        },
        "row_count": 1000,
        "availability": {
            "status": "up",
            "uptime_percentage": 99.9,
        },
    }


@pytest.fixture
def sample_health_response():
    """Sample health response from a data service."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T12:00:00Z",
        "service": "orders-service",
    }
