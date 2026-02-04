"""
Tests for the Guide agent.
"""
import pytest


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
    for intent, keywords in INTENT_KEYWORDS.items():
        assert isinstance(keywords, list)
        assert len(keywords) > 0


def test_personality_styles():
    """Test that all 12 zodiac signs have personality styles."""
    from packages.guide.src.agent import PERSONALITY_STYLES

    signs = [
        "aries", "taurus", "gemini", "cancer",
        "leo", "virgo", "libra", "scorpio",
        "sagittarius", "capricorn", "aquarius", "pisces"
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
    from packages.guide.src.agent import AgentState

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

        assert best_intent == expected_intent, f"Expected {expected_intent} for '{user_input}', got {best_intent}"


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
    assert guide._route_by_intent({"intent": IntentType.REMEDY}) == "general"
    assert guide._route_by_intent({"intent": IntentType.UNKNOWN}) == "general"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
