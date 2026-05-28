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
        assert len(defs) == 33

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
            # Original 10
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
            # Phase 1: Timing & Predictions (6)
            "get_forecast",
            "get_upcoming_events",
            "get_muhurta",
            "get_remedies",
            "get_dasha_timeline",
            "correlate_event",
            # Phase 2: Deep Analysis (6)
            "get_soul_purpose",
            "get_gem_recommendation",
            "get_divisional_chart",
            "check_yoga_cancellation",
            "get_retrograde_effects",
            "get_combustion_status",
            # Phase 3: Advanced Systems (7)
            "get_varshaphal",
            "get_kp_prediction",
            "get_prashna",
            "get_ashtakavarga",
            "get_alternative_dasha",
            "get_jaimini_analysis",
            "lookup_knowledge",
            "get_numerology",
            # Ambient (BPHS slow-burn) signals
            "get_ambient_signals",
            # Tithi Pravesha annual chart (lunar varshaphal)
            "get_tithi_pravesha",
            # Jaimini Chara Dasha + transit cross-analysis
            "get_chara_dasha_overlay",
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

    def test_get_current_dasha_includes_sookshma(self):
        result = execute_tool("get_current_dasha", {}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "current_sookshma" in result
            sookshma = result["current_sookshma"]
            assert "lord" in sookshma
            assert "days_remaining" in sookshma

    def test_get_current_dasha_includes_prana_deha(self):
        result = execute_tool("get_current_dasha", {}, SAMPLE_BIRTH_CONTEXT)
        if result.get("success"):
            assert "current_prana" in result
            assert "current_deha" in result
            assert "lord" in result["current_prana"]
            assert "lord" in result["current_deha"]

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
        assert result["success"] is True, f"get_yogas failed: {result.get('error')}"
        assert "yogas" in result
        assert isinstance(result["yogas"], list)
        assert result["yoga_count"] >= 0
        # Verify serialization — each yoga should be a dict (not pydantic model)
        for y in result["yogas"]:
            assert isinstance(y, dict)
            assert "name" in y
            assert "yoga_id" in y

    def test_get_doshas_returns_list(self):
        result = execute_tool("get_doshas", {}, SAMPLE_BIRTH_CONTEXT)
        assert result["success"] is True, f"get_doshas failed: {result.get('error')}"
        assert "doshas" in result
        assert isinstance(result["doshas"], list)
        assert result["dosha_count"] >= 0
        # Verify serialization — each dosha should be a dict (not pydantic model)
        for d in result["doshas"]:
            assert isinstance(d, dict)
            assert "name" in d
            assert "dosha_id" in d

    def test_get_current_transits_success(self):
        result = execute_tool("get_current_transits", {}, SAMPLE_BIRTH_CONTEXT)
        assert result["success"] is True, f"get_current_transits failed: {result.get('error')}"
        assert "transits" in result
        assert "natal_moon" in result

    def test_get_current_transits_without_sign_key(self):
        """Transit tool works even when moon has rashi_name instead of sign."""
        ctx_no_sign = {
            **SAMPLE_BIRTH_CONTEXT,
            "natal_planets": {
                **SAMPLE_BIRTH_CONTEXT["natal_planets"],
                "moon": {
                    "longitude": 326.85,
                    "rashi": 10,
                    "rashi_name": "aquarius",
                    "house": 5,
                    "nakshatra": "Purva Bhadrapada",
                },
            },
            "moon_rashi": None,  # simulate missing DB field
        }
        result = execute_tool("get_current_transits", {}, ctx_no_sign)
        assert result["success"] is True, f"transit failed without sign: {result.get('error')}"
        assert result["natal_moon"] == "Aquarius"

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

    # ── Phase 1: Timing & Predictions ──

    def test_get_forecast_daily(self):
        result = execute_tool("get_forecast", {"period": "daily"}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "forecast" in result

    def test_get_forecast_weekly(self):
        result = execute_tool("get_forecast", {"period": "weekly"}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "forecast" in result

    def test_get_forecast_monthly(self):
        result = execute_tool("get_forecast", {"period": "monthly"}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "forecast" in result

    def test_get_upcoming_events(self):
        result = execute_tool("get_upcoming_events", {"days_ahead": 7}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "triggers" in result

    def test_get_muhurta(self):
        result = execute_tool("get_muhurta", {"activity": "travel"}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "quality" in result or "score" in result or "overall_quality" in result

    def test_get_remedies(self):
        result = execute_tool("get_remedies", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "remedies" in result

    def test_get_dasha_timeline(self):
        result = execute_tool("get_dasha_timeline", {"years": 10}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "dasha_periods" in result or "dasha_timeline" in result

    def test_correlate_event(self):
        result = execute_tool(
            "correlate_event",
            {"event_date": "2020-03-15", "event_type": "career", "description": "Got promoted"},
            SAMPLE_BIRTH_CONTEXT,
        )
        assert isinstance(result, dict)
        if result.get("success"):
            assert "correlation" in result

    # ── Phase 2: Deep Analysis ──

    def test_get_soul_purpose(self):
        result = execute_tool("get_soul_purpose", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "atmakaraka" in result

    def test_get_gem_recommendation(self):
        result = execute_tool("get_gem_recommendation", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "gems" in result

    def test_get_gem_recommendation_specific_planet(self):
        result = execute_tool("get_gem_recommendation", {"planet": "jupiter"}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)

    def test_get_divisional_chart_d9(self):
        result = execute_tool("get_divisional_chart", {"chart_number": 9}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "divisional_charts" in result

    def test_check_yoga_cancellation(self):
        result = execute_tool("check_yoga_cancellation", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "total_yogas" in result
            assert "surviving_count" in result

    def test_get_retrograde_effects(self):
        result = execute_tool("get_retrograde_effects", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_get_combustion_status(self):
        result = execute_tool("get_combustion_status", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        assert result.get("success") is True

    # ── Phase 3: Advanced Systems ──

    def test_get_varshaphal(self):
        result = execute_tool("get_varshaphal", {"year": 2025}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "year" in result

    def test_get_kp_prediction(self):
        result = execute_tool(
            "get_kp_prediction", {"question_type": "career"}, SAMPLE_BIRTH_CONTEXT
        )
        assert isinstance(result, dict)
        if result.get("success"):
            assert "kp_analysis" in result

    def test_get_prashna(self):
        result = execute_tool(
            "get_prashna",
            {"question": "Will I get the job?", "category": "career"},
            SAMPLE_BIRTH_CONTEXT,
        )
        assert isinstance(result, dict)

    def test_get_ashtakavarga(self):
        result = execute_tool("get_ashtakavarga", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "bhinnashtakavarga" in result or "sarvashtakavarga" in result

    def test_get_alternative_dasha_yogini(self):
        result = execute_tool("get_alternative_dasha", {"system": "yogini"}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert result.get("system") == "yogini"

    def test_get_alternative_dasha_ashtottari(self):
        result = execute_tool(
            "get_alternative_dasha", {"system": "ashtottari"}, SAMPLE_BIRTH_CONTEXT
        )
        assert isinstance(result, dict)
        if result.get("success"):
            assert result.get("system") == "ashtottari"

    def test_get_jaimini_analysis(self):
        result = execute_tool("get_jaimini_analysis", {}, SAMPLE_BIRTH_CONTEXT)
        assert isinstance(result, dict)
        if result.get("success"):
            assert "chara_karakas" in result

    def test_lookup_knowledge_planet(self):
        result = execute_tool(
            "lookup_knowledge", {"query": "jupiter", "category": "planet"}, SAMPLE_BIRTH_CONTEXT
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("category") == "planet"

    def test_lookup_knowledge_yoga(self):
        result = execute_tool(
            "lookup_knowledge", {"query": "gajakesari", "category": "yoga"}, SAMPLE_BIRTH_CONTEXT
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
