"""
Integration tests for API wiring — verifies end-to-end connectivity
between API endpoints, Guide agent, and MemoryStore.

These tests use FastAPI's TestClient and live database where available.
Tests requiring ANTHROPIC_API_KEY are skipped if the key is not set.
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.api.main import app, settings  # noqa: E402

# Markers
requires_db = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping DB-dependent test",
)
requires_api_key = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping LLM-dependent test",
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    with TestClient(app) as c:
        yield c


# ============================================================================
# Health & Lifecycle Tests
# ============================================================================


class TestLifecycle:
    """Test application lifecycle and health checks."""

    def test_health_check(self, client):
        """GET /health returns 200 with status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """GET / returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == settings.app_name
        assert "version" in data
        assert data["docs"] == "/docs"


# ============================================================================
# Chat Endpoint Tests
# ============================================================================


class TestChatEndpoint:
    """Test /api/v1/chat endpoint wiring."""

    def test_chat_without_api_key(self, client):
        """POST /api/v1/chat without ANTHROPIC_API_KEY returns helpful message."""
        # Ensure no API key is set for this test
        with patch.object(settings, "anthropic_api_key", ""):
            response = client.post(
                "/api/v1/chat",
                json={"message": "What is my moon sign?"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "ANTHROPIC_API_KEY" in data["response"]
        assert data["metadata"]["status"] == "no_api_key"
        assert data["metadata"]["agent_available"] is False

    def test_chat_without_user_id(self, client):
        """POST /api/v1/chat without user_id still works."""
        with patch.object(settings, "anthropic_api_key", ""):
            response = client.post(
                "/api/v1/chat",
                json={"message": "Hello"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] is None

    def test_chat_with_user_id(self, client):
        """POST /api/v1/chat with user_id passes it through."""
        with patch.object(settings, "anthropic_api_key", ""):
            response = client.post(
                "/api/v1/chat",
                json={"message": "Hello", "user_id": "test-user-123"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user-123"

    @requires_api_key
    def test_chat_with_api_key(self, client):
        """POST /api/v1/chat with ANTHROPIC_API_KEY returns agent response."""
        response = client.post(
            "/api/v1/chat",
            json={"message": "What is Vedic astrology?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["agent_available"] is True
        assert data["metadata"]["status"] == "ok"
        assert len(data["response"]) > 0
        assert "intent" in data["metadata"]


# ============================================================================
# User Endpoint Tests
# ============================================================================


class TestUserEndpoints:
    """Test /api/v1/users endpoints."""

    def test_get_user_no_db(self, client):
        """GET /api/v1/users/{id} without DB returns 503."""
        # When memory_store is None (no DATABASE_URL), should return 503
        with patch.object(app.state, "memory_store", None):
            response = client.get("/api/v1/users/some-id")

        assert response.status_code == 503

    def test_create_user_no_db(self, client):
        """POST /api/v1/users without DB returns 503."""
        with patch.object(app.state, "memory_store", None):
            response = client.post(
                "/api/v1/users",
                json={
                    "email": "test@example.com",
                    "birth_datetime": "1992-12-03T03:00:00",
                    "latitude": 16.726,
                    "longitude": 81.288,
                    "timezone_offset": 5.5,
                },
            )

        assert response.status_code == 503

    def test_get_user_not_found(self, client):
        """GET /api/v1/users/{id} with mock store returns 404 for unknown user."""
        mock_store = AsyncMock()
        mock_store.get_user = AsyncMock(return_value=None)

        with patch.object(app.state, "memory_store", mock_store):
            response = client.get("/api/v1/users/nonexistent-user-id")

        assert response.status_code == 404

    def test_get_user_with_profile(self, client):
        """GET /api/v1/users/{id} returns user + birth_chart + patterns."""
        mock_store = AsyncMock()
        mock_store.get_user = AsyncMock(
            return_value={
                "id": "test-user-id",
                "email": "test@example.com",
                "name": "Test User",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        )
        mock_store.get_birth_chart = AsyncMock(
            return_value={
                "user_id": "test-user-id",
                "chart_data": {"lagna_rashi": "Libra"},
            }
        )
        mock_store.get_user_patterns = AsyncMock(return_value=[])

        with patch.object(app.state, "memory_store", mock_store):
            response = client.get("/api/v1/users/test-user-id")

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == "test-user-id"
        assert data["birth_chart"] is not None
        assert isinstance(data["patterns"], list)

    def test_create_user_returns_chart(self, client):
        """POST /api/v1/users calculates chart and returns summary."""
        mock_store = AsyncMock()
        mock_store.create_user = AsyncMock(
            return_value={
                "id": "new-user-id",
                "email": "new@example.com",
                "name": "New User",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        )
        mock_store.save_birth_chart = AsyncMock(return_value={"id": "chart-1"})

        with patch.object(app.state, "memory_store", mock_store):
            response = client.post(
                "/api/v1/users",
                json={
                    "email": "new@example.com",
                    "name": "New User",
                    "birth_datetime": "1992-12-03T03:00:00",
                    "latitude": 16.726239,
                    "longitude": 81.288428,
                    "timezone_offset": 5.5,
                    "timezone": "Asia/Kolkata",
                    "ayanamsa": "lahiri",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "new-user-id"
        assert "chart_summary" in data
        assert "lagna_rashi" in data["chart_summary"]
        assert "moon_rashi" in data["chart_summary"]
        assert "moon_nakshatra" in data["chart_summary"]
        assert data["chart_summary"]["planet_count"] == 9  # 9 Vedic planets

        # Verify store methods were called
        mock_store.create_user.assert_called_once_with(email="new@example.com", name="New User")
        mock_store.save_birth_chart.assert_called_once()


# ============================================================================
# Existing Chart Endpoints Still Work
# ============================================================================


class TestChartEndpointsIntact:
    """Verify existing chart endpoints still work after wiring."""

    def test_chart_calculation(self, client):
        """POST /api/v1/chart still returns chart data."""
        response = client.post(
            "/api/v1/chart",
            json={
                "datetime": "1992-12-03T03:00:00",
                "latitude": 16.726239,
                "longitude": 81.288428,
                "timezone_offset": 5.5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "planets" in data
        assert "ascendant" in data
        assert "moon_nakshatra" in data

    def test_timing_dasha(self, client):
        """POST /api/v1/timing/dasha still returns dasha data."""
        response = client.post(
            "/api/v1/timing/dasha",
            json={
                "datetime": "1992-12-03T03:00:00",
                "latitude": 16.726239,
                "longitude": 81.288428,
                "timezone_offset": 5.5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "current" in data
        assert "mahadasha_sequence" in data
