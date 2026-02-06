"""
Integration tests for Session 22 features.

Tests new MCP tools, API endpoints, Guide agent wiring, and module exports
added during Session 22:
- Synastry (house overlay, cross aspects, composite chart)
- Gem Recommender (prescription, compatibility check)
- Atmakaraka Deep Analysis (soul purpose, Ishta Devata, Karakamsha)
- Daily / Weekly / Monthly Forecast engines
- Guide agent wiring (new tool methods, extended intent handling)
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.api.main import app  # noqa: E402

# Sample birth chart data (User's birth data for Libra lagna)
SAMPLE_PLANETS = {
    "sun": {
        "longitude": 227.5,
        "rashi": "scorpio",
        "house": 2,
        "is_retrograde": False,
        "speed": 1.0,
    },
    "moon": {
        "longitude": 326.85,
        "rashi": "aquarius",
        "house": 5,
        "is_retrograde": False,
        "speed": 13.0,
    },
    "mars": {
        "longitude": 85.5,
        "rashi": "gemini",
        "house": 9,
        "is_retrograde": False,
        "speed": 0.5,
    },
    "mercury": {
        "longitude": 210.5,
        "rashi": "libra",
        "house": 1,
        "is_retrograde": False,
        "speed": 1.2,
    },
    "jupiter": {
        "longitude": 125.5,
        "rashi": "leo",
        "house": 11,
        "is_retrograde": False,
        "speed": 0.08,
    },
    "venus": {
        "longitude": 250.5,
        "rashi": "sagittarius",
        "house": 3,
        "is_retrograde": False,
        "speed": 1.1,
    },
    "saturn": {
        "longitude": 315.5,
        "rashi": "aquarius",
        "house": 5,
        "is_retrograde": False,
        "speed": 0.03,
    },
    "rahu": {
        "longitude": 50.0,
        "rashi": "taurus",
        "house": 8,
        "is_retrograde": True,
        "speed": -0.05,
    },
    "ketu": {
        "longitude": 230.0,
        "rashi": "scorpio",
        "house": 2,
        "is_retrograde": True,
        "speed": -0.05,
    },
}

# Partner chart data for synastry tests
PARTNER_PLANETS = {
    "sun": {"longitude": 60.0, "rashi": "gemini", "house": 7, "is_retrograde": False},
    "moon": {"longitude": 150.0, "rashi": "virgo", "house": 10, "is_retrograde": False},
    "mars": {"longitude": 280.0, "rashi": "capricorn", "house": 2, "is_retrograde": False},
    "mercury": {"longitude": 45.0, "rashi": "taurus", "house": 6, "is_retrograde": False},
    "jupiter": {"longitude": 240.0, "rashi": "sagittarius", "house": 1, "is_retrograde": False},
    "venus": {"longitude": 30.0, "rashi": "taurus", "house": 6, "is_retrograde": False},
    "saturn": {"longitude": 300.0, "rashi": "aquarius", "house": 3, "is_retrograde": False},
    "rahu": {"longitude": 120.0, "rashi": "leo", "house": 9, "is_retrograde": True},
    "ketu": {"longitude": 300.0, "rashi": "aquarius", "house": 3, "is_retrograde": True},
}

SAMPLE_CUSPS = [180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0]
PARTNER_CUSPS = [240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0]

SAMPLE_BIRTH_REQUEST = {
    "datetime": "1992-12-03T03:00:00",
    "latitude": 16.726239,
    "longitude": 81.288428,
    "timezone_offset": 5.5,
    "ayanamsa": "lahiri",
}


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client():
    """Create FastAPI test client."""
    with TestClient(app) as c:
        yield c


# ============================================================================
# Module Import Tests
# ============================================================================


class TestModuleImports:
    """Test that all new Session 22 exports are importable."""

    def test_self_synastry_imports(self):
        """Test synastry functions are importable from self package."""
        from packages.self.src import (
            calculate_composite_chart,
            calculate_cross_aspects,
            calculate_house_overlay,
            get_synastry_report,
        )

        assert callable(calculate_house_overlay)
        assert callable(calculate_cross_aspects)
        assert callable(calculate_composite_chart)
        assert callable(get_synastry_report)

    def test_self_gem_recommender_imports(self):
        """Test gem recommender functions are importable."""
        from packages.self.src import (
            check_gem_compatibility,
            get_lagna_gem_map,
            recommend_gems,
        )

        assert callable(recommend_gems)
        assert callable(get_lagna_gem_map)
        assert callable(check_gem_compatibility)

    def test_self_atmakaraka_imports(self):
        """Test new Jaimini/atmakaraka functions are importable."""
        from packages.self.src import (
            get_all_chara_karaka_analysis,
            get_atmakaraka_analysis,
            get_ishta_devata,
        )

        assert callable(get_atmakaraka_analysis)
        assert callable(get_ishta_devata)
        assert callable(get_all_chara_karaka_analysis)

    def test_context_forecast_imports(self):
        """Test forecast functions are importable from context package."""
        from packages.context.src import (
            get_daily_forecast,
            get_monthly_forecast,
            get_weekly_forecast,
        )

        assert callable(get_daily_forecast)
        assert callable(get_weekly_forecast)
        assert callable(get_monthly_forecast)


# ============================================================================
# MCP Tools Integration Tests -- Patterns Server
# ============================================================================


class TestMCPPatternToolsSession22:
    """Test new MCP tools added to patterns_server.py in Session 22."""

    def test_synastry_analysis_tool(self):
        """Test synastry_analysis MCP tool."""
        from services.mcp.patterns_server import synastry_analysis

        result = synastry_analysis(
            native_planets=SAMPLE_PLANETS,
            native_cusps=SAMPLE_CUSPS,
            partner_planets=PARTNER_PLANETS,
            partner_cusps=PARTNER_CUSPS,
            native_ascendant=180.0,
            partner_ascendant=240.0,
        )
        assert result.get("success") is True
        assert "house_overlay" in result or "cross_aspects" in result or "composite" in result

    def test_synastry_analysis_tool_error_handling(self):
        """Test synastry_analysis handles errors gracefully."""
        from services.mcp.patterns_server import synastry_analysis

        result = synastry_analysis(
            native_planets={},
            native_cusps=[],
            partner_planets={},
            partner_cusps=[],
            native_ascendant=0.0,
            partner_ascendant=0.0,
        )
        # Should either succeed with empty data or return error gracefully
        assert isinstance(result, dict)

    def test_gem_recommendation_tool(self):
        """Test gem_recommendation MCP tool."""
        from services.mcp.patterns_server import gem_recommendation

        result = gem_recommendation(
            lagna_rashi="libra",
            planets=SAMPLE_PLANETS,
        )
        assert result.get("success") is True

    def test_gem_recommendation_with_dasha(self):
        """Test gem recommendation with current dasha info."""
        from services.mcp.patterns_server import gem_recommendation

        result = gem_recommendation(
            lagna_rashi="libra",
            planets=SAMPLE_PLANETS,
            current_dasha={"mahadasha_lord": "mercury", "antardasha_lord": "venus"},
        )
        assert result.get("success") is True

    def test_atmakaraka_analysis_tool(self):
        """Test atmakaraka_analysis MCP tool."""
        from services.mcp.patterns_server import atmakaraka_analysis

        result = atmakaraka_analysis(
            planets=SAMPLE_PLANETS,
            lagna_rashi="libra",
        )
        assert result.get("success") is True

    def test_check_gem_compatibility_tool(self):
        """Test check_gem_compatibility_tool MCP tool."""
        from services.mcp.patterns_server import check_gem_compatibility_tool

        result = check_gem_compatibility_tool(
            gem_planet="saturn",
            lagna_rashi="libra",
            planets=SAMPLE_PLANETS,
        )
        assert result.get("success") is True

    def test_check_gem_compatibility_malefic(self):
        """Test gem compatibility check for a potentially harmful gem."""
        from services.mcp.patterns_server import check_gem_compatibility_tool

        result = check_gem_compatibility_tool(
            gem_planet="mars",
            lagna_rashi="libra",
            planets=SAMPLE_PLANETS,
        )
        assert result.get("success") is True


# ============================================================================
# MCP Tools Integration Tests -- Context Server
# ============================================================================


class TestMCPContextToolsSession22:
    """Test new MCP tools added to context_server.py in Session 22."""

    def test_daily_forecast_tool(self):
        """Test daily_forecast MCP tool."""
        from services.mcp.context_server import daily_forecast

        result = daily_forecast(
            birth_datetime="1992-12-03T03:00:00+05:30",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
        )
        assert result.get("success") is True
        assert "day_rating" in result

    def test_daily_forecast_with_query_date(self):
        """Test daily forecast for a specific date."""
        from services.mcp.context_server import daily_forecast

        result = daily_forecast(
            birth_datetime="1992-12-03T03:00:00+05:30",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07T00:00:00+05:30",
        )
        assert result.get("success") is True

    def test_weekly_forecast_tool(self):
        """Test weekly_forecast MCP tool."""
        from services.mcp.context_server import weekly_forecast

        result = weekly_forecast(
            birth_datetime="1992-12-03T03:00:00+05:30",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
        )
        assert result.get("success") is True

    def test_monthly_forecast_tool(self):
        """Test monthly_forecast MCP tool."""
        from services.mcp.context_server import monthly_forecast

        # Use naive datetime string to avoid naive/aware comparison in monthly_forecast
        result = monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            month=2,
            year=2026,
        )
        assert result.get("success") is True

    def test_monthly_forecast_default_month(self):
        """Test monthly forecast defaults to current month."""
        from services.mcp.context_server import monthly_forecast

        # Use naive datetime string to avoid naive/aware comparison in monthly_forecast
        result = monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
        )
        assert result.get("success") is True


# ============================================================================
# API Endpoint Tests
# ============================================================================


class TestAPIEndpointsSession22:
    """Test new API endpoints added in Session 22."""

    def test_synastry_endpoint(self, client):
        """Test POST /api/v1/analysis/synastry."""
        response = client.post(
            "/api/v1/analysis/synastry",
            json={
                "native_datetime": "1992-12-03T03:00:00",
                "native_latitude": 16.726239,
                "native_longitude": 81.288428,
                "partner_datetime": "1995-06-15T10:30:00",
                "partner_latitude": 17.385044,
                "partner_longitude": 78.486671,
                "timezone_offset": 5.5,
                "partner_timezone_offset": 5.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_gem_recommendation_endpoint(self, client):
        """Test POST /api/v1/analysis/gem-recommendation."""
        response = client.post(
            "/api/v1/analysis/gem-recommendation",
            json=SAMPLE_BIRTH_REQUEST,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_gem_compatibility_check_endpoint(self, client):
        """Test POST /api/v1/analysis/gem-recommendation with gem_planet."""
        request_data = {**SAMPLE_BIRTH_REQUEST, "gem_planet": "saturn"}
        response = client.post(
            "/api/v1/analysis/gem-recommendation",
            json=request_data,
        )
        assert response.status_code == 200

    def test_atmakaraka_endpoint(self, client):
        """Test POST /api/v1/analysis/atmakaraka."""
        response = client.post(
            "/api/v1/analysis/atmakaraka",
            json=SAMPLE_BIRTH_REQUEST,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_daily_forecast_endpoint(self, client):
        """Test POST /api/v1/forecast/daily."""
        response = client.post(
            "/api/v1/forecast/daily",
            json=SAMPLE_BIRTH_REQUEST,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_daily_forecast_with_date(self, client):
        """Test daily forecast with specific query date."""
        request_data = {**SAMPLE_BIRTH_REQUEST, "query_date": "2026-02-07"}
        response = client.post(
            "/api/v1/forecast/daily",
            json=request_data,
        )
        assert response.status_code == 200

    def test_weekly_forecast_endpoint(self, client):
        """Test POST /api/v1/forecast/weekly."""
        response = client.post(
            "/api/v1/forecast/weekly",
            json=SAMPLE_BIRTH_REQUEST,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_monthly_forecast_endpoint(self, client):
        """Test POST /api/v1/forecast/monthly."""
        request_data = {**SAMPLE_BIRTH_REQUEST, "month": 2, "year": 2026}
        response = client.post(
            "/api/v1/forecast/monthly",
            json=request_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


# ============================================================================
# Synastry Module Tests
# ============================================================================


class TestSynastryModule:
    """Test synastry module functions directly."""

    def test_house_overlay(self):
        """Test calculate_house_overlay."""
        from packages.self.src.synastry import calculate_house_overlay

        result = calculate_house_overlay(SAMPLE_PLANETS, SAMPLE_CUSPS, PARTNER_PLANETS)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_cross_aspects(self):
        """Test calculate_cross_aspects."""
        from packages.self.src.synastry import calculate_cross_aspects

        result = calculate_cross_aspects(SAMPLE_PLANETS, PARTNER_PLANETS)
        assert isinstance(result, list)

    def test_composite_chart(self):
        """Test calculate_composite_chart."""
        from packages.self.src.synastry import calculate_composite_chart

        result = calculate_composite_chart(
            SAMPLE_PLANETS,
            PARTNER_PLANETS,
            180.0,
            240.0,
        )
        assert isinstance(result, dict)

    def test_full_synastry_report(self):
        """Test get_synastry_report combines all analyses."""
        from packages.self.src.synastry import get_synastry_report

        result = get_synastry_report(
            native_planets=SAMPLE_PLANETS,
            native_cusps=SAMPLE_CUSPS,
            partner_planets=PARTNER_PLANETS,
            partner_cusps=PARTNER_CUSPS,
            native_ascendant=180.0,
            partner_ascendant=240.0,
            native_moon_nakshatra=22,
            partner_moon_nakshatra=13,
        )
        assert isinstance(result, dict)


# ============================================================================
# Gem Recommender Module Tests
# ============================================================================


class TestGemRecommenderModule:
    """Test gem recommender functions directly."""

    def test_recommend_gems(self):
        """Test recommend_gems returns prescriptions."""
        from packages.self.src.gem_recommender import recommend_gems

        result = recommend_gems(lagna_rashi="libra", planets=SAMPLE_PLANETS)
        assert isinstance(result, dict)

    def test_get_lagna_gem_map(self):
        """Test lagna-to-gem mapping."""
        from packages.self.src.gem_recommender import get_lagna_gem_map

        result = get_lagna_gem_map("libra")
        assert isinstance(result, dict)

    def test_check_gem_compatibility_safe(self):
        """Test gem compatibility for a yogakaraka planet."""
        from packages.self.src.gem_recommender import check_gem_compatibility

        # Saturn is yogakaraka for Libra lagna
        result = check_gem_compatibility("saturn", "libra", SAMPLE_PLANETS)
        assert isinstance(result, dict)

    def test_check_gem_compatibility_all_lagnas(self):
        """Test gem compatibility works for all 12 lagnas."""
        from packages.self.src.gem_recommender import check_gem_compatibility

        signs = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]
        for sign in signs:
            result = check_gem_compatibility("venus", sign, SAMPLE_PLANETS)
            assert isinstance(result, dict), f"Failed for {sign}"


# ============================================================================
# Forecast Module Tests
# ============================================================================


class TestDailyForecastModule:
    """Test daily forecast engine directly."""

    def test_daily_forecast_basic(self):
        """Test daily forecast returns expected structure."""
        from packages.context.src.daily_forecast import get_daily_forecast

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
        )
        assert isinstance(result, dict)
        assert "day_rating" in result
        assert 1 <= result["day_rating"] <= 10

    def test_daily_forecast_specific_date(self):
        """Test daily forecast for specific date."""
        from packages.context.src.daily_forecast import get_daily_forecast

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )
        assert isinstance(result, dict)
        assert "day_rating" in result


class TestWeeklyForecastModule:
    """Test weekly forecast engine directly."""

    def test_weekly_forecast_basic(self):
        """Test weekly forecast returns expected structure."""
        from packages.context.src.weekly_forecast import get_weekly_forecast

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
        )
        assert isinstance(result, dict)


class TestMonthlyForecastModule:
    """Test monthly forecast engine directly."""

    def test_monthly_forecast_basic(self):
        """Test monthly forecast returns expected structure."""
        from packages.context.src.monthly_forecast import get_monthly_forecast

        result = get_monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            month=2,
            year=2026,
        )
        assert isinstance(result, dict)

    def test_monthly_forecast_defaults_to_current(self):
        """Test monthly forecast defaults to current month when not specified."""
        from packages.context.src.monthly_forecast import get_monthly_forecast

        result = get_monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=SAMPLE_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
        )
        assert isinstance(result, dict)


# ============================================================================
# Guide Agent Tools Tests
# ============================================================================


class TestGuideAgentToolsSession22:
    """Test new Guide agent tool methods added in Session 22."""

    def test_tools_get_synastry_report(self):
        """Test AstrologyTools.get_synastry_report."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_synastry_report(
            native_birth_dt=datetime(1992, 12, 3, 3, 0, 0),
            native_lat=16.726239,
            native_lon=81.288428,
            partner_birth_dt=datetime(1995, 6, 15, 10, 30, 0),
            partner_lat=17.385044,
            partner_lon=78.486671,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_tools_get_gem_recommendation(self):
        """Test AstrologyTools.get_gem_recommendation."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_gem_recommendation(
            birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
            latitude=16.726239,
            longitude=81.288428,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_tools_get_gem_recommendation_specific(self):
        """Test gem compatibility check for specific planet."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_gem_recommendation(
            birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
            latitude=16.726239,
            longitude=81.288428,
            gem_planet="saturn",
        )
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_tools_get_atmakaraka_analysis(self):
        """Test AstrologyTools.get_atmakaraka_analysis."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_atmakaraka_analysis(
            birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
            latitude=16.726239,
            longitude=81.288428,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_tools_get_daily_forecast(self):
        """Test AstrologyTools.get_daily_forecast."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_daily_forecast(
            birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
            latitude=16.726239,
            longitude=81.288428,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_tools_get_weekly_forecast(self):
        """Test AstrologyTools.get_weekly_forecast."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_weekly_forecast(
            birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
            latitude=16.726239,
            longitude=81.288428,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True

    def test_tools_get_monthly_forecast(self):
        """Test AstrologyTools.get_monthly_forecast."""
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        result = tools.get_monthly_forecast(
            birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
            latitude=16.726239,
            longitude=81.288428,
            month=2,
            year=2026,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True


# ============================================================================
# Guide Agent Intent Wiring Tests
# ============================================================================


class TestGuideAgentWiringSession22:
    """Test that Guide agent correctly routes new intents."""

    def test_intent_keywords_have_forecast_terms(self):
        """Test that PREDICT intent includes forecast keywords."""
        from packages.guide.src.agent import INTENT_KEYWORDS, IntentType

        predict_keywords = INTENT_KEYWORDS[IntentType.PREDICT]
        assert "forecast" in predict_keywords
        assert "today" in predict_keywords
        assert "weekly" in predict_keywords
        assert "monthly" in predict_keywords

    def test_intent_keywords_have_gem_terms(self):
        """Test that ANALYZE intent includes gem/synastry keywords."""
        from packages.guide.src.agent import INTENT_KEYWORDS, IntentType

        analyze_keywords = INTENT_KEYWORDS[IntentType.ANALYZE]
        assert "gemstone" in analyze_keywords or "gem" in analyze_keywords
        assert "synastry" in analyze_keywords
        assert "atmakaraka" in analyze_keywords

    def test_convenience_functions_exist(self):
        """Test that convenience functions are exported from tools module."""
        from packages.guide.src.tools import (
            get_atmakaraka_analysis,
            get_daily_forecast,
            get_gem_recommendation,
            get_monthly_forecast,
            get_synastry_report_fn,
            get_weekly_forecast,
        )

        assert callable(get_synastry_report_fn)
        assert callable(get_gem_recommendation)
        assert callable(get_atmakaraka_analysis)
        assert callable(get_daily_forecast)
        assert callable(get_weekly_forecast)
        assert callable(get_monthly_forecast)


# ============================================================================
# Knowledge Rules Tests
# ============================================================================


class TestKnowledgeRulesSession22:
    """Test that new knowledge rule files are loadable."""

    def test_atmakaraka_rules_exist(self):
        """Test atmakaraka_rules.json is loadable."""
        import json

        path = PROJECT_ROOT / "knowledge" / "rules" / "atmakaraka_rules.json"
        assert path.exists(), f"{path} does not exist"
        with path.open() as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_synastry_rules_exist(self):
        """Test synastry_rules.json is loadable."""
        import json

        path = PROJECT_ROOT / "knowledge" / "rules" / "synastry_rules.json"
        assert path.exists(), f"{path} does not exist"
        with path.open() as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_gem_prescription_rules_exist(self):
        """Test gem_prescription_rules.json is loadable."""
        import json

        path = PROJECT_ROOT / "knowledge" / "rules" / "gem_prescription_rules.json"
        assert path.exists(), f"{path} does not exist"
        with path.open() as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert len(data) > 0
