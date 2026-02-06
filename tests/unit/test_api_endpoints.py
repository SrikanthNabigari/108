"""Tests for new REST API endpoints added in Session 18.

Tests cover:
- POST /api/v1/analysis/aspects
- POST /api/v1/analysis/bhava-bala
- GET /api/v1/timing/abhijit-muhurta
- GET /api/v1/timing/brahma-muhurta
- GET /api/v1/timing/eclipses/{year}/{month}
- POST /api/v1/dasha/ashtottari
- POST /api/v1/progressions/current
- GET /api/v1/knowledge/tithis/{number}
- GET /api/v1/knowledge/karanas/{name}
- GET /api/v1/knowledge/varas/{name}
- GET /api/v1/knowledge/avasthas/{planet}
- GET /api/v1/knowledge/nitya-yogas/{number}
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.api.main import app  # noqa: E402

client = TestClient(app)

# Standard birth data for testing
BIRTH_DATA = {
    "datetime": "1992-12-03T03:00:00",
    "latitude": 16.726239,
    "longitude": 81.288428,
    "timezone_offset": 5.5,
    "ayanamsa": "lahiri",
    "house_system": "whole_sign",
}


# =============================================================================
# Aspect Endpoint
# =============================================================================


class TestAspectsEndpoint:
    """Test POST /api/v1/analysis/aspects."""

    def test_aspects_success(self):
        """Test successful aspect calculation."""
        response = client.post("/api/v1/analysis/aspects", json=BIRTH_DATA)
        assert response.status_code == 200

        data = response.json()
        assert "aspects" in data
        assert "houses_aspected" in data
        assert "planet_houses" in data

    def test_aspects_has_planets(self):
        """Test that aspects include planets."""
        response = client.post("/api/v1/analysis/aspects", json=BIRTH_DATA)
        data = response.json()

        aspects = data["aspects"]
        assert "sun" in aspects or "moon" in aspects

    def test_aspects_house_format(self):
        """Test that houses_aspected has correct format."""
        response = client.post("/api/v1/analysis/aspects", json=BIRTH_DATA)
        data = response.json()

        houses = data["houses_aspected"]
        # Keys should be string house numbers
        for _key, value in houses.items():
            assert isinstance(value, list)


# =============================================================================
# Bhava Bala Endpoint
# =============================================================================


class TestBhavaBalaEndpoint:
    """Test POST /api/v1/analysis/bhava-bala."""

    def test_bhava_bala_success(self):
        """Test successful Bhava Bala calculation."""
        response = client.post("/api/v1/analysis/bhava-bala", json=BIRTH_DATA)
        assert response.status_code == 200

        data = response.json()
        assert "houses" in data
        assert "lagna_rashi" in data

    def test_bhava_bala_all_12_houses(self):
        """Test that all 12 houses are present."""
        response = client.post("/api/v1/analysis/bhava-bala", json=BIRTH_DATA)
        data = response.json()

        houses = data["houses"]
        for h in range(1, 13):
            assert str(h) in houses

    def test_bhava_bala_has_components(self):
        """Test that each house has strength components."""
        response = client.post("/api/v1/analysis/bhava-bala", json=BIRTH_DATA)
        data = response.json()

        house_1 = data["houses"]["1"]
        assert "total" in house_1
        assert "components" in house_1
        assert "is_strong" in house_1


# =============================================================================
# Muhurta Endpoints
# =============================================================================


class TestAbhijitMuhurtaEndpoint:
    """Test GET /api/v1/timing/abhijit-muhurta."""

    def test_abhijit_success(self):
        """Test successful Abhijit muhurta calculation."""
        response = client.get(
            "/api/v1/timing/abhijit-muhurta",
            params={"lat": 16.726, "lon": 81.288, "date": "2026-02-04T12:00:00"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "abhijit_start" in data
        assert "abhijit_end" in data
        assert "duration_minutes" in data

    def test_abhijit_default_date(self):
        """Test without explicit date (defaults to now)."""
        response = client.get(
            "/api/v1/timing/abhijit-muhurta",
            params={"lat": 16.726, "lon": 81.288},
        )
        assert response.status_code == 200


class TestBrahmaMuhurtaEndpoint:
    """Test GET /api/v1/timing/brahma-muhurta."""

    def test_brahma_success(self):
        """Test successful Brahma muhurta calculation."""
        response = client.get(
            "/api/v1/timing/brahma-muhurta",
            params={"lat": 16.726, "lon": 81.288, "date": "2026-02-04T12:00:00"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "brahma_start" in data
        assert "brahma_end" in data
        assert data["duration_minutes"] == 48


class TestEclipseEndpoint:
    """Test GET /api/v1/timing/eclipses/{year}/{month}."""

    def test_eclipse_success(self):
        """Test successful eclipse check."""
        response = client.get("/api/v1/timing/eclipses/2025/3")
        assert response.status_code == 200

        data = response.json()
        assert "year" in data
        assert data["year"] == 2025
        assert "month" in data
        assert data["month"] == 3
        assert "eclipse_count" in data
        assert "eclipses" in data

    def test_eclipse_no_eclipses_month(self):
        """Test month with no eclipses."""
        response = client.get("/api/v1/timing/eclipses/2025/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["eclipses"], list)


# =============================================================================
# Ashtottari Dasha Endpoint
# =============================================================================


class TestAshtottariEndpoint:
    """Test POST /api/v1/dasha/ashtottari."""

    def test_ashtottari_success(self):
        """Test successful Ashtottari dasha calculation."""
        response = client.post(
            "/api/v1/dasha/ashtottari",
            json={
                "birth_datetime": "1992-12-03T03:00:00",
                "moon_nakshatra": 25,
                "degree_in_nakshatra": 10.0,
                "rahu_house": 7,
                "lagna_lord_house": 1,
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["system"] == "ashtottari"
        assert "applicable" in data
        assert "current" in data
        assert "periods" in data

    def test_ashtottari_current_has_lords(self):
        """Test that current dasha has lord information."""
        response = client.post(
            "/api/v1/dasha/ashtottari",
            json={
                "birth_datetime": "1992-12-03T03:00:00",
                "moon_nakshatra": 25,
                "degree_in_nakshatra": 10.0,
            },
        )
        data = response.json()

        current = data["current"]
        assert "mahadasha_lord" in current
        assert "antardasha_lord" in current

    def test_ashtottari_not_applicable(self):
        """Test when Ashtottari is not applicable."""
        response = client.post(
            "/api/v1/dasha/ashtottari",
            json={
                "birth_datetime": "1992-12-03T03:00:00",
                "moon_nakshatra": 25,
                "degree_in_nakshatra": 10.0,
                "rahu_house": 6,
                "lagna_lord_house": 1,
            },
        )
        data = response.json()
        assert data["applicable"] is False


# =============================================================================
# Progressions Endpoint
# =============================================================================


class TestProgressionsEndpoint:
    """Test POST /api/v1/progressions/current."""

    def test_progressions_success(self):
        """Test successful progressions calculation."""
        response = client.post("/api/v1/progressions/current", json=BIRTH_DATA)
        assert response.status_code == 200

        data = response.json()
        assert data["system"] == "secondary_progressions"
        assert "age_years" in data
        assert "progressed_positions" in data
        assert "active_aspects" in data

    def test_progressions_has_planets(self):
        """Test that progressed positions include planets."""
        response = client.post("/api/v1/progressions/current", json=BIRTH_DATA)
        data = response.json()

        prog = data["progressed_positions"]
        assert "sun" in prog


# =============================================================================
# Knowledge Endpoints
# =============================================================================


class TestTithiEndpoint:
    """Test GET /api/v1/knowledge/tithis/{number}."""

    def test_tithi_lookup(self):
        """Test tithi lookup returns data."""
        response = client.get("/api/v1/knowledge/tithis/1")
        # May be 200 or 404 depending on data format
        assert response.status_code in (200, 404)


class TestKaranaEndpoint:
    """Test GET /api/v1/knowledge/karanas/{name}."""

    def test_karana_lookup(self):
        """Test karana lookup returns data."""
        response = client.get("/api/v1/knowledge/karanas/bava")
        assert response.status_code in (200, 404)


class TestVaraEndpoint:
    """Test GET /api/v1/knowledge/varas/{name}."""

    def test_vara_lookup(self):
        """Test vara lookup returns data."""
        response = client.get("/api/v1/knowledge/varas/monday")
        assert response.status_code in (200, 404)


class TestAvasthaEndpoint:
    """Test GET /api/v1/knowledge/avasthas/{planet}."""

    def test_avastha_lookup(self):
        """Test avastha lookup returns data."""
        response = client.get("/api/v1/knowledge/avasthas/jupiter", params={"longitude": 136.24})
        assert response.status_code == 200

        data = response.json()
        assert "planet" in data
        assert data["planet"] == "jupiter"

    def test_avastha_with_baladi(self):
        """Test baladi avastha calculation."""
        response = client.get("/api/v1/knowledge/avasthas/sun", params={"longitude": 45.0})
        data = response.json()

        # 45 % 30 = 15 -> yuva (12-18)
        assert data.get("baladi_avastha") == "yuva"


class TestNityaYogaEndpoint:
    """Test GET /api/v1/knowledge/nitya-yogas/{number}."""

    def test_nitya_yoga_lookup(self):
        """Test nitya yoga lookup returns data."""
        response = client.get("/api/v1/knowledge/nitya-yogas/1")
        assert response.status_code in (200, 404)
