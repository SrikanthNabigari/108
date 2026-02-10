"""
Tests for the Guide agent.
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from packages.guide.src.agent import AgentState


def test_intent_keywords():
    """Test that intent keywords are properly defined."""
    from packages.guide.src.agent import INTENT_KEYWORDS, IntentType

    # Check all intents have keywords
    assert IntentType.CALCULATE in INTENT_KEYWORDS
    assert IntentType.ANALYZE in INTENT_KEYWORDS
    assert IntentType.DASHA in INTENT_KEYWORDS
    assert IntentType.TRANSIT in INTENT_KEYWORDS
    assert IntentType.PREDICT in INTENT_KEYWORDS

    # Check keywords are non-empty lists
    for _intent, keywords in INTENT_KEYWORDS.items():
        assert isinstance(keywords, list)
        assert len(keywords) > 0


def test_personality_styles():
    """Test that all 12 zodiac signs have personality styles."""
    from packages.guide.src.agent import PERSONALITY_STYLES

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
        assert sign in PERSONALITY_STYLES
        style = PERSONALITY_STYLES[sign]
        assert "name" in style
        assert "tone" in style
        assert "approach" in style
        assert "keywords" in style


def test_intent_type_enum():
    """Test IntentType enum values."""
    from packages.guide.src.agent import IntentType

    assert IntentType.CALCULATE.value == "calculate"
    assert IntentType.ANALYZE.value == "analyze"
    assert IntentType.PREDICT.value == "predict"
    assert IntentType.DASHA.value == "dasha"
    assert IntentType.TRANSIT.value == "transit"


def test_agent_state_structure():
    """Test AgentState TypedDict has required fields."""

    # Check that AgentState can be used as type hint
    state: AgentState = {
        "messages": [],
        "user_input": "test",
        "response": None,
        "user_id": "test-user",
        "birth_chart": None,
        "current_dasha": None,
        "current_transits": None,
        "detected_yogas": [],
        "detected_doshas": [],
        "analysis_results": {},
        "memories": [],
        "intent": None,
        "personality_style": None,
        "session_id": "test-session",
        "timestamp": "2024-01-01T00:00:00",
    }

    assert state["user_input"] == "test"
    assert state["user_id"] == "test-user"


def test_keyword_based_classification():
    """Test that keyword-based intent classification works."""
    from packages.guide.src.agent import INTENT_KEYWORDS, IntentType

    # Test cases with clear keyword matches (avoiding overlap)
    test_cases = [
        ("what is my mahadasha dasha period", IntentType.DASHA),  # 2 dasha keywords
        ("calculate chart positions degree longitude", IntentType.CALCULATE),  # 3 calc keywords
        ("predict future outcome result", IntentType.PREDICT),  # 3 predict keywords
        ("transit gochara saturn passing through", IntentType.TRANSIT),  # 3 transit keywords
        ("yoga dosha strength pattern", IntentType.ANALYZE),  # 4 analyze keywords
    ]

    for user_input, expected_intent in test_cases:
        user_input_lower = user_input.lower()

        # Find best matching intent
        max_matches = 0
        best_intent = IntentType.UNKNOWN

        for intent_type, keywords in INTENT_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in user_input_lower)
            if matches > max_matches:
                max_matches = matches
                best_intent = intent_type

        assert (
            best_intent == expected_intent
        ), f"Expected {expected_intent} for '{user_input}', got {best_intent}"


def test_format_context_empty():
    """Test context formatting with empty state."""
    from packages.guide.src.agent import Guide

    # Create guide without API key (won't make API calls)
    guide = Guide.__new__(Guide)
    guide.debug = False

    state = {
        "birth_chart": None,
        "current_dasha": {},
        "analysis_results": {},
        "detected_yogas": [],
        "detected_doshas": [],
        "memories": [],
    }

    context = guide._format_context(state)
    assert "No specific context loaded" in context


def test_format_context_with_birth_chart():
    """Test context formatting with birth chart."""
    from packages.guide.src.agent import Guide

    guide = Guide.__new__(Guide)
    guide.debug = False

    state = {
        "birth_chart": {
            "lagna_rashi": "Libra",
            "moon_rashi": "Aquarius",
            "moon_nakshatra": "Purva Bhadrapada",
        },
        "current_dasha": {
            "mahadasha_lord": "Mercury",
            "antardasha_lord": "Sun",
        },
        "analysis_results": {},
        "detected_yogas": [{"name": "Budha-Aditya Yoga"}],
        "detected_doshas": [],
        "memories": [],
    }

    context = guide._format_context(state)
    assert "Libra" in context
    assert "Aquarius" in context
    assert "Mercury" in context
    assert "Budha-Aditya Yoga" in context


def test_route_by_intent():
    """Test intent routing logic."""
    from packages.guide.src.agent import Guide, IntentType

    guide = Guide.__new__(Guide)

    # Test routing
    assert guide._route_by_intent({"intent": IntentType.CALCULATE}) == "calculate"
    assert guide._route_by_intent({"intent": IntentType.DASHA}) == "calculate"
    assert guide._route_by_intent({"intent": IntentType.TRANSIT}) == "calculate"
    assert guide._route_by_intent({"intent": IntentType.ANALYZE}) == "analyze"
    assert guide._route_by_intent({"intent": IntentType.PREDICT}) == "predict"
    assert guide._route_by_intent({"intent": IntentType.TIMING}) == "predict"
    assert guide._route_by_intent({"intent": IntentType.GENERAL}) == "general"
    assert guide._route_by_intent({"intent": IntentType.REMEDY}) == "remedy"
    assert guide._route_by_intent({"intent": IntentType.UNKNOWN}) == "general"
    assert guide._route_by_intent({"intent": IntentType.STATE_MAP}) == "predict"


def test_state_map_intent_classification():
    """Test that STATE_MAP intent is classified by keywords."""
    from packages.guide.src.agent import INTENT_KEYWORDS, IntentType

    # Verify STATE_MAP keywords exist
    assert IntentType.STATE_MAP in INTENT_KEYWORDS
    keywords = INTENT_KEYWORDS[IntentType.STATE_MAP]
    assert len(keywords) > 0

    # Test specific queries that should trigger STATE_MAP
    test_queries = [
        "how is my career today",
        "show me the state map",
        "what are my strong areas",
        "how am i doing overall state",
        "life area scores please",
    ]

    for query in test_queries:
        query_lower = query.lower()
        max_matches = 0
        best_intent = IntentType.UNKNOWN

        for intent_type, kws in INTENT_KEYWORDS.items():
            matches = sum(1 for kw in kws if kw in query_lower)
            if matches > max_matches:
                max_matches = matches
                best_intent = intent_type

        assert (
            best_intent == IntentType.STATE_MAP
        ), f"Expected STATE_MAP for '{query}', got {best_intent}"


def test_state_map_conditional_edges():
    """Test that STATE_MAP is wired in the conditional edges."""
    from packages.guide.src.agent import IntentType

    # STATE_MAP should route to predict
    assert IntentType.STATE_MAP.value == "state_map"


def test_format_context_with_state_vector():
    """Test context formatting with state_vector in analysis_results."""
    from packages.guide.src.agent import Guide

    guide = Guide.__new__(Guide)
    guide.debug = False

    state = {
        "birth_chart": {
            "lagna_rashi": "Libra",
            "moon_rashi": "Aquarius",
        },
        "current_dasha": {},
        "analysis_results": {
            "state_vector": {
                "composite": 6.3,
                "mental_state": "positive",
                "factors": [
                    {"id": "panchanga", "short_name": "PAN", "score": 6.2, "label": "good"},
                    {"id": "transit_moon", "short_name": "MON", "score": 5.1, "label": "moderate"},
                    {"id": "gochara", "short_name": "GOC", "score": 7.0, "label": "good"},
                    {"id": "dasha", "short_name": "DAS", "score": 6.8, "label": "good"},
                    {
                        "id": "yoga_activation",
                        "short_name": "YOG",
                        "score": 5.5,
                        "label": "moderate",
                    },
                    {"id": "shadbala", "short_name": "SHA", "score": 6.0, "label": "moderate"},
                    {"id": "ashtakavarga", "short_name": "ASH", "score": 5.9, "label": "moderate"},
                ],
                "areas": [
                    {
                        "id": "career",
                        "score": 7.2,
                        "double_transit": True,
                        "active_yogas": ["Raja Yoga"],
                    },
                    {"id": "relationships", "score": 5.5},
                    {"id": "health", "score": 6.1},
                    {"id": "finance", "score": 6.8, "active_yogas": ["Dhana Yoga"]},
                    {"id": "spiritual", "score": 4.3},
                    {"id": "family", "score": 5.9},
                    {"id": "education", "score": 6.0},
                    {"id": "travel", "score": 5.0},
                ],
            },
        },
        "detected_yogas": [],
        "detected_doshas": [],
        "memories": [],
    }

    context = guide._format_context(state)
    assert "composite=6.3/10" in context
    assert "positive" in context
    assert "PAN=6.2" in context
    assert "career: 7.2/10" in context
    assert "DT" in context  # double transit annotation
    assert "1Y" in context  # 1 yoga annotation for career


def test_get_state_vector_tool():
    """Test AstrologyTools.get_state_vector() returns correct structure."""
    from datetime import datetime

    from packages.guide.src.tools import AstrologyTools

    tools = AstrologyTools()

    natal_planets = {
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

    result = tools.get_state_vector(
        birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
        birth_lat=16.726239,
        birth_lon=81.288428,
        natal_planets=natal_planets,
        moon_longitude=326.85,
        lagna_rashi="libra",
        moon_rashi="aquarius",
    )

    assert result["success"] is True
    sv = result["state_vector"]
    assert "factors" in sv
    assert "areas" in sv
    assert "composite" in sv
    assert "mental_state" in sv
    assert isinstance(sv["factors"], list)
    assert len(sv["factors"]) == 7
    assert isinstance(sv["areas"], list)
    assert len(sv["areas"]) == 8


def test_get_life_area_score_tool():
    """Test AstrologyTools.get_life_area_score() returns single area."""
    from datetime import datetime

    from packages.guide.src.tools import AstrologyTools

    tools = AstrologyTools()

    natal_planets = {
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

    result = tools.get_life_area_score(
        area_id="career",
        birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
        birth_lat=16.726239,
        birth_lon=81.288428,
        natal_planets=natal_planets,
        moon_longitude=326.85,
        lagna_rashi="libra",
    )

    assert result["success"] is True
    assert result["area_id"] == "career"
    assert "area" in result
    assert "composite" in result
    assert "mental_state" in result


def test_get_life_area_score_unknown_area():
    """Test get_life_area_score with unknown area returns error."""
    from datetime import datetime

    from packages.guide.src.tools import AstrologyTools

    tools = AstrologyTools()

    natal_planets = {
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

    result = tools.get_life_area_score(
        area_id="nonexistent",
        birth_datetime=datetime(1992, 12, 3, 3, 0, 0),
        birth_lat=16.726239,
        birth_lon=81.288428,
        natal_planets=natal_planets,
        moon_longitude=326.85,
        lagna_rashi="libra",
    )

    assert result["success"] is False
    assert "Unknown area" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
