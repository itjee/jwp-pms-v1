"""
Test Configuration

Pytest fixtures and configuration for testing.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest  # type: ignore
import pytest_asyncio  # type: ignore
from core.config import settings
from core.database import Base, get_async_session
from fastapi.testclient import TestClient  # type: ignore
from main import app
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # type: ignore

# Test database URL (SQLite in memory for fast testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    """
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

        async with TestSessionLocal() as session:
            yield session

        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """
    Override the get_async_session dependency for testing.
    """

    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture
def test_client(override_get_db) -> TestClient:
    """
    Create a test client with database dependency override.
    """
    app.dependency_overrides[get_async_session] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Sample user data for testing.
    """
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123",
        "is_active": True,
    }


@pytest.fixture
def test_project_data():
    """
    Sample project data for testing.
    """
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "status": "planning",
        "priority": "medium",
    }


@pytest.fixture
def test_task_data():
    """
    Sample task data for testing.
    """
    return {
        "title": "Test Task",
        "description": "A test task for unit testing",
        "status": "todo",
        "priority": "medium",
    }


# Test utilities
class TestUtils:
    """
    Utility class for common test operations.
    """

    @staticmethod
    async def create_test_user(db: AsyncSession, user_data: dict):
        """
        Create a test user in the database.
        """
        # TODO: Implement after user model is created
        pass

    @staticmethod
    async def create_test_project(db: AsyncSession, project_data: dict, user_id: int):
        """
        Create a test project in the database.
        """
        # TODO: Implement after project model is created
        pass

    @staticmethod
    async def create_test_task(
        db: AsyncSession, task_data: dict, project_id: int, user_id: int
    ):
        """
        Create a test task in the database.
        """
        # TODO: Implement after task model is created
        pass


@pytest.fixture
def test_utils():
    """
    Provide test utilities.
    """
    return TestUtils


# Pytest configuration
def pytest_configure(config):
    """
    Configure pytest settings.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# Mark async tests
pytest_plugins = ("pytest_asyncio",)
