"""Pytest fixtures for Contract Service tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from contract_service.main import app
from contract_service.models import Base
from contract_service.api.dependencies import get_db


# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """Create tables before each test and drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_contract() -> dict[str, Any]:
    """Sample contract data for tests."""
    return {
        "name": "test_orders",
        "version": "1.0.0",
        "description": "Test orders dataset",
        "publisher": {
            "team": "commerce",
            "owner": "orders-service",
        },
        "schema": [
            {
                "name": "order_id",
                "data_type": "uuid",
                "description": "Unique order identifier",
                "nullable": False,
                "is_primary_key": True,
            },
            {
                "name": "customer_id",
                "data_type": "uuid",
                "description": "Customer reference",
                "nullable": False,
                "is_foreign_key": True,
                "foreign_key_reference": "customers.id",
            },
            {
                "name": "total",
                "data_type": "decimal",
                "description": "Order total",
                "nullable": False,
            },
            {
                "name": "status",
                "data_type": "string",
                "description": "Order status",
                "nullable": False,
            },
        ],
        "quality": [
            {
                "metric_type": "freshness",
                "threshold": "15 minutes",
            },
            {
                "metric_type": "completeness",
                "threshold": "99.5%",
            },
        ],
        "tags": ["orders", "commerce"],
    }


@pytest.fixture
def sample_subscriber() -> dict[str, Any]:
    """Sample subscriber data for tests."""
    return {
        "team": "analytics",
        "use_case": "Order analytics dashboard",
        "fields_used": ["order_id", "total", "status"],
        "contact_email": "analytics@example.com",
    }
