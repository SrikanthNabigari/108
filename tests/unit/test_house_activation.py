"""Tests for the House Activation Engine.

Tests cover:
- check_double_transit: basic, same-sign, no-overlap, strength variants
- get_house_activations: 12 houses, score range, grades, planets, aspects, themes
- get_transit_snapshot: structure, double transit list, sorting, trend, summary
"""

from __future__ import annotations

from unittest.mock import patch

from packages.context.src.house_activation import (
    HOUSE_THEMES,
    check_double_transit,
    get_house_activations,
    get_transit_snapshot,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MOCK_TRANSITS: dict[str, dict] = {
    "sun": {
        "longitude": 315.0,
        "rashi_num": 10,
        "rashi": "aquarius",
        "speed": 1.0,
        "is_retrograde": False,
    },
    "moon": {
        "longitude": 45.0,
        "rashi_num": 1,
        "rashi": "taurus",
        "speed": 13.0,
        "is_retrograde": False,
    },
    "mars": {
        "longitude": 90.0,
        "rashi_num": 3,
        "rashi": "cancer",
        "speed": 0.5,
        "is_retrograde": False,
    },
    "mercury": {
        "longitude": 300.0,
        "rashi_num": 10,
        "rashi": "aquarius",
        "speed": 1.5,
        "is_retrograde": False,
    },
    "jupiter": {
        "longitude": 15.0,
        "rashi_num": 0,
        "rashi": "aries",
        "speed": 0.08,
        "is_retrograde": False,
    },
    "venus": {
        "longitude": 330.0,
        "rashi_num": 11,
        "rashi": "pisces",
        "speed": 1.2,
        "is_retrograde": False,
    },
    "saturn": {
        "longitude": 340.0,
        "rashi_num": 11,
        "rashi": "pisces",
        "speed": 0.03,
        "is_retrograde": False,
    },
    "rahu": {
        "longitude": 350.0,
        "rashi_num": 11,
        "rashi": "pisces",
        "speed": -0.05,
        "is_retrograde": True,
    },
    "ketu": {
        "longitude": 170.0,
        "rashi_num": 5,
        "rashi": "virgo",
        "speed": -0.05,
        "is_retrograde": True,
    },
}

LAGNA_LIBRA = 6  # Libra
MOON_AQUARIUS = 10  # Aquarius

MOCK_NATAL_PLANETS: dict[str, dict] = {
    "sun": {"longitude": 226.0, "rashi_num": 7, "speed": 1.0},
    "moon": {"longitude": 326.85, "rashi_num": 10, "speed": 13.0},
    "mars": {"longitude": 115.0, "rashi_num": 3, "speed": 0.5},
    "mercury": {"longitude": 220.0, "rashi_num": 7, "speed": 1.5},
    "jupiter": {"longitude": 125.0, "rashi_num": 4, "speed": 0.08},
    "venus": {"longitude": 240.0, "rashi_num": 8, "speed": 1.2},
    "saturn": {"longitude": 310.0, "rashi_num": 10, "speed": 0.03},
    "rahu": {"longitude": 190.0, "rashi_num": 6, "speed": -0.05},
    "ketu": {"longitude": 10.0, "rashi_num": 0, "speed": -0.05},
}


# ===========================================================================
# Tests for check_double_transit
# ===========================================================================


class TestCheckDoubleTransit:
    """Tests for the check_double_transit function."""

    def test_basic(self):
        """Jupiter in Aries (0), Saturn in Pisces (11), Lagna Libra (6).

        Jupiter is in house 7 (0 from 6 -> (0-6)%12+1 = 7).
        Jupiter aspects: 7th from 7=1, 5th from 7=11, 9th from 7=3 -> houses 1,3,11
        Plus occupation house 7. Jupiter influences: {7, 1, 3, 11}.

        Saturn is in house 6 (11 from 6 -> (11-6)%12+1 = 6).
        Saturn aspects: 7th from 6=12, 3rd from 6=8, 10th from 6=3 -> houses 12, 8, 3
        Plus occupation house 6. Saturn influences: {6, 12, 8, 3}.

        Overlap: house 3 (Jupiter aspects, Saturn aspects -> moderate).
        """
        result = check_double_transit(
            jupiter_rashi=0,
            saturn_rashi=11,
            lagna_rashi=6,
        )
        assert 3 in result
        assert result[3]["jupiter_influence"] == "aspects"
        assert result[3]["saturn_influence"] == "aspects"
        assert result[3]["strength"] == "moderate"

    def test_same_sign(self):
        """Both Jupiter and Saturn in same sign -> that house is 'strong'."""
        result = check_double_transit(
            jupiter_rashi=0,
            saturn_rashi=0,
            lagna_rashi=0,
        )
        # Both occupy house 1
        assert 1 in result
        assert result[1]["jupiter_influence"] == "occupies"
        assert result[1]["saturn_influence"] == "occupies"
        assert result[1]["strength"] == "strong"

    def test_no_overlap(self):
        """Find positions where no double transit occurs.

        Jupiter in Taurus (1), house 1 from Taurus lagna (1).
        Jupiter influences: house 1 (occ), 7 (7th), 5 (5th), 9 (9th) = {1,5,7,9}.

        Saturn in Gemini (2), house 2 from Taurus lagna.
        Saturn influences: house 2 (occ), 8 (7th), 4 (3rd), 11 (10th) = {2,4,8,11}.

        Intersection: {} -- no overlap.
        """
        result = check_double_transit(
            jupiter_rashi=1,
            saturn_rashi=2,
            lagna_rashi=1,
        )
        assert len(result) == 0

    def test_strength_strong_one_occupies_one_aspects(self):
        """One occupies and the other aspects -> strong."""
        # Jupiter in Aries (0), lagna Aries (0) -> Jupiter in house 1
        # Jupiter influences: {1 (occ), 5, 7, 9}
        # Saturn in Cancer (3), lagna Aries (0) -> Saturn in house 4
        # Saturn influences: {4 (occ), 10 (7th), 6 (3rd), 1 (10th from 4)}
        # Overlap: house 1: Jupiter occupies, Saturn aspects -> strong
        result = check_double_transit(
            jupiter_rashi=0,
            saturn_rashi=3,
            lagna_rashi=0,
        )
        assert 1 in result
        assert result[1]["jupiter_influence"] == "occupies"
        assert result[1]["saturn_influence"] == "aspects"
        assert result[1]["strength"] == "strong"

    def test_strength_moderate_both_aspect(self):
        """Both only aspect the house -> moderate."""
        # Jupiter in Aries (0), lagna Aries (0) -> house 1
        # Jupiter aspects houses: 5, 7, 9
        # Saturn in Cancer (3), lagna Aries (0) -> house 4
        # Saturn aspects houses: 6, 10, 1
        # House 10 is not in Jupiter aspects. House 6 is not either.
        # Let's find a house both only aspect:
        # Jupiter aspects {5,7,9}. Saturn aspects {6,10,1}.
        # No overlap on pure-aspect basis. Try different setup:

        # Jupiter in Taurus (1), lagna Aries (0) -> house 2
        # Jupiter aspects: 5th from 2=6, 7th from 2=8, 9th from 2=10 -> {6,8,10}
        # Saturn in Scorpio (7), lagna Aries (0) -> house 8
        # Saturn aspects: 3rd from 8=10, 7th from 8=2, 10th from 8=5 -> {2,5,10}
        # Overlap on aspects: house 10 (Jupiter aspects, Saturn aspects) -> moderate
        result = check_double_transit(
            jupiter_rashi=1,
            saturn_rashi=7,
            lagna_rashi=0,
        )
        assert 10 in result
        assert result[10]["jupiter_influence"] == "aspects"
        assert result[10]["saturn_influence"] == "aspects"
        assert result[10]["strength"] == "moderate"


# ===========================================================================
# Tests for get_house_activations
# ===========================================================================


class TestGetHouseActivations:
    """Tests for the get_house_activations function."""

    def test_returns_12_houses(self):
        """Always returns exactly 12 house dicts."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        assert len(result) == 12

    def test_score_range(self):
        """All scores should be between 0 and 100."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        for h in result:
            assert 0 <= h["score"] <= 100, f"House {h['house']} score {h['score']} out of range"

    def test_grade_thresholds(self):
        """Verify grade boundaries: highly_active >= 70, active >= 40, moderate >= 20, quiet < 20."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        for h in result:
            if h["score"] >= 70:
                assert h["grade"] == "highly_active"
            elif h["score"] >= 40:
                assert h["grade"] == "active"
            elif h["score"] >= 20:
                assert h["grade"] == "moderate"
            else:
                assert h["grade"] == "quiet"

    def test_planets_present(self):
        """Verify planets are assigned to correct houses."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        # Jupiter in Aries (0), lagna Libra (6) -> house 7
        house_7 = next(h for h in result if h["house"] == 7)
        assert "jupiter" in house_7["planets_present"]

        # Mars in Cancer (3), lagna Libra (6) -> (3-6)%12+1 = 10
        house_10 = next(h for h in result if h["house"] == 10)
        assert "mars" in house_10["planets_present"]

    def test_aspects_included(self):
        """Verify aspecting planets are listed."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        # Jupiter in house 7, aspects 5th(11), 7th(1), 9th(3)
        house_1 = next(h for h in result if h["house"] == 1)
        assert "jupiter" in house_1["planets_aspecting"]

    def test_without_chart(self):
        """chart=None still works (uses neutral ashtakavarga score of 7)."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS, chart=None)
        assert len(result) == 12
        # All houses should have ashtakavarga_sav = None since no chart provided
        for h in result:
            assert h["ashtakavarga_sav"] is None

    def test_with_slow_planets_score_higher(self):
        """Slow planets (Jupiter, Saturn, Rahu, Ketu) contribute more presence score."""
        # Create transits where a slow planet is in house 1 and a fast planet in house 2
        slow_transits = {
            "jupiter": {"longitude": 180.0, "rashi_num": 6, "speed": 0.08, "is_retrograde": False},
        }
        fast_transits = {
            "sun": {"longitude": 180.0, "rashi_num": 6, "speed": 1.0, "is_retrograde": False},
        }
        # Lagna 6 (Libra) -> rashi 6 is house 1
        slow_result = get_house_activations(slow_transits, 6, 10)
        fast_result = get_house_activations(fast_transits, 6, 10)

        slow_h1 = next(h for h in slow_result if h["house"] == 1)
        fast_h1 = next(h for h in fast_result if h["house"] == 1)

        # Slow planet contributes 15 presence vs fast planet 8
        assert slow_h1["score"] > fast_h1["score"]

    def test_themes(self):
        """Each house has themes from HOUSE_THEMES."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        for h in result:
            assert h["themes"] == HOUSE_THEMES[h["house"]]

    def test_house_numbers_sequential(self):
        """Houses should be numbered 1-12 in order."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        houses = [h["house"] for h in result]
        assert houses == list(range(1, 13))

    def test_sign_calculation(self):
        """Sign for each house is (lagna_rashi + house - 1) % 12."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        for h in result:
            expected_sign = (LAGNA_LIBRA + h["house"] - 1) % 12
            assert h["sign"] == expected_sign

    def test_double_transit_flag(self):
        """Houses with double transit should have double_transit=True."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        # Jupiter in Aries (0), Saturn in Pisces (11), lagna Libra (6)
        dt = check_double_transit(0, 11, LAGNA_LIBRA)
        for h in result:
            if h["house"] in dt:
                assert h["double_transit"] is True
            else:
                assert h["double_transit"] is False

    def test_summary_nonempty(self):
        """Each house summary should be a non-empty string."""
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS)
        for h in result:
            assert isinstance(h["summary"], str)
            assert len(h["summary"]) > 0


# ===========================================================================
# Tests for get_transit_snapshot
# ===========================================================================


class TestGetTransitSnapshot:
    """Tests for the get_transit_snapshot function."""

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_structure(self, mock_positions):
        """Verify all top-level keys present in snapshot."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        expected_keys = {
            "timestamp",
            "transit_positions",
            "house_activations",
            "double_transit_houses",
            "most_active_houses",
            "most_quiet_houses",
            "active_aspects",
            "gochara_summary",
            "overall_trend",
            "summary",
        }
        assert set(result.keys()) == expected_keys

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_double_transit_list(self, mock_positions):
        """Houses with double transit appear in the list."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        dt_houses = result["double_transit_houses"]
        assert isinstance(dt_houses, list)
        # Verify consistency with house_activations
        for h in result["house_activations"]:
            if h["double_transit"]:
                assert h["house"] in dt_houses

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_sorting(self, mock_positions):
        """most_active_houses sorted by score descending (top 3)."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        assert len(result["most_active_houses"]) == 3
        assert len(result["most_quiet_houses"]) == 2

        # Verify ordering: scores of most_active_houses should be >= scores of most_quiet_houses
        activations_by_house = {h["house"]: h["score"] for h in result["house_activations"]}
        active_scores = [activations_by_house[h] for h in result["most_active_houses"]]
        quiet_scores = [activations_by_house[h] for h in result["most_quiet_houses"]]
        assert min(active_scores) >= max(quiet_scores)

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_overall_trend_favorable(self, mock_positions):
        """Test favorable trend when top houses have high scores."""
        # All planets concentrated to create high scores
        high_transits = {
            "jupiter": {"longitude": 180.0, "rashi_num": 6, "speed": 0.08, "is_retrograde": False},
            "saturn": {"longitude": 180.0, "rashi_num": 6, "speed": 0.03, "is_retrograde": False},
            "rahu": {"longitude": 180.0, "rashi_num": 6, "speed": -0.05, "is_retrograde": True},
            "ketu": {"longitude": 0.0, "rashi_num": 0, "speed": -0.05, "is_retrograde": True},
            "sun": {"longitude": 180.0, "rashi_num": 6, "speed": 1.0, "is_retrograde": False},
            "moon": {"longitude": 180.0, "rashi_num": 6, "speed": 13.0, "is_retrograde": False},
            "mars": {"longitude": 180.0, "rashi_num": 6, "speed": 0.5, "is_retrograde": False},
            "mercury": {"longitude": 180.0, "rashi_num": 6, "speed": 1.5, "is_retrograde": False},
            "venus": {"longitude": 180.0, "rashi_num": 6, "speed": 1.2, "is_retrograde": False},
        }
        mock_positions.return_value = high_transits
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=6,
            moon_rashi=10,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        # With all planets in house 1, the top house should be very active
        assert result["overall_trend"] in ("favorable", "mixed")

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_overall_trend_challenging(self, mock_positions):
        """Test challenging trend with sparse positions."""
        sparse_transits = {
            "sun": {"longitude": 0.0, "rashi_num": 0, "speed": 1.0, "is_retrograde": False},
            "moon": {"longitude": 30.0, "rashi_num": 1, "speed": 13.0, "is_retrograde": False},
        }
        mock_positions.return_value = sparse_transits
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        # With only 2 fast planets spread across 2 houses, most houses will be low-scoring
        assert result["overall_trend"] in ("challenging", "mixed")

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_summary_nonempty(self, mock_positions):
        """Summary is a non-empty string."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_house_activations_count(self, mock_positions):
        """House activations always contains 12 entries."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        assert len(result["house_activations"]) == 12

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_timestamp_present(self, mock_positions):
        """Snapshot includes a valid ISO timestamp."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
        assert "T" in result["timestamp"]  # ISO format


class TestGocharaSummary:
    """Tests for gochara_summary in get_transit_snapshot."""

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_gochara_summary_present(self, mock_positions):
        """Snapshot includes gochara_summary with entries for all 9 planets."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        assert "gochara_summary" in result
        gochara = result["gochara_summary"]
        assert isinstance(gochara, list)
        assert len(gochara) == 9  # all 9 planets

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_gochara_entry_keys(self, mock_positions):
        """Each gochara entry has required keys."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        required_keys = {
            "planet",
            "sign",
            "house_from_moon",
            "is_favorable",
            "has_vedha",
            "vedha_by",
            "net_effect",
            "effects",
            "is_retrograde",
            "degree_in_sign",
            "bav_score",
        }
        for entry in result["gochara_summary"]:
            assert required_keys.issubset(set(entry.keys())), f"Missing keys in {entry['planet']}"

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_gochara_house_from_moon_range(self, mock_positions):
        """house_from_moon should be 1-12."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        for entry in result["gochara_summary"]:
            assert 1 <= entry["house_from_moon"] <= 12

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_gochara_bav_none_without_chart(self, mock_positions):
        """BAV score is None when no chart is provided."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
            chart=None,
        )
        for entry in result["gochara_summary"]:
            assert entry["bav_score"] is None

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_gochara_net_effect_values(self, mock_positions):
        """net_effect is either 'favorable' or 'unfavorable'."""
        mock_positions.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460400.5,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=MOCK_NATAL_PLANETS,
        )
        for entry in result["gochara_summary"]:
            assert entry["net_effect"] in ("favorable", "unfavorable")
