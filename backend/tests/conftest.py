"""
WoSafe Tests — Configuration & Fixtures
Pytest fixtures for async testing with a test database and HTTP client.
"""

import asyncio
import os
from typing import AsyncGenerator
from uuid import uuid4

# ── Override DB URL BEFORE any app imports ─────
# Ensures session.py picks up SQLite instead of Postgres during testing
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.dependencies import get_db
from app.database.base import Base
from app.main import app

# ── Test Database ──────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
    connect_args={"check_same_thread": False},
)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client with test database."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def user_data() -> dict:
    """Sample user data for tests."""
    return {
        "name": "Test User",
        "email": f"test-{uuid4().hex[:8]}@wosafe.app",
        "phone": "+1234567890",
        "firebase_uid": f"test-uid-{uuid4().hex[:8]}",
        "role": "user",
    }


@pytest.fixture
def journey_data() -> dict:
    """Sample journey data for tests."""
    return {
        "origin_latitude": 40.7128,
        "origin_longitude": -74.0060,
        "dest_latitude": 40.7580,
        "dest_longitude": -73.9855,
        "dest_address": "Times Square, NYC",
        "route_type": "safest",
    }


@pytest.fixture
def incident_data() -> dict:
    """Sample incident data for tests."""
    return {
        "category": "harassment",
        "title": "Suspicious activity on 5th Avenue",
        "description": "A group of individuals making threatening gestures near the subway exit.",
        "severity": "high",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "5th Ave & 23rd St",
        "is_anonymous": False,
    }


@pytest.fixture
def sos_data() -> dict:
    """Sample SOS data for tests."""
    return {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "trigger_type": "sos_button",
        "address": "5th Ave & 23rd St",
    }
