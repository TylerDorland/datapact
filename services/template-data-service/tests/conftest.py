"""Pytest fixtures for Template Data Service tests."""

import asyncio
from collections.abc import AsyncGenerator
from decimal import Decimal
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data_service.main import app
from data_service.models import Base, ExampleData
from data_service.database import get_db


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
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for test setup."""
    async with async_session_maker() as session:
        yield session
        await session.commit()


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Sample data entry for tests."""
    return {
        "name": "Test Item",
        "description": "A test data entry",
        "value": "99.99",
        "category": "test",
        "is_active": True,
    }


@pytest.fixture
async def seeded_data(db_session: AsyncSession) -> list[ExampleData]:
    """Seed the database with test data."""
    entries = [
        ExampleData(
            name=f"Item {i}",
            description=f"Description {i}",
            value=Decimal(f"{i * 10}.00"),
            category="category_a" if i % 2 == 0 else "category_b",
            is_active=i < 3,
        )
        for i in range(5)
    ]
    for entry in entries:
        db_session.add(entry)
    await db_session.flush()
    return entries
