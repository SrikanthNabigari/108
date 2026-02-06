"""Tests for packages/context/src/dasha_transit.py — Dasha-Transit Cross-Analysis Engine."""

from packages.context.src.dasha_transit import (
    HOUSE_THEMES,
    RASHI_LORDS,
    _angular_distance,
    _get_house_from_lagna,
    _get_houses_owned_from_lagna,
    _get_rashi_from_longitude,
    _merge_windows,
    _score_transit_activation,
    cross_analyze,
    find_activation_windows,
)

# Standard test birth data: Dec 3, 1992, 3:00 AM IST
# Lagna: Libra (6), Moon: Aquarius (10), Mercury MD (2019-2036)
NATAL_PLANETS = {
    "sun": {"longitude": 227.5, "rashi": 7},  # Scorpio
    "moon": {"longitude": 326.85, "rashi": 10},  # Aquarius
    "mars": {"longitude": 85.0, "rashi": 2},  # Gemini
    "mercury": {"longitude": 240.0, "rashi": 8},  # Sagittarius
    "jupiter": {"longitude": 145.0, "rashi": 4},  # Leo
    "venus": {"longitude": 210.0, "rashi": 7},  # Scorpio
    "saturn": {"longitude": 310.0, "rashi": 10},  # Aquarius
    "rahu": {"longitude": 170.0, "rashi": 5},  # Virgo
    "ketu": {"longitude": 350.0, "rashi": 11},  # Pisces
}

LAGNA_RASHI = 6  # Libra

CURRENT_DASHA = {
    "mahadasha": "mercury",
    "antardasha": "ketu",
    "pratyantardasha": "venus",
}


class TestHelpers:
    """Test helper functions."""

    def test_get_house_from_lagna_same_sign(self):
        assert _get_house_from_lagna(6, 6) == 1  # Libra lagna, planet in Libra

    def test_get_house_from_lagna_7th(self):
        assert _get_house_from_lagna(0, 6) == 7  # Aries from Libra = 7th

    def test_get_house_from_lagna_wraps(self):
        assert _get_house_from_lagna(5, 6) == 12  # Virgo from Libra = 12th

    def test_get_rashi_from_longitude_aries(self):
        assert _get_rashi_from_longitude(15.0) == 0

    def test_get_rashi_from_longitude_pisces(self):
        assert _get_rashi_from_longitude(350.0) == 11

    def test_get_rashi_from_longitude_boundary(self):
        assert _get_rashi_from_longitude(30.0) == 1  # Taurus starts at 30

    def test_angular_distance_same(self):
        assert _angular_distance(100.0, 100.0) == 0.0

    def test_angular_distance_opposite(self):
        assert _angular_distance(0.0, 180.0) == 180.0

    def test_angular_distance_wrap(self):
        assert abs(_angular_distance(350.0, 10.0) - 20.0) < 0.01

    def test_get_houses_owned_mars(self):
        # Mars owns Aries (0) and Scorpio (7)
        # From Libra (6) lagna: Aries = house 7, Scorpio = house 2
        houses = _get_houses_owned_from_lagna("mars", 6)
        assert 7 in houses
        assert 2 in houses

    def test_get_houses_owned_sun(self):
        # Sun owns Leo (4). From Libra (6): house 11
        houses = _get_houses_owned_from_lagna("sun", 6)
        assert 11 in houses

    def test_get_houses_owned_unknown_planet(self):
        houses = _get_houses_owned_from_lagna("unknown", 6)
        assert houses == []


class TestScoreTransitActivation:
    """Test transit activation scoring."""

    def test_conjunction_scores_high(self):
        # Transit planet in same rashi as natal dasha lord
        score = _score_transit_activation("jupiter", 8, "mercury", 8, 6)
        assert score >= 0.4

    def test_owned_sign_scores(self):
        # Mercury owns Gemini (2) and Virgo (5)
        # Transit in Gemini activates Mercury dasha
        score = _score_transit_activation("jupiter", 2, "mercury", 8, 6)
        assert score >= 0.3

    def test_aspect_scores(self):
        # Transit Jupiter in rashi 2, natal Mercury at rashi 8 -> distance is 6 houses
        # Jupiter doesn't have 6th aspect, but check 7th
        # rashi 8, aspect 7 from rashi 1 -> let's try proper setup
        # Jupiter at rashi 1, Mercury at rashi 7 -> distance 6, no aspect
        # Jupiter at rashi 1, Mercury at rashi 8 -> distance 7, 7th aspect!
        score = _score_transit_activation("jupiter", 1, "mercury", 8, 6)
        assert score >= 0.2

    def test_slow_mover_bonus(self):
        score_saturn = _score_transit_activation("saturn", 8, "mercury", 8, 6)
        score_venus = _score_transit_activation("venus", 8, "mercury", 8, 6)
        assert score_saturn > score_venus  # Saturn gets slow-mover bonus

    def test_no_activation(self):
        # Transit in unrelated sign, no aspect
        score = _score_transit_activation("venus", 3, "mercury", 8, 6)
        assert score == 0.0

    def test_max_score_capped_at_1(self):
        # Even with multiple hits, score should be <= 1.0
        score = _score_transit_activation("saturn", 2, "mercury", 2, 6)
        assert score <= 1.0


class TestCrossAnalyze:
    """Test the main cross_analyze function."""

    def test_returns_expected_keys(self):
        transits = {
            "jupiter": {"longitude": 240.0, "rashi": 8},
            "saturn": {"longitude": 310.0, "rashi": 10},
        }
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert "active_themes" in result
        assert "strongest_house" in result
        assert "most_active_planet" in result
        assert "overall_period_quality" in result
        assert "score" in result
        assert "house_scores" in result
        assert "dasha_lords" in result

    def test_active_themes_list(self):
        transits = {
            "jupiter": {"longitude": 240.0, "rashi": 8},
            "saturn": {"longitude": 65.0, "rashi": 2},
        }
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert isinstance(result["active_themes"], list)

    def test_dasha_lords_extracted(self):
        result = cross_analyze(
            NATAL_PLANETS,
            {"sun": {"longitude": 240.0, "rashi": 8}},
            CURRENT_DASHA,
            LAGNA_RASHI,
            10,
        )
        assert "mercury" in result["dasha_lords"]
        assert "ketu" in result["dasha_lords"]
        assert "venus" in result["dasha_lords"]

    def test_score_is_integer(self):
        transits = {"jupiter": {"longitude": 240.0, "rashi": 8}}
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert isinstance(result["score"], int)

    def test_score_range(self):
        transits = {"jupiter": {"longitude": 240.0, "rashi": 8}}
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert 0 <= result["score"] <= 100

    def test_strongest_house_valid(self):
        transits = {"jupiter": {"longitude": 240.0, "rashi": 8}}
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert 1 <= result["strongest_house"] <= 12

    def test_string_rashi_input(self):
        transits = {"jupiter": {"longitude": 240.0, "rashi": 8}}
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, "libra", "aquarius")
        assert "active_themes" in result

    def test_empty_transits(self):
        result = cross_analyze(NATAL_PLANETS, {}, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert result["score"] == 0
        assert result["active_themes"] == []

    def test_empty_dasha(self):
        result = cross_analyze(
            NATAL_PLANETS,
            {"jupiter": {"longitude": 240.0, "rashi": 8}},
            {"mahadasha": "", "antardasha": "", "pratyantardasha": ""},
            LAGNA_RASHI,
            10,
        )
        assert result["score"] == 0

    def test_theme_has_expected_fields(self):
        transits = {"jupiter": {"longitude": 240.0, "rashi": 8}}
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        if result["active_themes"]:
            theme = result["active_themes"][0]
            assert "theme" in theme
            assert "strength" in theme
            assert "dasha_trigger" in theme
            assert "transit_trigger" in theme
            assert "houses_activated" in theme

    def test_quality_is_string(self):
        transits = {"jupiter": {"longitude": 240.0, "rashi": 8}}
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert isinstance(result["overall_period_quality"], str)

    def test_with_many_transits(self):
        transits = {
            "sun": {"longitude": 290.0, "rashi": 9},
            "moon": {"longitude": 120.0, "rashi": 4},
            "mars": {"longitude": 65.0, "rashi": 2},
            "mercury": {"longitude": 280.0, "rashi": 9},
            "jupiter": {"longitude": 80.0, "rashi": 2},
            "venus": {"longitude": 310.0, "rashi": 10},
            "saturn": {"longitude": 340.0, "rashi": 11},
            "rahu": {"longitude": 350.0, "rashi": 11},
            "ketu": {"longitude": 170.0, "rashi": 5},
        }
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert result["score"] > 0
        assert len(result["active_themes"]) > 0

    def test_themes_sorted_by_strength(self):
        transits = {
            "jupiter": {"longitude": 240.0, "rashi": 8},
            "saturn": {"longitude": 65.0, "rashi": 2},
        }
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        themes = result["active_themes"]
        if len(themes) >= 2:
            assert themes[0]["strength"] >= themes[1]["strength"]

    def test_max_10_themes(self):
        # Create many transits to generate many themes
        transits = {
            p: {"longitude": float(i * 30 + 15), "rashi": i}
            for i, p in enumerate(
                ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
            )
        }
        result = cross_analyze(NATAL_PLANETS, transits, CURRENT_DASHA, LAGNA_RASHI, 10)
        assert len(result["active_themes"]) <= 10


class TestMergeWindows:
    """Test window merging logic."""

    def test_empty_windows(self):
        assert _merge_windows([]) == []

    def test_single_window(self):
        windows = [
            {
                "date": "2026-02-10",
                "score": 50,
                "quality": "growth",
                "strongest_house": 5,
                "most_active_planet": "jupiter",
            }
        ]
        result = _merge_windows(windows)
        assert len(result) == 1
        assert result[0]["start_date"] == "2026-02-10"
        assert result[0]["end_date"] == "2026-02-10"

    def test_consecutive_windows_merge(self):
        windows = [
            {
                "date": "2026-02-10",
                "score": 50,
                "quality": "growth",
                "strongest_house": 5,
                "most_active_planet": "jupiter",
            },
            {
                "date": "2026-02-17",
                "score": 60,
                "quality": "growth",
                "strongest_house": 5,
                "most_active_planet": "jupiter",
            },
        ]
        result = _merge_windows(windows)
        assert len(result) == 1
        assert result[0]["start_date"] == "2026-02-10"
        assert result[0]["end_date"] == "2026-02-17"
        assert result[0]["score"] == 60  # Peak score

    def test_non_consecutive_windows_separate(self):
        windows = [
            {
                "date": "2026-02-10",
                "score": 50,
                "quality": "growth",
                "strongest_house": 5,
                "most_active_planet": "jupiter",
            },
            {
                "date": "2026-03-10",
                "score": 60,
                "quality": "career",
                "strongest_house": 10,
                "most_active_planet": "saturn",
            },
        ]
        result = _merge_windows(windows)
        assert len(result) == 2


class TestFindActivationWindows:
    """Test find_activation_windows with real ephemeris."""

    def test_returns_list(self):
        result = find_activation_windows(
            NATAL_PLANETS,
            CURRENT_DASHA,
            "2026-02-01",
            "2026-02-28",
            LAGNA_RASHI,
        )
        assert isinstance(result, list)

    def test_window_has_expected_keys(self):
        result = find_activation_windows(
            NATAL_PLANETS,
            CURRENT_DASHA,
            "2026-02-01",
            "2026-02-28",
            LAGNA_RASHI,
        )
        if result:
            w = result[0]
            assert "start_date" in w
            assert "end_date" in w
            assert "score" in w
            assert "quality" in w

    def test_string_lagna(self):
        result = find_activation_windows(
            NATAL_PLANETS,
            CURRENT_DASHA,
            "2026-02-01",
            "2026-02-14",
            "libra",
        )
        assert isinstance(result, list)


class TestHouseThemes:
    """Test house themes data."""

    def test_all_12_houses_have_themes(self):
        for h in range(1, 13):
            assert h in HOUSE_THEMES
            assert len(HOUSE_THEMES[h]) > 0

    def test_rashi_lords_complete(self):
        for r in range(12):
            assert r in RASHI_LORDS
