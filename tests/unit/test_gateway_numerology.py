"""Tests for the numerology gateway router and chat tool integration.

Tests cover:
- Numerology router helper functions (extract_birth_date)
- Router endpoint logic (profile, cycles, name-analysis, compatibility, daily)
- Chat tool integration (get_numerology tool definition and execution)
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.self.src.numerology import (
    NUMBER_PLANET_MAP,
    analyze_name,
    calculate_full_profile,
    calculate_personal_day,
    get_compound_meaning,
    get_number_compatibility,
    get_personal_cycles,
)

# ── Sample data ──

BIRTH_DATE = date(1992, 12, 3)
SAMPLE_NAME = "Srikanth"

SAMPLE_BIRTH_CONTEXT: dict[str, Any] = {
    "birth_datetime": "1992-12-03T03:00:00+05:30",
    "birth_lat": 16.726239,
    "birth_lon": 81.288428,
    "natal_planets": {
        "sun": {"longitude": 227.0, "rashi": 7, "house": 2, "nakshatra": "Anuradha"},
        "moon": {
            "longitude": 326.85,
            "rashi": 10,
            "house": 5,
            "nakshatra": "Purva Bhadrapada",
            "sign": "Aquarius",
        },
        "mars": {"longitude": 97.0, "rashi": 3, "house": 10, "nakshatra": "Pushya"},
        "mercury": {"longitude": 243.0, "rashi": 8, "house": 2, "nakshatra": "Jyeshtha"},
        "jupiter": {"longitude": 155.0, "rashi": 5, "house": 11, "nakshatra": "Uttara Phalguni"},
        "venus": {"longitude": 198.0, "rashi": 6, "house": 1, "nakshatra": "Swati"},
        "saturn": {"longitude": 318.0, "rashi": 10, "house": 4, "nakshatra": "Shatabhisha"},
        "rahu": {"longitude": 212.0, "rashi": 7, "house": 1, "nakshatra": "Vishakha"},
        "ketu": {"longitude": 32.0, "rashi": 1, "house": 7, "nakshatra": "Rohini"},
    },
    "moon_longitude": 326.85,
    "lagna_rashi": "Libra",
    "moon_rashi": "Aquarius",
    "moon_nakshatra": "Purva Bhadrapada",
}


# =====================================================================
# A. Router helper: _extract_birth_date
# =====================================================================


class TestExtractBirthDate:
    """Verify _extract_birth_date handles various input types."""

    def test_from_datetime(self) -> None:
        from gateway.routers.numerology import _extract_birth_date

        chart = {"birth_datetime": datetime(1992, 12, 3, 3, 0, 0)}
        assert _extract_birth_date(chart) == date(1992, 12, 3)

    def test_from_date(self) -> None:
        from gateway.routers.numerology import _extract_birth_date

        chart = {"birth_datetime": date(1992, 12, 3)}
        assert _extract_birth_date(chart) == date(1992, 12, 3)

    def test_from_iso_string(self) -> None:
        from gateway.routers.numerology import _extract_birth_date

        chart = {"birth_datetime": "1992-12-03T03:00:00+05:30"}
        assert _extract_birth_date(chart) == date(1992, 12, 3)

    def test_missing_raises(self) -> None:
        from gateway.routers.numerology import _extract_birth_date

        with pytest.raises(ValueError, match="missing"):
            _extract_birth_date({})

    def test_none_raises(self) -> None:
        from gateway.routers.numerology import _extract_birth_date

        with pytest.raises(ValueError, match="missing"):
            _extract_birth_date({"birth_datetime": None})


# =====================================================================
# B. Numerology profile computation (backend logic used by router)
# =====================================================================


class TestNumerologyProfile:
    """Test the profile calculation that the router endpoint calls."""

    def test_full_profile_returns_profile(self) -> None:
        profile = calculate_full_profile(BIRTH_DATE)
        assert profile.psychic_number == 3
        assert 1 <= profile.destiny_number <= 9
        assert profile.psychic_planet in NUMBER_PLANET_MAP.values()
        assert profile.destiny_planet in NUMBER_PLANET_MAP.values()

    def test_full_profile_with_name(self) -> None:
        profile = calculate_full_profile(BIRTH_DATE, name=SAMPLE_NAME)
        assert profile.name_number is not None
        assert 1 <= profile.name_number <= 9
        assert profile.name_planet is not None

    def test_personal_cycles(self) -> None:
        target = date(2026, 3, 7)
        cycles = get_personal_cycles(BIRTH_DATE, target)
        assert 1 <= cycles.personal_year <= 9
        assert 1 <= cycles.personal_month <= 9
        assert 1 <= cycles.personal_day <= 9
        assert cycles.year_planet in NUMBER_PLANET_MAP.values()
        assert cycles.year_meaning  # non-empty

    def test_personal_day(self) -> None:
        target = date(2026, 3, 7)
        pd = calculate_personal_day(BIRTH_DATE, target)
        assert 1 <= pd <= 9


# =====================================================================
# C. Name analysis (backend logic used by name-analysis endpoint)
# =====================================================================


class TestNameAnalysis:
    """Test name analysis functions used by the POST endpoint."""

    def test_analyze_name_returns_analysis(self) -> None:
        analysis = analyze_name(SAMPLE_NAME)
        assert analysis.full_name == SAMPLE_NAME
        assert 1 <= analysis.chaldean_reduced <= 9
        assert 1 <= analysis.pythagorean_reduced <= 9
        assert analysis.ruling_planet in NUMBER_PLANET_MAP.values()
        assert len(analysis.letter_breakdown) > 0

    def test_compound_meaning(self) -> None:
        meaning = get_compound_meaning(19)
        assert meaning  # non-empty for compound 19
        assert "Sun" in meaning or "success" in meaning.lower()

    def test_compound_meaning_none(self) -> None:
        meaning = get_compound_meaning(None)
        assert meaning == ""


# =====================================================================
# D. Compatibility (backend logic used by compatibility endpoint)
# =====================================================================


class TestNumerologyCompatibility:
    """Test number compatibility functions."""

    def test_same_number_compatibility(self) -> None:
        result = get_number_compatibility(3, 3)
        assert result.number_1 == 3
        assert result.number_2 == 3
        assert 0 <= result.score <= 100

    def test_different_numbers(self) -> None:
        result = get_number_compatibility(1, 9)
        assert result.score >= 80  # 1-9 is traditionally excellent
        assert result.nature == "excellent"

    def test_invalid_numbers_raise(self) -> None:
        with pytest.raises(ValueError):
            get_number_compatibility(0, 5)

    def test_compatibility_symmetric(self) -> None:
        r1 = get_number_compatibility(3, 7)
        r2 = get_number_compatibility(7, 3)
        assert r1.score == r2.score
        assert r1.nature == r2.nature


# =====================================================================
# E. Daily numerology (backend logic used by daily endpoint)
# =====================================================================


class TestDailyNumerology:
    """Test daily numerology calculation logic."""

    def test_personal_day_planet_mapping(self) -> None:
        pd = calculate_personal_day(BIRTH_DATE, date(2026, 3, 7))
        planet = NUMBER_PLANET_MAP.get(pd)
        assert planet is not None
        assert planet in NUMBER_PLANET_MAP.values()

    def test_compound_meaning_for_compound(self) -> None:
        # Compound numbers 10-33 should have meanings
        for n in [10, 11, 15, 19, 22, 27, 33]:
            meaning = get_compound_meaning(n)
            assert meaning, f"Compound {n} should have a meaning"


# =====================================================================
# F. Chat tool integration
# =====================================================================


class TestNumerologyChatTool:
    """Test the get_numerology chat tool definition and execution."""

    def test_tool_definition_present(self) -> None:
        from packages.guide.src.chat_tools import TOOL_DEFINITIONS

        names = {t["name"] for t in TOOL_DEFINITIONS}
        assert "get_numerology" in names

    def test_tool_schema_valid(self) -> None:
        from packages.guide.src.chat_tools import TOOL_DEFINITIONS

        tool = next(t for t in TOOL_DEFINITIONS if t["name"] == "get_numerology")
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert schema["required"] == []

    def test_execute_numerology_without_name(self) -> None:
        from packages.guide.src.chat_tools import execute_tool

        result = execute_tool("get_numerology", {}, SAMPLE_BIRTH_CONTEXT)
        assert result.get("success") is True
        assert "psychic_number" in result
        assert "destiny_number" in result
        assert "personal_year" in result
        assert "lo_shu_grid" in result
        assert result["psychic_number"] == 3  # Dec 3 -> 3

    def test_execute_numerology_with_name(self) -> None:
        from packages.guide.src.chat_tools import execute_tool

        result = execute_tool("get_numerology", {"name": "Srikanth"}, SAMPLE_BIRTH_CONTEXT)
        assert result.get("success") is True
        assert result["name_number"] is not None
        assert 1 <= result["name_number"] <= 9

    def test_execute_numerology_includes_jyotish_ref(self) -> None:
        from packages.guide.src.chat_tools import execute_tool

        result = execute_tool("get_numerology", {}, SAMPLE_BIRTH_CONTEXT)
        assert result.get("success") is True
        assert "jyotish_cross_reference" in result
        jref = result["jyotish_cross_reference"]
        assert "psychic_planet" in jref
        assert "destiny_planet" in jref


# =====================================================================
# G. Router module importability
# =====================================================================


class TestRouterImport:
    """Verify the numerology router imports cleanly."""

    def test_router_importable(self) -> None:
        from gateway.routers.numerology import router

        assert router is not None

    def test_router_has_expected_routes(self) -> None:
        from gateway.routers.numerology import router

        route_paths = [r.path for r in router.routes]
        assert "/profile" in route_paths
        assert "/cycles" in route_paths
        assert "/name-analysis" in route_paths
        assert "/compatibility" in route_paths
        assert "/daily" in route_paths

    def test_main_app_includes_numerology(self) -> None:
        from gateway.main import create_app

        app = create_app()
        route_paths = [r.path for r in app.routes]
        assert "/api/v1/numerology/profile" in route_paths
        assert "/api/v1/numerology/cycles" in route_paths
        assert "/api/v1/numerology/name-analysis" in route_paths
        assert "/api/v1/numerology/compatibility" in route_paths
        assert "/api/v1/numerology/daily" in route_paths
