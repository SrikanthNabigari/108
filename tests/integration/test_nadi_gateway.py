"""Integration tests for Nadi gateway endpoints."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from gateway.main import app  # noqa: E402


@pytest.fixture
def client():
    """Create a FastAPI test client for gateway."""
    with TestClient(app) as c:
        yield c


USER_PLANETS = {
    "sun": {"longitude": 227.2154, "rashi": "scorpio", "house": 2},
    "moon": {"longitude": 324.1124, "rashi": "aquarius", "house": 5},
    "mars": {"longitude": 93.7587, "rashi": "cancer", "house": 10},
    "mercury": {"longitude": 208.6609, "rashi": "libra", "house": 1},
    "jupiter": {"longitude": 166.2399, "rashi": "virgo", "house": 12},
    "venus": {"longitude": 269.3543, "rashi": "sagittarius", "house": 3},
    "saturn": {"longitude": 289.9336, "rashi": "capricorn", "house": 4},
    "rahu": {"longitude": 238.2083, "rashi": "scorpio", "house": 2},
    "ketu": {"longitude": 58.2083, "rashi": "taurus", "house": 8},
}


class TestCKNEndpoint:
    """Tests for Chandra Kala Nadi endpoint."""

    def test_ckn_returns_success(self, client):
        """Test CKN endpoint returns success with valid data."""
        resp = client.post(
            "/api/v1/nadi/chandra-kala-nadi",
            json={
                "natal_planets": USER_PLANETS,
                "current_jupiter_sign": "gemini",
                "moon_rashi": "aquarius",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "conjunctions" in data

    def test_ckn_detects_sun_rahu_conjunction(self, client):
        """Test CKN detects Sun-Rahu conjunction in Scorpio."""
        resp = client.post(
            "/api/v1/nadi/chandra-kala-nadi",
            json={
                "natal_planets": USER_PLANETS,
                "current_jupiter_sign": "gemini",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        conj_signs = [c["sign"] for c in data.get("conjunctions", [])]
        assert "Scorpio" in conj_signs

    def test_ckn_without_moon_rashi(self, client):
        """Test CKN works without moon_rashi parameter."""
        resp = client.post(
            "/api/v1/nadi/chandra-kala-nadi",
            json={
                "natal_planets": USER_PLANETS,
                "current_jupiter_sign": "gemini",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["moon_analysis"] is None

    def test_ckn_invalid_jupiter_sign(self, client):
        """Test CKN handles invalid Jupiter sign gracefully."""
        resp = client.post(
            "/api/v1/nadi/chandra-kala-nadi",
            json={
                "natal_planets": USER_PLANETS,
                "current_jupiter_sign": "invalid_sign",
            },
        )
        assert resp.status_code == 200  # Should not fail, just handle gracefully


class TestNadiAmshaEndpoint:
    """Tests for Nadi Amsha (D-150) endpoint."""

    def test_nadi_amsha_returns_success(self, client):
        """Test Nadi Amsha endpoint returns success with valid data."""
        resp = client.post(
            "/api/v1/nadi/nadi-amsha",
            json={
                "natal_planets": USER_PLANETS,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "planet_positions" in data
        assert "dominant_nadi" in data

    def test_nadi_amsha_with_lagna(self, client):
        """Test Nadi Amsha with lagna longitude."""
        resp = client.post(
            "/api/v1/nadi/nadi-amsha",
            json={
                "natal_planets": USER_PLANETS,
                "lagna_longitude": 208.66,  # Libra lagna
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["lagna_position"] is not None
        assert "nadi_amsha_sign" in data["lagna_position"]

    def test_nadi_amsha_moon_analysis(self, client):
        """Test Nadi Amsha includes Moon sublord analysis."""
        resp = client.post(
            "/api/v1/nadi/nadi-amsha",
            json={
                "natal_planets": USER_PLANETS,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["moon_sublord_analysis"] is not None
        assert "moon_sublord" in data["moon_sublord_analysis"]


class TestNadiAmshaPositionEndpoint:
    """Tests for single position Nadi Amsha endpoint."""

    def test_position_calculation(self, client):
        """Test single longitude position calculation."""
        resp = client.get("/api/v1/nadi/nadi-amsha/position?longitude=324.11")
        assert resp.status_code == 200
        data = resp.json()
        assert "amsha_number" in data
        assert "nadi_amsha_sign" in data
        assert "nadi_type" in data
        assert data["nadi_type"] in ["Adi", "Madhya", "Antya"]

    def test_position_at_zero(self, client):
        """Test position calculation at 0 degrees."""
        resp = client.get("/api/v1/nadi/nadi-amsha/position?longitude=0")
        assert resp.status_code == 200
        data = resp.json()
        assert data["natal_sign"] == "Aries"
        assert data["amsha_number"] == 0
        assert data["nadi_type"] == "Adi"

    def test_position_at_boundary(self, client):
        """Test position calculation at sign boundary."""
        resp = client.get("/api/v1/nadi/nadi-amsha/position?longitude=29.99")
        assert resp.status_code == 200
        data = resp.json()
        assert data["natal_sign"] == "Aries"
        assert data["amsha_number"] == 149


class TestKPSublordEndpoint:
    """Tests for KP sublord endpoint."""

    def test_kp_sublord_basic(self, client):
        """Test KP sublord calculation."""
        resp = client.get("/api/v1/nadi/kp-sublord?longitude=324.11&house_num=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "sublord" in data
        assert "nadi_amsha_sign" in data
        assert "house" in data
        assert data["house"] == 5
        assert "kp_interpretation" in data

    def test_kp_sublord_without_house(self, client):
        """Test KP sublord without house number."""
        resp = client.get("/api/v1/nadi/kp-sublord?longitude=324.11")
        assert resp.status_code == 200
        data = resp.json()
        assert "sublord" in data
        assert "house" not in data
        assert "kp_interpretation" not in data

    def test_kp_sublord_various_longitudes(self, client):
        """Test KP sublord for various longitude values."""
        longitudes = [0, 90, 180, 270, 359.99]
        for lon in longitudes:
            resp = client.get(f"/api/v1/nadi/kp-sublord?longitude={lon}")
            assert resp.status_code == 200
            data = resp.json()
            assert "sublord" in data
            assert data["sublord"] in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]


class TestSensitivePointsEndpoint:
    """Tests for Sensitive Points endpoint."""

    def test_sensitive_points_returns_success(self, client):
        """Test sensitive points endpoint returns success with valid data."""
        resp = client.post(
            "/api/v1/nadi/sensitive-points",
            json={
                "natal_planets": USER_PLANETS,
                "lagna_rashi": "libra",
                "lagna_longitude": 180.9,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "bhrigu_bindu" in data
        assert "indu_lagna" in data
        assert "sree_lagna" in data

    def test_bhrigu_bindu_capricorn(self, client):
        """Test Bhrigu Bindu calculation for user's chart."""
        resp = client.post(
            "/api/v1/nadi/sensitive-points",
            json={
                "natal_planets": USER_PLANETS,
                "lagna_rashi": "libra",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["bhrigu_bindu"]["sign"] == "Capricorn"
        assert "longitude" in data["bhrigu_bindu"]
        assert "degree_in_sign" in data["bhrigu_bindu"]

    def test_indu_lagna_gemini(self, client):
        """Test Indu Lagna calculation for user's chart."""
        resp = client.post(
            "/api/v1/nadi/sensitive-points",
            json={
                "natal_planets": USER_PLANETS,
                "lagna_rashi": "libra",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["indu_lagna"]["indu_lagna_sign"] == "Gemini"
        assert "bindu_sum" in data["indu_lagna"]
        assert "wealth_channel" in data["indu_lagna"]
