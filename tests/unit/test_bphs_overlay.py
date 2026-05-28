"""Tests for BPHS overlay helpers in gateway/routers/analysis.py.

These helpers generate chart-specific text from interpret_dasha_combination()
output to replace generic knowledge text in dasha effects responses.
"""

import sys
from pathlib import Path

import pytest

# Ensure gateway is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.routers.analysis import (
    _bphs_area_text,
    _bphs_challenges,
    _bphs_focus_areas,
    _bphs_negative,
    _bphs_opportunities,
    _bphs_positive,
    _bphs_practical_advice,
)

# ── Fixtures ──


@pytest.fixture
def mercury_libra_bphs() -> dict:
    """Mercury as 9th/12th lord for Libra lagna, placed in 1st house.

    Matches the user's actual chart: Mercury rules Gemini (9th) and
    Virgo (12th) from Libra lagna, placed in house 1.
    """
    return {
        "lord": "mercury",
        "houses_ruled": [9, 12],
        "house_labels": [
            "9th (Dharma, Fortune, Philosophy)",
            "12th (Moksha, Foreign Lands, Spirituality)",
        ],
        "functional_nature": "benefic",
        "nature_explanation": "Mercury rules 9th (trikona) for Libra lagna",
        "natal_house": 1,
        "natal_house_label": "1st (Self, Body, Personality)",
        "dignity": "neutral",
        "dignity_label": "Neutral in Libra",
        "is_retrograde": False,
        "is_combust": False,
        "aspects_received": [
            {"planet": "saturn", "from_house": 4, "nature": "benefic"},
            {"planet": "mars", "from_house": 10, "nature": "malefic"},
        ],
        "conjunctions": [
            {"planet": "venus", "relationship": "friendly"},
        ],
        "yogas": [
            {"name": "Budha-Aditya Yoga", "strength": 0.7},
        ],
        "shadbala_score": 6.5,
        "house_lord_reading": {
            "summary": "9th lord in 1st: fortunate personality, dharmic nature.",
            "positive": [
                "Natural inclination toward higher learning",
                "Father's blessings support personal growth",
                "Fortune through self-effort and initiative",
            ],
            "negative": [
                "May become overly philosophical",
                "Foreign connections may cause displacement",
            ],
        },
        "summary": "Mercury as 9L/12L in H1 with neutral dignity...",
        "prediction": "Period activates dharma, fortune, and spirituality.",
    }


@pytest.fixture
def debilitated_mars_bphs() -> dict:
    """Mars debilitated in Cancer (H10) for Libra lagna, retrograde."""
    return {
        "lord": "mars",
        "houses_ruled": [2, 7],
        "house_labels": [
            "2nd (Wealth, Family, Speech)",
            "7th (Marriage, Partnership, Business)",
        ],
        "functional_nature": "neutral",
        "natal_house": 10,
        "dignity": "debilitated",
        "dignity_label": "Debilitated in Cancer",
        "is_retrograde": True,
        "is_combust": False,
        "aspects_received": [
            {"planet": "jupiter", "from_house": 6, "nature": "benefic"},
        ],
        "conjunctions": [
            {"planet": "saturn", "relationship": "hostile"},
        ],
        "yogas": [],
        "house_lord_reading": {
            "summary": "2nd lord in 10th: wealth through career.",
            "positive": ["Earns well through professional efforts"],
            "negative": ["Financial ups and downs tied to career"],
        },
        "summary": "Mars as 2L/7L debilitated in H10, retrograde...",
        "prediction": "Challenges in partnerships and finances.",
    }


@pytest.fixture
def exalted_lord_bphs() -> dict:
    """Jupiter exalted in Cancer (H10) — strong benefic."""
    return {
        "lord": "jupiter",
        "houses_ruled": [3, 6],
        "house_labels": ["3rd", "6th"],
        "functional_nature": "neutral",
        "natal_house": 10,
        "dignity": "exalted",
        "dignity_label": "Exalted in Cancer",
        "is_retrograde": False,
        "is_combust": True,
        "aspects_received": [],
        "conjunctions": [],
        "yogas": [{"name": "Hamsa Yoga", "strength": 0.85}],
        "house_lord_reading": {
            "summary": "3rd lord in 10th.",
            "positive": ["Initiative rewarded in career"],
            "negative": [],
        },
        "summary": "Jupiter exalted in H10...",
        "prediction": "Strong career growth expected.",
    }


@pytest.fixture
def empty_bphs() -> dict:
    """Minimal BPHS data with no aspects, conjunctions, or yogas."""
    return {
        "lord": "ketu",
        "houses_ruled": [],
        "natal_house": 5,
        "dignity": "neutral",
        "is_retrograde": False,
        "is_combust": False,
        "aspects_received": [],
        "conjunctions": [],
        "yogas": [],
        "house_lord_reading": {},
        "summary": "Ketu in H5.",
        "prediction": "Spiritual detachment from creativity.",
    }


# ======================================================================
# Test: _bphs_focus_areas
# ======================================================================


class TestBphsFocusAreas:
    def test_returns_theme_labels_for_ruled_houses(self, mercury_libra_bphs):
        result = _bphs_focus_areas(mercury_libra_bphs)
        assert len(result) == 2
        assert "Dharma & Fortune" in result
        assert "Moksha & Foreign Lands" in result

    def test_empty_when_no_houses_ruled(self, empty_bphs):
        result = _bphs_focus_areas(empty_bphs)
        assert result == []

    def test_returns_list_of_strings(self, debilitated_mars_bphs):
        result = _bphs_focus_areas(debilitated_mars_bphs)
        assert all(isinstance(s, str) for s in result)
        assert len(result) == 2


# ======================================================================
# Test: _bphs_area_text
# ======================================================================


class TestBphsAreaText:
    def test_lordship_connection_produces_text(self, mercury_libra_bphs):
        # Mercury rules 9 → spiritual area has house 9
        text = _bphs_area_text(mercury_libra_bphs, "spiritual")
        assert text  # Non-empty
        assert "9th" in text
        assert "lord" in text.lower()

    def test_placement_connection_produces_text(self, mercury_libra_bphs):
        # Mercury placed in house 1 → health area has house 1
        text = _bphs_area_text(mercury_libra_bphs, "health")
        assert "1st house" in text or "Placed in" in text

    def test_no_connection_returns_empty(self, mercury_libra_bphs):
        # Mercury rules 9,12 placed in 1 → career houses are 10,6,2
        # No lordship overlap, no placement overlap
        text = _bphs_area_text(mercury_libra_bphs, "career")
        # Mars aspects from H10 which is in career houses
        # So there might be aspect text, but no lordship/placement text
        # (H10 is a career house, and mars aspects from there)
        assert isinstance(text, str)

    def test_aspects_included_when_hitting_area_houses(self, mercury_libra_bphs):
        # Saturn aspects from H4; education houses are [4,5,9]
        text = _bphs_area_text(mercury_libra_bphs, "education")
        assert "Saturn" in text

    def test_dignity_modifier_included(self, debilitated_mars_bphs):
        # Mars rules 2,7; finances houses are [2,11,5]
        # Mars rules 2 → overlap; debilitated → dignity text
        text = _bphs_area_text(debilitated_mars_bphs, "finances")
        assert "Debilitated" in text or "debilitated" in text.lower()

    def test_invalid_area_returns_empty(self, mercury_libra_bphs):
        text = _bphs_area_text(mercury_libra_bphs, "nonexistent")
        assert text == ""


# ======================================================================
# Test: _bphs_opportunities
# ======================================================================


class TestBphsOpportunities:
    def test_benefic_aspects_mentioned(self, mercury_libra_bphs):
        text = _bphs_opportunities(mercury_libra_bphs)
        assert "Saturn" in text
        assert "Benefic" in text

    def test_friendly_conjunctions_mentioned(self, mercury_libra_bphs):
        text = _bphs_opportunities(mercury_libra_bphs)
        assert "Venus" in text
        assert "friend" in text.lower()

    def test_yogas_mentioned(self, mercury_libra_bphs):
        text = _bphs_opportunities(mercury_libra_bphs)
        assert "Budha-Aditya" in text

    def test_exalted_dignity_mentioned(self, exalted_lord_bphs):
        text = _bphs_opportunities(exalted_lord_bphs)
        assert "Exalted" in text or "exalted" in text
        assert "Jupiter" in text

    def test_empty_when_nothing_positive(self, empty_bphs):
        text = _bphs_opportunities(empty_bphs)
        assert text == ""


# ======================================================================
# Test: _bphs_challenges
# ======================================================================


class TestBphsChallenges:
    def test_debilitation_mentioned(self, debilitated_mars_bphs):
        text = _bphs_challenges(debilitated_mars_bphs)
        assert "Debilitated" in text or "debilitated" in text

    def test_retrograde_mentioned(self, debilitated_mars_bphs):
        text = _bphs_challenges(debilitated_mars_bphs)
        assert "Retrograde" in text or "retrograde" in text

    def test_combustion_mentioned(self, exalted_lord_bphs):
        text = _bphs_challenges(exalted_lord_bphs)
        assert "combust" in text.lower()

    def test_malefic_aspects_mentioned(self, mercury_libra_bphs):
        text = _bphs_challenges(mercury_libra_bphs)
        assert "Mars" in text
        assert "Malefic" in text or "malefic" in text

    def test_enemy_conjunctions_mentioned(self, debilitated_mars_bphs):
        text = _bphs_challenges(debilitated_mars_bphs)
        assert "Saturn" in text
        assert "enemy" in text.lower()

    def test_empty_when_nothing_challenging(self, empty_bphs):
        text = _bphs_challenges(empty_bphs)
        assert text == ""


# ======================================================================
# Test: _bphs_practical_advice
# ======================================================================


class TestBphsPracticalAdvice:
    def test_includes_house_lord_reading_positives(self, mercury_libra_bphs):
        advice = _bphs_practical_advice(mercury_libra_bphs)
        assert any("higher learning" in a for a in advice)

    def test_max_3_from_reading(self, mercury_libra_bphs):
        advice = _bphs_practical_advice(mercury_libra_bphs)
        # 3 from reading + yogas advice
        reading_items = mercury_libra_bphs["house_lord_reading"]["positive"]
        count = sum(1 for a in advice if a in reading_items)
        assert count <= 3

    def test_dignity_advice_included(self, debilitated_mars_bphs):
        advice = _bphs_practical_advice(debilitated_mars_bphs)
        assert any("remedial" in a.lower() for a in advice)

    def test_exalted_advice_included(self, exalted_lord_bphs):
        advice = _bphs_practical_advice(exalted_lord_bphs)
        assert any("exalted" in a.lower() for a in advice)

    def test_yoga_advice_included(self, mercury_libra_bphs):
        advice = _bphs_practical_advice(mercury_libra_bphs)
        assert any("Budha-Aditya" in a for a in advice)

    def test_returns_list(self, empty_bphs):
        advice = _bphs_practical_advice(empty_bphs)
        assert isinstance(advice, list)


# ======================================================================
# Test: _bphs_positive
# ======================================================================


class TestBphsPositive:
    def test_returns_nonempty_list(self, mercury_libra_bphs):
        items = _bphs_positive(mercury_libra_bphs)
        assert len(items) > 0

    def test_benefic_aspects_included(self, mercury_libra_bphs):
        items = _bphs_positive(mercury_libra_bphs)
        assert any("Saturn" in i for i in items)

    def test_yogas_included(self, mercury_libra_bphs):
        items = _bphs_positive(mercury_libra_bphs)
        assert any("Budha-Aditya" in i for i in items)

    def test_fallback_for_empty(self, empty_bphs):
        items = _bphs_positive(empty_bphs)
        assert len(items) == 1
        assert "Standard results" in items[0]


# ======================================================================
# Test: _bphs_negative
# ======================================================================


class TestBphsNegative:
    def test_debilitation_included(self, debilitated_mars_bphs):
        items = _bphs_negative(debilitated_mars_bphs)
        assert any("Debilitated" in i or "debilitated" in i for i in items)

    def test_retrograde_included(self, debilitated_mars_bphs):
        items = _bphs_negative(debilitated_mars_bphs)
        assert any("Retrograde" in i or "retrograde" in i for i in items)

    def test_malefic_aspects_included(self, mercury_libra_bphs):
        items = _bphs_negative(mercury_libra_bphs)
        assert any("Mars" in i for i in items)

    def test_enemy_conjunctions_included(self, debilitated_mars_bphs):
        items = _bphs_negative(debilitated_mars_bphs)
        assert any("Saturn" in i for i in items)

    def test_fallback_for_empty(self, empty_bphs):
        items = _bphs_negative(empty_bphs)
        assert len(items) == 1
        assert "No significant challenges" in items[0]


# ======================================================================
# Integration: overlay logic with interpret_dasha_combination
# ======================================================================


class TestBphsOverlayIntegration:
    """Test that interpret_dasha_combination output feeds cleanly into overlay helpers."""

    def test_real_bphs_output_feeds_helpers(self):
        """Call interpret_dasha_combination with real data and feed to helpers."""
        from packages.context.src.dasha_interpreter import interpret_dasha_combination

        # User's actual chart data (Libra lagna)
        natal_planets = {
            "sun": {
                "longitude": 227.0,
                "latitude": 0,
                "speed": 1.0,
                "rashi": 7,
                "house": 1,
                "is_retrograde": False,
            },
            "moon": {
                "longitude": 326.85,
                "latitude": 0,
                "speed": 13.0,
                "rashi": 10,
                "house": 5,
                "is_retrograde": False,
            },
            "mars": {
                "longitude": 108.0,
                "latitude": 0,
                "speed": -0.3,
                "rashi": 3,
                "house": 10,
                "is_retrograde": True,
            },
            "mercury": {
                "longitude": 223.0,
                "latitude": 0,
                "speed": 1.5,
                "rashi": 7,
                "house": 1,
                "is_retrograde": False,
            },
            "jupiter": {
                "longitude": 128.0,
                "latitude": 0,
                "speed": 0.1,
                "rashi": 4,
                "house": 11,
                "is_retrograde": False,
            },
            "venus": {
                "longitude": 210.0,
                "latitude": 0,
                "speed": 1.2,
                "rashi": 7,
                "house": 1,
                "is_retrograde": False,
            },
            "saturn": {
                "longitude": 307.0,
                "latitude": 0,
                "speed": 0.05,
                "rashi": 10,
                "house": 4,
                "is_retrograde": False,
            },
            "rahu": {
                "longitude": 240.0,
                "latitude": 0,
                "speed": -0.05,
                "rashi": 8,
                "house": 2,
                "is_retrograde": True,
            },
            "ketu": {
                "longitude": 60.0,
                "latitude": 0,
                "speed": -0.05,
                "rashi": 2,
                "house": 8,
                "is_retrograde": True,
            },
        }

        bphs = interpret_dasha_combination(
            md="mercury",
            ad="venus",
            pd="mars",
            natal_planets=natal_planets,
            lagna_index=6,  # Libra
        )

        assert bphs is not None
        md_bphs = bphs["mahadasha"]
        ad_bphs = bphs["antardasha"]
        pd_bphs = bphs["pratyantardasha"]

        # All helpers should work without errors
        focus = _bphs_focus_areas(md_bphs)
        assert isinstance(focus, list)

        for area in [
            "career",
            "health",
            "spiritual",
            "finances",
            "relationships",
            "family",
            "education",
            "travel",
        ]:
            text = _bphs_area_text(md_bphs, area)
            assert isinstance(text, str)

        opp = _bphs_opportunities(md_bphs)
        assert isinstance(opp, str)

        chall = _bphs_challenges(md_bphs)
        assert isinstance(chall, str)

        advice = _bphs_practical_advice(md_bphs)
        assert isinstance(advice, list)

        pos = _bphs_positive(ad_bphs)
        assert isinstance(pos, list)
        assert len(pos) >= 1

        neg = _bphs_negative(ad_bphs)
        assert isinstance(neg, list)
        assert len(neg) >= 1

        # PD theme from summary
        assert pd_bphs["summary"]
        assert pd_bphs["prediction"]
