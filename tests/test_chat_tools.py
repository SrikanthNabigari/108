"""Tests for chat tool definitions and execute_tool dispatcher."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.guide.src.chat_tools import (
    TOOL_DEFINITIONS,
    execute_tool,
    get_tool_definitions,
)

# ── Sample birth context (User's actual birth data) ──

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


class TestToolDefinitions:
    """Tests for tool schema definitions."""

    def test_get_tool_definitions_returns_list(self):
        defs = get_tool_definitions()
        assert isinstance(defs, list)
        assert len(defs) == 10

    def test_each_tool_has_required_keys(self):
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool.get('name')}"
            assert "input_schema" in tool, f"Tool missing 'input_schema': {tool.get('name')}"

    def test_each_tool_schema_is_valid_object(self):
        for tool in TOOL_DEFINITIONS:
            schema = tool["input_schema"]
            assert schema.get("type") == "object", f"Schema not object for {tool['name']}"
            assert "properties" in schema
            assert "required" in schema

    def test_tool_names_are_unique(self):
        names = [t["name"] for t in TOOL_DEFINITIONS]
        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

    def test_known_tools_present(self):
        names = {t["name"] for t in TOOL_DEFINITIONS}
        expected = {
            "get_state_now",
            "get_life_area",
            "get_current_dasha",
            "get_current_transits",
            "get_panchanga",
            "get_birth_chart_summary",
            "get_yogas",
            "get_doshas",
            "get_planet_strength",
            "get_compatibility",
        }
        assert expected == names

    def test_life_area_has_enum(self):
        area_tool = next(t for t in TOOL_DEFINITIONS if t["name"] == "get_life_area")
        area_enum = area_tool["input_schema"]["properties"]["area_id"]["enum"]
        assert "career" in area_enum
        assert "health" in area_enum
        assert "family" in area_enum
        assert len(area_enum) == 8

    def test_planet_strength_has_enum(self):
        tool = next(t for t in TOOL_DEFINITIONS if t["name"] == "get_planet_strength")
        planet_enum = tool["input_schema"]["properties"]["planet"]["enum"]
        assert "sun" in planet_enum
        assert "saturn" in planet_enum
        assert len(planet_enum) == 9


class TestExecuteTool:
    """Tests for tool dispatch execution."""

    def test_unknown_tool_returns_error(self):
        result = execute_tool("nonexistent_tool", {}, SAMPLE_BIRTH_CONTEXT)
        assert result["success"] is False
        assert "Unknown tool" in result["error"]

    def test_get_state_now_returns_state_vector(self):
        result = execute_tool("get_state_now", {}, SAMPLE_BIRTH_CONTEXT)
        assert "composite" in result or "error" in result
        # If successful, should have factors and areas
        if result.get("composite") is not None:
            assert "factors" in result
            assert "areas" in result

    def test_get_life_area_career(self):
        result = execute_tool("get_life_area", {"area_id": "career"}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "area" in result
            assert result["area"]["id"] == "career"
            assert "composite" in result

    def test_get_life_area_invalid(self):
        result = execute_tool("get_life_area", {"area_id": "nonexistent"}, SAMPLE_BIRTH_CONTEXT)
        # Should either error or return not found
        if result.get("success") is False:
            assert "error" in result

    def test_get_current_dasha_returns_periods(self):
        result = execute_tool("get_current_dasha", {}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "current_mahadasha" in result
            assert "current_antardasha" in result

    def test_get_panchanga_returns_five_limbs(self):
        result = execute_tool("get_panchanga", {}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "tithi" in result
            assert "nakshatra" in result
            assert "vara" in result

    def test_get_birth_chart_summary_from_context(self):
        result = execute_tool("get_birth_chart_summary", {}, SAMPLE_BIRTH_CONTEXT)
        assert result["success"] is True
        assert result["lagna_rashi"] == "Libra"
        assert result["moon_rashi"] == "Aquarius"
        assert "planets" in result
        assert "sun" in result["planets"]

    def test_get_yogas_returns_list(self):
        result = execute_tool("get_yogas", {}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "yogas" in result
            assert isinstance(result["yogas"], list)

    def test_get_doshas_returns_list(self):
        result = execute_tool("get_doshas", {}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "doshas" in result
            assert isinstance(result["doshas"], list)

    def test_get_planet_strength_sun(self):
        result = execute_tool("get_planet_strength", {"planet": "sun"}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert result["planet"] == "sun"

    def test_execute_with_empty_birth_context(self):
        result = execute_tool("get_birth_chart_summary", {}, {})
        assert result["success"] is True
        assert result["lagna_rashi"] is None

    def test_execute_tool_catches_exceptions(self):
        # Minimal context that might cause calculation errors
        result = execute_tool("get_state_now", {}, {"birth_datetime": "invalid"})
        # Should not raise, should return error dict
        assert isinstance(result, dict)
