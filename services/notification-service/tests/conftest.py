"""Test configuration and fixtures."""

import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from notification_service.database import get_session
from notification_service.main import app
from notification_service.models.base import Base
from notification_service.models.notification import (
    Notification,
    NotificationPreference,
    NotificationStatus,
)
from notification_service.models.watcher import Watcher


# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_notification_data():
    """Sample notification data."""
    return {
        "event_type": "schema_drift",
        "event_id": f"event-{uuid4()}",
        "contract_id": uuid4(),
        "contract_name": "test_dataset",
        "recipient_email": "user@example.com",
        "recipient_team": "data-team",
        "subject": "Schema Drift Detected: test_dataset",
        "body_html": "<p>Schema drift detected</p>",
        "body_text": "Schema drift detected",
        "channel": "email",
        "status": NotificationStatus.PENDING,
    }


@pytest.fixture
def sample_schema_drift_event():
    """Sample schema drift event data."""
    return {
        "event_type": "schema_drift",
        "event_id": f"drift-{uuid4()}",
        "contract_name": "test_dataset",
        "contract_version": "1.0.0",
        "publisher_team": "data-team",
        "contact_email": "owner@example.com",
        "errors": ["Field 'user_id' type mismatch: expected uuid, got string"],
        "warnings": [],
        "missing_fields": [],
        "extra_fields": ["new_field"],
    }


@pytest.fixture
def sample_quality_breach_event():
    """Sample quality breach event data."""
    return {
        "event_type": "quality_breach",
        "event_id": f"breach-{uuid4()}",
        "contract_name": "test_dataset",
        "contract_version": "1.0.0",
        "publisher_team": "data-team",
        "metric_type": "freshness",
        "threshold": "24h",
        "actual_value": "48h",
        "is_critical": True,
        "failed_checks": [
            {"metric_type": "freshness", "message": "Data is stale", "actual_value": "48h"}
        ],
    }


@pytest_asyncio.fixture
async def sample_notification(test_session: AsyncSession, sample_notification_data):
    """Create a sample notification in the database."""
    notification = Notification(**sample_notification_data)
    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)
    return notification


@pytest_asyncio.fixture
async def sample_preference(test_session: AsyncSession):
    """Create sample notification preferences."""
    preference = NotificationPreference(
        email="user@example.com",
        team="data-team",
        email_enabled=True,
        schema_drift_enabled=True,
        quality_breach_enabled=True,
    )
    test_session.add(preference)
    await test_session.commit()
    await test_session.refresh(preference)
    return preference


@pytest_asyncio.fixture
async def sample_watcher(test_session: AsyncSession):
    """Create a sample watcher."""
    watcher = Watcher(
        contract_id=uuid4(),
        watcher_email="watcher@example.com",
        watcher_team="analytics-team",
        watch_schema_drift=True,
        watch_quality_breach=True,
    )
    test_session.add(watcher)
    await test_session.commit()
    await test_session.refresh(watcher)
    return watcher
