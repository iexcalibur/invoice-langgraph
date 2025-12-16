"""
Pytest configuration and fixtures for Invoice LangGraph Agent tests.
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.config import get_settings, Settings
from app.bigtool import BigtoolPicker, ToolRegistry
from app.mcp import MCPRouter


# ============================================
# EVENT LOOP FIXTURE
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================
# TEST DATABASE
# ============================================

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def override_get_db(test_db_session):
    """Override get_db dependency for tests."""
    async def _override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# ============================================
# TEST CLIENT
# ============================================

@pytest.fixture
def client(override_get_db) -> Generator[TestClient, None, None]:
    """Create test client with database override."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def async_client(override_get_db):
    """Create async test client."""
    from httpx import AsyncClient, ASGITransport
    
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ============================================
# SAMPLE DATA FIXTURES
# ============================================

@pytest.fixture
def sample_invoice_payload() -> dict:
    """Sample invoice payload for testing."""
    return {
        "invoice_id": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "vendor_tax_id": "12-3456789",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-14",
        "amount": 15000.00,
        "currency": "USD",
        "line_items": [
            {
                "desc": "Widget A",
                "qty": 100,
                "unit_price": 100.00,
                "total": 10000.00,
            },
            {
                "desc": "Widget B",
                "qty": 50,
                "unit_price": 100.00,
                "total": 5000.00,
            },
        ],
        "attachments": ["invoice.pdf"],
    }


@pytest.fixture
def sample_invoice_matched(sample_invoice_payload) -> dict:
    """Invoice that should match (for happy path testing)."""
    return sample_invoice_payload


@pytest.fixture
def sample_invoice_failed() -> dict:
    """Invoice that should fail matching (for HITL path testing)."""
    return {
        "invoice_id": "INV-2024-002",
        "vendor_name": "Unknown Vendor LLC",
        "vendor_tax_id": "",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-14",
        "amount": 99999.99,  # High amount, won't match any PO
        "currency": "USD",
        "line_items": [
            {
                "desc": "Mysterious Item",
                "qty": 1,
                "unit_price": 99999.99,
                "total": 99999.99,
            },
        ],
        "attachments": [],
    }


# ============================================
# BIGTOOL FIXTURES
# ============================================

@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create fresh tool registry for testing."""
    registry = ToolRegistry()
    registry.initialize_default_tools()
    return registry


@pytest.fixture
def bigtool_picker(tool_registry) -> BigtoolPicker:
    """Create bigtool picker for testing."""
    return BigtoolPicker(registry=tool_registry)


# ============================================
# MCP FIXTURES
# ============================================

@pytest.fixture
def mcp_router() -> MCPRouter:
    """Create MCP router for testing."""
    return MCPRouter()


# ============================================
# MOCK FIXTURES
# ============================================

@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        app_name="Test Invoice Agent",
        app_env="testing",
        debug=True,
        database_url=TEST_DATABASE_URL,
        match_threshold=0.90,
        two_way_tolerance_pct=5.0,
    )


@pytest.fixture
def mock_workflow_state() -> dict:
    """Create mock workflow state for testing."""
    return {
        "workflow_id": "wf_test_001",
        "invoice_id": "INV-2024-001",
        "status": "RUNNING",
        "current_stage": "INTAKE",
        "raw_payload": {
            "invoice_id": "INV-2024-001",
            "vendor_name": "Test Vendor",
            "amount": 10000.00,
            "currency": "USD",
            "line_items": [],
            "attachments": [],
        },
    }


# ============================================
# UTILITY FIXTURES
# ============================================

@pytest.fixture
def freeze_time():
    """Fixture to freeze time for consistent testing."""
    from unittest.mock import patch
    
    frozen_time = datetime(2024, 1, 15, 10, 30, 0)
    
    with patch("app.utils.helpers.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = frozen_time
        mock_datetime.now.return_value = frozen_time
        yield frozen_time

