"""Tests for MCP state_vector and state_range tools."""

from typing import Any

# ── Test data: reuse from test_state_engine ──

BIRTH_DT = "1992-12-03T03:00:00"
BIRTH_LAT = 16.726239
BIRTH_LON = 81.288428
LAGNA_RASHI = "libra"
MOON_LONGITUDE = 326.85
MOON_RASHI = "aquarius"

NATAL_PLANETS: dict[str, Any] = {
    "sun": {"longitude": 226.5, "rashi": 7, "house": 2},
    "moon": {"longitude": 326.85, "rashi": 10, "house": 5},
    "mars": {"longitude": 103.2, "rashi": 3, "house": 10},
    "mercury": {"longitude": 241.3, "rashi": 8, "house": 2},
    "jupiter": {"longitude": 142.8, "rashi": 4, "house": 11},
    "venus": {"longitude": 206.1, "rashi": 6, "house": 12},
    "saturn": {"longitude": 313.7, "rashi": 10, "house": 4},
    "rahu": {"longitude": 205.5, "rashi": 6, "house": 12},
    "ketu": {"longitude": 25.5, "rashi": 0, "house": 6},
}

EXPECTED_FACTORS = [
    "panchanga",
    "transit_moon",
    "gochara",
    "dasha",
    "yoga_activation",
    "shadbala",
    "ashtakavarga",
]

EXPECTED_AREAS = [
    "career",
    "relationships",
    "health",
    "finance",
    "spiritual",
    "family",
    "education",
    "travel",
]


class TestStateVectorMCP:
    """Tests for the state_vector MCP tool."""

    def test_state_vector_returns_success(self):
        """state_vector returns success=True with valid inputs."""
        from services.mcp.context_server import state_vector

        result = state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=MOON_RASHI,
        )

        assert result["success"] is True

    def test_state_vector_has_7_factors(self):
        """state_vector returns all 7 factor scores."""
        from services.mcp.context_server import state_vector

        result = state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
        )

        assert result["success"] is True
        factors = result["factors"]
        assert isinstance(factors, list)
        assert len(factors) == 7
        factor_ids = {f["id"] for f in factors}
        for factor_name in EXPECTED_FACTORS:
            assert factor_name in factor_ids, f"Missing factor: {factor_name}"
        for fdata in factors:
            assert "score" in fdata
            assert 0.0 <= fdata["score"] <= 10.0

    def test_state_vector_has_8_areas(self):
        """state_vector returns all 8 life area scores."""
        from services.mcp.context_server import state_vector

        result = state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
        )

        assert result["success"] is True
        areas = result["areas"]
        assert isinstance(areas, list)
        assert len(areas) == 8
        area_ids = {a["id"] for a in areas}
        for area_name in EXPECTED_AREAS:
            assert area_name in area_ids, f"Missing area: {area_name}"
        for adata in areas:
            assert "score" in adata
            assert 0.0 <= adata["score"] <= 10.0

    def test_state_vector_has_composite_and_mental(self):
        """state_vector returns composite score and mental_state."""
        from services.mcp.context_server import state_vector

        result = state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
        )

        assert result["success"] is True
        assert "composite" in result
        assert 0.0 <= result["composite"] <= 10.0
        assert "mental_state" in result
        assert result["mental_state"] in (
            "Thriving",
            "Flowing",
            "Steady",
            "Challenged",
            "Struggling",
            "Turbulent",
        )

    def test_state_vector_error_handling(self):
        """state_vector returns success=False on bad inputs."""
        from services.mcp.context_server import state_vector

        result = state_vector(
            birth_datetime="not-a-date",
            birth_lat=0.0,
            birth_lon=0.0,
            natal_planets={},
            moon_longitude=0.0,
            lagna_rashi="invalid",
        )

        assert result["success"] is False
        assert "error" in result

    def test_state_vector_with_query_datetime(self):
        """state_vector accepts a specific query_datetime."""
        from services.mcp.context_server import state_vector

        result = state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            query_datetime="2026-01-15T12:00:00",
        )

        assert result["success"] is True
        assert "composite" in result


class TestStateRangeMCP:
    """Tests for the state_range MCP tool."""

    def test_state_range_returns_vectors(self):
        """state_range returns a list of vectors."""
        from services.mcp.context_server import state_range

        result = state_range(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            start_date="2026-02-01",
            end_date="2026-02-03",
            resolution="daily",
        )

        assert result["success"] is True
        assert "vectors" in result
        assert isinstance(result["vectors"], list)
        assert len(result["vectors"]) >= 2  # At least 2 days

    def test_state_range_vectors_have_structure(self):
        """Each vector in range has composite and factors."""
        from services.mcp.context_server import state_range

        result = state_range(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            start_date="2026-02-01",
            end_date="2026-02-02",
            resolution="daily",
        )

        assert result["success"] is True
        for vec in result["vectors"]:
            assert "composite" in vec
            assert "factors" in vec
            assert "areas" in vec

    def test_state_range_bad_input_returns_empty_vectors(self):
        """state_range with bad birth data returns empty vectors list."""
        from services.mcp.context_server import state_range

        result = state_range(
            birth_datetime="bad-date",
            birth_lat=0.0,
            birth_lon=0.0,
            natal_planets={},
            moon_longitude=0.0,
            lagna_rashi="invalid",
            start_date="2026-02-01",
            end_date="2026-02-03",
        )

        # compute_state_range catches per-vector errors internally
        assert result["success"] is True
        assert result["vectors"] == []
