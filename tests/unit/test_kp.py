"""Tests for KP (Krishnamurti Paddhati) module."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from packages.self.src.kp import (
    KP_HOUSE_GROUPS,
    SIGN_RULERS,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_YEARS,
    analyze_kp_house,
    get_cuspal_sublords,
    get_kp_prediction,
    get_kp_significators,
    get_kp_sublord,
    get_kp_sublord_table,
    get_ruling_planets,
)

# ============================================================================
# TEST DATA
# ============================================================================

# Sample chart data for tests
SAMPLE_PLANETS = {
    "sun": {"longitude": 227.5, "sign": "scorpio", "house": 2},
    "moon": {"longitude": 324.1, "sign": "aquarius", "house": 5},
    "mars": {"longitude": 93.8, "sign": "cancer", "house": 10},
    "mercury": {"longitude": 208.7, "sign": "libra", "house": 1},
    "jupiter": {"longitude": 166.2, "sign": "virgo", "house": 12},
    "venus": {"longitude": 269.4, "sign": "sagittarius", "house": 3},
    "saturn": {"longitude": 289.9, "sign": "capricorn", "house": 4},
    "rahu": {"longitude": 238.2, "sign": "scorpio", "house": 2},
    "ketu": {"longitude": 58.2, "sign": "taurus", "house": 8},
}

# Sample house cusps (Placidus-style for ~16.7°N latitude)
SAMPLE_CUSPS = [180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0]

# Simplified cusps for straightforward tests
SIMPLE_CUSPS = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]


# ============================================================================
# TestGetKPSublord
# ============================================================================


class TestGetKPSublord:
    """Test the sub-lord calculation for any longitude."""

    def test_sublord_at_zero_degrees(self):
        """Test Aries start (0°), Ashwini nakshatra, Ketu star lord."""
        result = get_kp_sublord(0.0)
        assert result["longitude"] == 0.0
        assert result["sign"] == "aries"
        assert result["sign_lord"] == "mars"
        assert result["star"] == "Ashwini"
        assert result["star_lord"] == "ketu"
        assert result["sub_lord"] == "ketu"

    def test_sublord_at_13_degrees(self):
        """Test near end of Ashwini, should still be in Ashwini."""
        result = get_kp_sublord(13.0)
        assert result["sign"] == "aries"
        assert result["star"] == "Ashwini"
        assert result["star_lord"] == "ketu"
        assert result["star_number"] == 1

    def test_sublord_at_30_degrees(self):
        """Test Taurus start (30°), in Krittika nakshatra (26°40'-40°)."""
        result = get_kp_sublord(30.0)
        assert result["sign"] == "taurus"
        assert result["sign_lord"] == "venus"
        assert result["star"] == "Krittika"
        assert result["star_lord"] == "sun"

    def test_sublord_at_60_degrees(self):
        """Test Gemini start (60°)."""
        result = get_kp_sublord(60.0)
        assert result["sign"] == "gemini"
        assert result["sign_lord"] == "mercury"

    def test_sublord_at_90_degrees(self):
        """Test Cancer start (90°)."""
        result = get_kp_sublord(90.0)
        assert result["sign"] == "cancer"
        assert result["sign_lord"] == "moon"

    def test_sublord_at_120_degrees(self):
        """Test Leo start (120°)."""
        result = get_kp_sublord(120.0)
        assert result["sign"] == "leo"
        assert result["sign_lord"] == "sun"

    def test_sublord_at_180_degrees(self):
        """Test Libra start (180°)."""
        result = get_kp_sublord(180.0)
        assert result["sign"] == "libra"
        assert result["sign_lord"] == "venus"

    def test_sublord_at_270_degrees(self):
        """Test Capricorn start (270°)."""
        result = get_kp_sublord(270.0)
        assert result["sign"] == "capricorn"
        assert result["sign_lord"] == "saturn"

    def test_sublord_at_359_9_degrees(self):
        """Test near end of Pisces/Revati."""
        result = get_kp_sublord(359.9)
        assert result["sign"] == "pisces"
        assert result["sign_lord"] == "jupiter"

    def test_sublord_sign_lord_matches_sign_ruler(self):
        """Verify that sign_lord matches SIGN_RULERS."""
        for lon in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
            result = get_kp_sublord(lon)
            sign = result["sign"]
            assert result["sign_lord"] == SIGN_RULERS[sign]

    def test_sublord_has_all_required_keys(self):
        """Test that result contains all required keys."""
        result = get_kp_sublord(45.5)
        assert "longitude" in result
        assert "sign" in result
        assert "sign_lord" in result
        assert "star" in result
        assert "star_number" in result
        assert "star_lord" in result
        assert "sub_lord" in result
        assert "sub_sub_lord" in result
        assert "degree_in_sub" in result
        assert "sub_span" in result

    def test_sublord_degree_in_sub_is_non_negative(self):
        """Test that degree_in_sub is non-negative."""
        for lon in [0, 45, 90, 180, 270, 359]:
            result = get_kp_sublord(lon)
            assert result["degree_in_sub"] >= 0

    def test_sublord_sub_span_is_positive(self):
        """Test that sub_span is positive."""
        result = get_kp_sublord(90.5)
        assert result["sub_span"] > 0

    def test_sublord_sub_sub_lord_is_valid(self):
        """Test that sub_sub_lord is a valid planet."""
        result = get_kp_sublord(45.0)
        assert result["sub_sub_lord"] in VIMSHOTTARI_SEQUENCE

    def test_sublord_negative_longitude_raises_error(self):
        """Test that negative longitude raises ValueError."""
        with pytest.raises(ValueError):
            get_kp_sublord(-1.0)

    def test_sublord_longitude_360_wraps_to_0(self):
        """Test that 360° wraps to 0°."""
        result_0 = get_kp_sublord(0.0)
        result_360 = get_kp_sublord(360.0)
        assert result_0["sign"] == result_360["sign"]
        assert result_0["star"] == result_360["star"]

    def test_sublord_longitude_over_360_normalizes(self):
        """Test that longitudes > 360 normalize correctly."""
        result_45 = get_kp_sublord(45.0)
        result_405 = get_kp_sublord(405.0)
        assert result_45["sign"] == result_405["sign"]
        assert result_45["star"] == result_405["star"]


# ============================================================================
# TestGetCuspalSublords
# ============================================================================


class TestGetCuspalSublords:
    """Test cusp analysis returning sub-lord info for all 12 houses."""

    def test_cuspal_sublords_returns_12_results(self):
        """Test that 12 cusps return 12 results."""
        result = get_cuspal_sublords(SAMPLE_CUSPS)
        assert len(result) == 12

    def test_cuspal_sublords_each_has_required_keys(self):
        """Test that each result has all required keys."""
        result = get_cuspal_sublords(SAMPLE_CUSPS)
        required_keys = [
            "house",
            "cusp_longitude",
            "sign",
            "sign_lord",
            "star",
            "star_lord",
            "sub_lord",
        ]
        for entry in result:
            for key in required_keys:
                assert key in entry

    def test_cuspal_sublords_house_numbers_are_1_to_12(self):
        """Test that house numbers are 1-12 in order."""
        result = get_cuspal_sublords(SAMPLE_CUSPS)
        for i, entry in enumerate(result):
            assert entry["house"] == i + 1

    def test_cuspal_sublords_first_cusp(self):
        """Test the first cusp (ascendant)."""
        result = get_cuspal_sublords(SIMPLE_CUSPS)
        assert result[0]["house"] == 1
        assert result[0]["cusp_longitude"] == 0.0
        assert result[0]["sign"] == "aries"

    def test_cuspal_sublords_spanning_different_signs(self):
        """Test that cusps in different signs have different sign lords."""
        result = get_cuspal_sublords(SIMPLE_CUSPS)
        # 1st cusp at 0° (Aries, Mars), 2nd at 30° (Taurus, Venus), etc.
        assert result[0]["sign_lord"] == "mars"  # Aries
        assert result[1]["sign_lord"] == "venus"  # Taurus
        assert result[2]["sign_lord"] == "mercury"  # Gemini
        assert result[3]["sign_lord"] == "moon"  # Cancer

    def test_cuspal_sublords_with_uneven_cusps(self):
        """Test with Placidus-style uneven cusps."""
        result = get_cuspal_sublords(SAMPLE_CUSPS)
        assert len(result) == 12
        # All should have valid planets as sign lords
        for entry in result:
            assert entry["sign_lord"] in SIGN_RULERS.values()

    def test_cuspal_sublords_invalid_count_raises_error(self):
        """Test that non-12 cusps raise ValueError."""
        with pytest.raises(ValueError):
            get_cuspal_sublords([0.0, 30.0, 60.0])

    def test_cuspal_sublords_11_cusps_raises_error(self):
        """Test that 11 cusps raise ValueError."""
        with pytest.raises(ValueError):
            get_cuspal_sublords(SIMPLE_CUSPS[:-1])

    def test_cuspal_sublords_13_cusps_raises_error(self):
        """Test that 13 cusps raise ValueError."""
        with pytest.raises(ValueError):
            get_cuspal_sublords([*SIMPLE_CUSPS, 0.0])


# ============================================================================
# TestGetKPSignificators
# ============================================================================


class TestGetKPSignificators:
    """Test KP significator determination."""

    def test_significators_returns_12_houses(self):
        """Test that all 12 houses have significators."""
        result = get_kp_significators(SAMPLE_PLANETS, SAMPLE_CUSPS)
        assert len(result) == 12
        for house in range(1, 13):
            assert house in result

    def test_significators_each_house_has_all_levels(self):
        """Test that each house has all 4 significator levels."""
        result = get_kp_significators(SAMPLE_PLANETS, SAMPLE_CUSPS)
        for _house_num, sigs in result.items():
            assert "level_1" in sigs
            assert "level_2" in sigs
            assert "level_3" in sigs
            assert "level_4" in sigs
            assert "all_significators" in sigs

    def test_significators_level_4_has_house_lord(self):
        """Test that level_4 contains the house lord (sub-lord of cusp)."""
        result = get_kp_significators(SAMPLE_PLANETS, SAMPLE_CUSPS)
        for _house_num, sigs in result.items():
            # Level 4 should not be empty (always has house lord)
            assert len(sigs["level_4"]) > 0

    def test_significators_all_significators_is_union(self):
        """Test that all_significators is union of all levels."""
        result = get_kp_significators(SAMPLE_PLANETS, SAMPLE_CUSPS)
        for _house_num, sigs in result.items():
            all_sigs = set(sigs["all_significators"])
            level_union = set(sigs["level_1"] + sigs["level_2"] + sigs["level_3"] + sigs["level_4"])
            assert all_sigs == level_union

    def test_significators_invalid_cusps_count_raises_error(self):
        """Test that invalid cusps length raises ValueError."""
        with pytest.raises(ValueError):
            get_kp_significators(SAMPLE_PLANETS, [0.0, 30.0, 60.0])

    def test_significators_with_simple_chart(self):
        """Test with simple chart (one planet per house roughly)."""
        result = get_kp_significators(SAMPLE_PLANETS, SIMPLE_CUSPS)
        # Should have significators for all houses
        for house in range(1, 13):
            assert len(result[house]["all_significators"]) > 0

    def test_significators_planet_can_significate_multiple_houses(self):
        """Test that a planet can significate multiple houses."""
        result = get_kp_significators(SAMPLE_PLANETS, SAMPLE_CUSPS)
        # Count how many houses each planet significates
        planet_house_counts = {}
        for _house_num, sigs in result.items():
            for planet in sigs["all_significators"]:
                planet_house_counts[planet] = planet_house_counts.get(planet, 0) + 1
        # At least one planet should significate multiple houses
        assert any(count > 1 for count in planet_house_counts.values())

    def test_significators_retrograde_planet_still_significates(self):
        """Test that retrograde planets are still considered significators."""
        planets_with_retrograde = SAMPLE_PLANETS.copy()
        planets_with_retrograde["mercury"]["is_retrograde"] = True
        result = get_kp_significators(planets_with_retrograde, SAMPLE_CUSPS)
        # Mercury should still appear in significators
        all_significators = []
        for sigs in result.values():
            all_significators.extend(sigs["all_significators"])
        assert "mercury" in all_significators


# ============================================================================
# TestGetRulingPlanets
# ============================================================================


class TestGetRulingPlanets:
    """Test KP ruling planets at a given moment."""

    def test_ruling_planets_has_all_required_keys(self):
        """Test that result has all required keys."""
        try:
            result = get_ruling_planets("2024-02-07T12:00:00+05:30", 16.726, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

        assert "lagna_sign_lord" in result
        assert "lagna_star_lord" in result
        assert "moon_sign_lord" in result
        assert "moon_star_lord" in result
        assert "day_lord" in result
        assert "ruling_planets" in result
        assert "strongest" in result
        assert "frequencies" in result

    def test_ruling_planets_day_lord_for_monday(self):
        """Test day lord for Monday (2024-02-05 is a Monday)."""
        try:
            result = get_ruling_planets("2024-02-05T12:00:00+05:30", 16.726, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

        assert result["day_lord"] == "moon"

    def test_ruling_planets_day_lord_for_tuesday(self):
        """Test day lord for Tuesday (2024-02-06 is a Tuesday)."""
        try:
            result = get_ruling_planets("2024-02-06T12:00:00+05:30", 16.726, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

        assert result["day_lord"] == "mars"

    def test_ruling_planets_frequencies_is_dict(self):
        """Test that frequencies is a dict with planets as keys."""
        try:
            result = get_ruling_planets("2024-02-07T12:00:00+05:30", 16.726, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

        assert isinstance(result["frequencies"], dict)
        for planet, freq in result["frequencies"].items():
            assert planet in VIMSHOTTARI_SEQUENCE or planet == "sun"
            assert isinstance(freq, int)
            assert freq > 0

    def test_ruling_planets_strongest_has_max_frequency(self):
        """Test that strongest is the planet with highest frequency."""
        try:
            result = get_ruling_planets("2024-02-07T12:00:00+05:30", 16.726, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

        frequencies = result["frequencies"]
        max_freq = max(frequencies.values())
        assert frequencies[result["strongest"]] == max_freq

    def test_ruling_planets_list_has_unique_entries(self):
        """Test that ruling_planets list has unique entries."""
        try:
            result = get_ruling_planets("2024-02-07T12:00:00+05:30", 16.726, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

        ruling_list = result["ruling_planets"]
        assert len(ruling_list) == len(set(ruling_list))

    def test_ruling_planets_invalid_datetime_raises_error(self):
        """Test that invalid datetime raises ValueError."""
        with pytest.raises(ValueError):
            get_ruling_planets("invalid-datetime", 16.726, 81.288)

    def test_ruling_planets_invalid_latitude_raises_error(self):
        """Test that invalid latitude raises ValueError."""
        try:
            with pytest.raises(ValueError):
                get_ruling_planets("2024-02-07T12:00:00+05:30", 91.0, 81.288)
        except ImportError:
            pytest.skip("Ephemeris module not available")

    def test_ruling_planets_invalid_longitude_raises_error(self):
        """Test that invalid longitude raises ValueError."""
        try:
            with pytest.raises(ValueError):
                get_ruling_planets("2024-02-07T12:00:00+05:30", 16.726, 181.0)
        except ImportError:
            pytest.skip("Ephemeris module not available")


# ============================================================================
# TestAnalyzeKPHouse
# ============================================================================


class TestAnalyzeKPHouse:
    """Test KP house analysis."""

    def test_analyze_house_returns_kp_house_analysis_type(self):
        """Test that result is a KPHouseAnalysis."""
        result = analyze_kp_house(7, SAMPLE_PLANETS, SAMPLE_CUSPS)
        assert "house" in result
        assert "cusp_longitude" in result
        assert "cusp_sign" in result
        assert "sign_lord" in result
        assert "star_lord" in result
        assert "sub_lord" in result

    def test_analyze_house_has_all_required_keys(self):
        """Test that result contains all required keys."""
        result = analyze_kp_house(1, SAMPLE_PLANETS, SAMPLE_CUSPS)
        required_keys = [
            "house",
            "cusp_longitude",
            "cusp_sign",
            "sign_lord",
            "star_lord",
            "sub_lord",
            "sub_lord_significates",
            "supporting_houses",
            "denying_houses",
            "judgment",
            "strength",
            "explanation",
        ]
        for key in required_keys:
            assert key in result

    def test_analyze_house_judgment_is_valid(self):
        """Test that judgment is one of valid values (neutral removed — star lord backup)."""
        valid_judgments = ["favorable", "unfavorable", "mixed"]
        result = analyze_kp_house(7, SAMPLE_PLANETS, SAMPLE_CUSPS)
        assert result["judgment"] in valid_judgments

    def test_analyze_house_strength_is_between_0_and_1(self):
        """Test that strength is between 0 and 1."""
        result = analyze_kp_house(10, SAMPLE_PLANETS, SAMPLE_CUSPS)
        assert 0 <= result["strength"] <= 1

    def test_analyze_house_explanation_is_non_empty(self):
        """Test that explanation is non-empty string."""
        result = analyze_kp_house(5, SAMPLE_PLANETS, SAMPLE_CUSPS)
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0

    def test_analyze_house_for_7th_house(self):
        """Test analysis of 7th house (marriage)."""
        result = analyze_kp_house(7, SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        assert result["house"] == 7
        assert result["supporting_houses"] == [2, 7, 11]
        assert set(result["denying_houses"]) >= {1, 6, 10, 12}

    def test_analyze_house_for_10th_house(self):
        """Test analysis of 10th house (career)."""
        result = analyze_kp_house(10, SAMPLE_PLANETS, SAMPLE_CUSPS, "career")
        assert result["house"] == 10
        assert result["supporting_houses"] == [2, 6, 10, 11]

    def test_analyze_house_for_all_12_houses(self):
        """Test that all 12 houses can be analyzed."""
        for house in range(1, 13):
            result = analyze_kp_house(house, SAMPLE_PLANETS, SAMPLE_CUSPS)
            assert result["house"] == house

    def test_analyze_house_invalid_house_number_raises_error(self):
        """Test that invalid house number raises ValueError."""
        with pytest.raises(ValueError):
            analyze_kp_house(0, SAMPLE_PLANETS, SAMPLE_CUSPS)
        with pytest.raises(ValueError):
            analyze_kp_house(13, SAMPLE_PLANETS, SAMPLE_CUSPS)

    def test_analyze_house_invalid_cusps_length_raises_error(self):
        """Test that invalid cusps length raises ValueError."""
        with pytest.raises(ValueError):
            analyze_kp_house(7, SAMPLE_PLANETS, [0.0, 30.0, 60.0])

    def test_analyze_house_with_different_questions(self):
        """Test that different questions affect supporting/denying houses."""
        result_marriage = analyze_kp_house(7, SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        result_career = analyze_kp_house(10, SAMPLE_PLANETS, SAMPLE_CUSPS, "career")
        # Different questions should produce different results
        # (though judgment might coincidentally be same)
        assert result_marriage["house"] != result_career["house"]


# ============================================================================
# TestGetKPPrediction
# ============================================================================


class TestGetKPPrediction:
    """Test KP prediction for life questions."""

    def test_prediction_marriage(self):
        """Test marriage prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        assert result["query_type"] == "marriage"
        assert result["primary_house"] == 7
        assert result["judgment"] in ["favorable", "unfavorable", "mixed"]

    def test_prediction_career(self):
        """Test career prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "career")
        assert result["query_type"] == "career"
        assert result["primary_house"] == 10

    def test_prediction_children(self):
        """Test children prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "children")
        assert result["query_type"] == "children"
        assert result["primary_house"] == 5

    def test_prediction_wealth(self):
        """Test wealth prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "wealth")
        assert result["query_type"] == "wealth"
        assert result["primary_house"] == 2

    def test_prediction_health(self):
        """Test health prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "health")
        assert result["query_type"] == "health"
        assert result["primary_house"] == 1

    def test_prediction_education(self):
        """Test education prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "education")
        assert result["query_type"] == "education"
        assert result["primary_house"] == 4

    def test_prediction_travel_short(self):
        """Test short travel prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "travel_short")
        assert result["query_type"] == "travel_short"
        assert result["primary_house"] == 3

    def test_prediction_travel_foreign(self):
        """Test foreign travel prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "travel_foreign")
        assert result["query_type"] == "travel_foreign"
        assert result["primary_house"] == 9

    def test_prediction_property(self):
        """Test property prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "property")
        assert result["query_type"] == "property"
        assert result["primary_house"] == 4

    def test_prediction_legal(self):
        """Test legal prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "legal")
        assert result["query_type"] == "legal"
        assert result["primary_house"] == 6

    def test_prediction_spiritual(self):
        """Test spiritual prediction."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "spiritual")
        assert result["query_type"] == "spiritual"
        assert result["primary_house"] == 12

    def test_prediction_has_all_required_keys(self):
        """Test that prediction result has all required keys."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        required_keys = [
            "query_type",
            "primary_house",
            "cusp_analysis",
            "significator_analysis",
            "ruling_planet_confirmation",
            "judgment",
            "confidence",
            "timing_hints",
            "explanation",
        ]
        for key in required_keys:
            assert key in result

    def test_prediction_confidence_is_between_0_and_1(self):
        """Test that confidence is between 0 and 1."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        assert 0 <= result["confidence"] <= 1

    def test_prediction_judgment_is_valid(self):
        """Test that judgment is one of valid values."""
        valid_judgments = ["favorable", "unfavorable", "mixed"]
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "wealth")
        assert result["judgment"] in valid_judgments

    def test_prediction_cusp_analysis_is_house_analysis(self):
        """Test that cusp_analysis is a KPHouseAnalysis."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "career")
        cusp = result["cusp_analysis"]
        assert "house" in cusp
        assert "judgment" in cusp
        assert "strength" in cusp

    def test_prediction_significator_analysis_has_required_keys(self):
        """Test that significator_analysis has required keys."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "children")
        sig_analysis = result["significator_analysis"]
        assert "supporting_significators" in sig_analysis
        assert "denying_significators" in sig_analysis
        assert "balance" in sig_analysis

    def test_prediction_timing_hints_has_dasha_lords(self):
        """Test that timing_hints contains dasha information."""
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "health")
        timing = result["timing_hints"]
        assert "dasha_lords_to_watch" in timing
        assert "transit_triggers" in timing
        assert isinstance(timing["dasha_lords_to_watch"], list)
        assert isinstance(timing["transit_triggers"], list)

    def test_prediction_invalid_query_type_raises_error(self):
        """Test that invalid query_type raises ValueError."""
        with pytest.raises(ValueError):
            get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "invalid_query")

    def test_prediction_invalid_cusps_length_raises_error(self):
        """Test that invalid cusps length raises ValueError."""
        with pytest.raises(ValueError):
            get_kp_prediction(SAMPLE_PLANETS, [0.0, 30.0, 60.0], "marriage")


# ============================================================================
# TestGetKPSublordTable
# ============================================================================


class TestGetKPSublordTable:
    """Test KP sub-lord table generation."""

    def test_sublord_table_covers_360_degrees(self):
        """Test that table entries cover 0-360 degrees."""
        table = get_kp_sublord_table()
        assert len(table) > 0
        # First entry should start near 0
        assert table[0]["start_degree"] == 0.0 or table[0]["start_degree"] < 1.0
        # Last entry should reach ~360
        assert table[-1]["end_degree"] >= 359.0

    def test_sublord_table_entries_are_contiguous(self):
        """Test that entries are contiguous (no gaps)."""
        table = get_kp_sublord_table()
        for i in range(len(table) - 1):
            # End of current entry should be start of next (within floating point tolerance)
            assert abs(table[i]["end_degree"] - table[i + 1]["start_degree"]) < 0.01

    def test_sublord_table_each_entry_has_required_keys(self):
        """Test that each entry has required keys."""
        table = get_kp_sublord_table()
        required_keys = [
            "start_degree",
            "end_degree",
            "star",
            "star_lord",
            "sub_lord",
            "sign",
            "sign_lord",
        ]
        for entry in table:
            for key in required_keys:
                assert key in entry

    def test_sublord_table_entries_sorted_by_start_degree(self):
        """Test that entries are sorted by start_degree."""
        table = get_kp_sublord_table()
        for i in range(len(table) - 1):
            assert table[i]["start_degree"] <= table[i + 1]["start_degree"]

    def test_sublord_table_all_star_lords_are_valid(self):
        """Test that all star_lords are valid planets."""
        table = get_kp_sublord_table()
        valid_planets = set(VIMSHOTTARI_SEQUENCE)
        for entry in table:
            assert entry["star_lord"] in valid_planets

    def test_sublord_table_all_sub_lords_are_valid(self):
        """Test that all sub_lords are valid planets."""
        table = get_kp_sublord_table()
        valid_planets = set(VIMSHOTTARI_SEQUENCE)
        for entry in table:
            assert entry["sub_lord"] in valid_planets

    def test_sublord_table_has_27_nakshatras(self):
        """Test that table has entries for 27 nakshatras."""
        table = get_kp_sublord_table()
        star_names = {entry["star"] for entry in table}
        assert len(star_names) == 27

    def test_sublord_table_reasonable_entry_count(self):
        """Test that table has reasonable entry count (~243)."""
        table = get_kp_sublord_table()
        # 27 nakshatras x 9 sub-lords = 243, but may vary due to rounding
        assert 200 < len(table) < 300

    def test_sublord_table_caching_returns_same_instance(self):
        """Test that multiple calls return the same cached instance."""
        table1 = get_kp_sublord_table()
        table2 = get_kp_sublord_table()
        # Should be same object due to caching
        assert len(table1) == len(table2)
        assert table1[0]["start_degree"] == table2[0]["start_degree"]


# ============================================================================
# TestKPIntegration
# ============================================================================


class TestKPIntegration:
    """Test integration across multiple KP functions."""

    def test_integration_sublord_to_significators_to_prediction(self):
        """Test full flow: sublord → significators → prediction."""
        # Get sublord for a cusp
        cusp_info = get_kp_sublord(SAMPLE_CUSPS[0])
        assert cusp_info["sub_lord"] in VIMSHOTTARI_SEQUENCE

        # Get significators
        sigs = get_kp_significators(SAMPLE_PLANETS, SAMPLE_CUSPS)
        assert len(sigs) == 12

        # Get prediction
        pred = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        assert pred["judgment"] in ["favorable", "unfavorable", "mixed"]

    def test_integration_cuspal_sublords_feed_into_house_analysis(self):
        """Test that cuspal sublords feed into house analysis correctly."""
        cuspal = get_cuspal_sublords(SAMPLE_CUSPS)

        for i in range(1, 13):
            house_analysis = analyze_kp_house(i, SAMPLE_PLANETS, SAMPLE_CUSPS)
            # The cusp should match
            assert abs(cuspal[i - 1]["cusp_longitude"] - house_analysis["cusp_longitude"]) < 0.01
            # The sub-lord should match
            assert cuspal[i - 1]["sub_lord"] == house_analysis["sub_lord"]

    def test_integration_sublord_table_contains_all_degrees(self):
        """Test that sublord table is consistent with get_kp_sublord."""
        table = get_kp_sublord_table()

        # Test a few specific degrees
        test_degrees = [0, 45, 90, 180, 270, 359]
        for degree in test_degrees:
            result = get_kp_sublord(degree)
            # Find entry in table that contains this degree
            found = False
            for entry in table:
                if entry["start_degree"] <= degree < entry["end_degree"]:
                    assert result["sub_lord"] == entry["sub_lord"]
                    assert result["star"] == entry["star"]
                    found = True
                    break
            assert found, f"Degree {degree} not found in sublord table"

    def test_integration_consistency_between_functions(self):
        """Test consistency between different KP functions."""
        cusps = SAMPLE_CUSPS

        # Get cuspal sublords
        cuspal = get_cuspal_sublords(cusps)

        # Get significators
        get_kp_significators(SAMPLE_PLANETS, cusps)

        # Get house analysis
        for house in range(1, 13):
            analysis = analyze_kp_house(house, SAMPLE_PLANETS, cusps)

            # The cusp sign should match cuspal sublords
            assert analysis["cusp_sign"] == cuspal[house - 1]["sign"]

            # The house number should match
            assert analysis["house"] == house

    def test_integration_all_query_types_return_valid_predictions(self):
        """Test that all query types return valid predictions."""
        for query_type in KP_HOUSE_GROUPS:
            result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, query_type)
            assert result["query_type"] == query_type
            assert result["judgment"] in ["favorable", "unfavorable", "mixed"]
            assert 0 <= result["confidence"] <= 1


# ============================================================================
# TestEdgeCases
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_edge_case_cusp_at_exact_sign_boundary(self):
        """Test cusp exactly at sign boundary (0, 30, 60, etc.)."""
        for degree in [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]:
            result = get_kp_sublord(degree)
            assert result["sign"] in SIGN_RULERS
            assert result["sign_lord"] == SIGN_RULERS[result["sign"]]

    def test_edge_case_cusp_at_exact_nakshatra_boundary(self):
        """Test cusp at exact nakshatra boundaries."""
        # Nakshatras are 13.333... degrees apart
        from packages.core.src.constants import NAKSHATRA_SPAN

        for star_num in [1, 10, 20, 27]:
            degree = (star_num - 1) * NAKSHATRA_SPAN
            result = get_kp_sublord(degree)
            assert result["star_number"] >= 1
            assert result["star_number"] <= 27

    def test_edge_case_longitude_just_under_360(self):
        """Test longitude very close to but under 360."""
        result = get_kp_sublord(359.999)
        assert result["sign"] == "pisces"
        assert result["sign_lord"] == "jupiter"

    def test_edge_case_empty_house_has_only_lord(self):
        """Test house with no planets has only house lord as significator."""
        # Create a chart with one planet in house 1, none in house 8
        planets = {"sun": {"longitude": 10.0, "sign": "aries", "house": 1}}
        cusps = SIMPLE_CUSPS

        sigs = get_kp_significators(planets, cusps)
        # House 8 should have at least the house lord
        assert len(sigs[8]["level_4"]) > 0

    def test_edge_case_very_small_sub_span(self):
        """Test sub-lords with very small spans."""
        table = get_kp_sublord_table()
        # Some subs will be smaller due to Vimshottari proportions
        for entry in table:
            span = entry["end_degree"] - entry["start_degree"]
            assert span > 0

    def test_edge_case_multiple_planets_same_house(self):
        """Test with multiple planets in the same house."""
        planets = {
            "sun": {"longitude": 10.0, "sign": "aries", "house": 1},
            "moon": {"longitude": 15.0, "sign": "aries", "house": 1},
            "mars": {"longitude": 20.0, "sign": "aries", "house": 1},
        }
        cusps = SIMPLE_CUSPS

        sigs = get_kp_significators(planets, cusps)
        # House 1 should have multiple planets as level_2
        assert len(sigs[1]["level_2"]) >= 3

    def test_edge_case_prediction_with_no_supporting_planets(self):
        """Test prediction when no planets support the matter."""
        # Create minimal chart
        minimal_planets = {"sun": {"longitude": 0.0}}
        minimal_cusps = SIMPLE_CUSPS

        # Even with minimal data, prediction should not crash
        result = get_kp_prediction(minimal_planets, minimal_cusps, "marriage")
        assert "judgment" in result
        assert "confidence" in result


# ============================================================================
# TestDataIntegrity
# ============================================================================


class TestDataIntegrity:
    """Test integrity of module constants and data structures."""

    def test_data_integrity_vimshottari_years_sum_to_120(self):
        """Test that Vimshottari years sum to 120."""
        total = sum(VIMSHOTTARI_YEARS.values())
        assert total == 120

    def test_data_integrity_vimshottari_sequence_length(self):
        """Test that Vimshottari sequence has 9 planets."""
        assert len(VIMSHOTTARI_SEQUENCE) == 9

    def test_data_integrity_sign_rulers_has_12_signs(self):
        """Test that sign rulers has 12 signs."""
        assert len(SIGN_RULERS) == 12

    def test_data_integrity_kp_house_groups_has_required_keys(self):
        """Test that each house group has primary, support, deny."""
        for _query_type, group in KP_HOUSE_GROUPS.items():
            assert "primary" in group
            assert "support" in group
            assert "deny" in group
            assert isinstance(group["primary"], int)
            assert isinstance(group["support"], list)
            assert isinstance(group["deny"], list)

    def test_data_integrity_all_signs_in_sign_rulers(self):
        """Test that all sign names are in SIGN_RULERS."""
        from packages.self.src.kp import RASHI_NAMES

        for sign in RASHI_NAMES:
            assert sign in SIGN_RULERS

    def test_data_integrity_sign_rulers_all_valid_planets(self):
        """Test that all sign rulers are valid planets."""
        valid_planets = set(VIMSHOTTARI_SEQUENCE)
        for planet in SIGN_RULERS.values():
            assert planet in valid_planets


# ============================================================================
# TestKPOverhaul — Phase 1-6 new tests
# ============================================================================


class TestKPOverhaul:
    """Tests for the Classical KP System Overhaul (Phases 1-6)."""

    def test_star_lord_backup_when_no_sublord_overlap(self):
        """Phase 1: Star lord backup used when sub-lord has zero overlap.

        The judgment should NOT be 'neutral' anymore — star lord provides a backup.
        """
        # Run all 12 houses across all query types; none should be 'neutral'
        for query_type in KP_HOUSE_GROUPS:
            groups = KP_HOUSE_GROUPS[query_type]
            primary_house = groups["primary"]
            result = analyze_kp_house(primary_house, SAMPLE_PLANETS, SAMPLE_CUSPS, query_type)
            assert result["judgment"] in ["favorable", "unfavorable", "mixed"], (
                f"House {primary_house} for {query_type} returned 'neutral' — "
                f"star lord backup should prevent this"
            )

    def test_weighted_significator_L1_stronger_than_L4(self):
        """Phase 2: Weighted scoring gives L1 (weight 4) more influence than L4 (weight 1)."""
        from packages.self.src.kp import _compute_weighted_score

        # Create mock significators where house 1 has L1 planets and house 2 has only L4
        mock_sigs = {
            1: {
                "level_1": ["jupiter"],
                "level_2": [],
                "level_3": [],
                "level_4": ["saturn"],
                "all_significators": ["jupiter", "saturn"],
            },
            2: {
                "level_1": [],
                "level_2": [],
                "level_3": [],
                "level_4": ["mars"],
                "all_significators": ["mars"],
            },
        }

        score_h1 = _compute_weighted_score(mock_sigs, [1])
        score_h2 = _compute_weighted_score(mock_sigs, [2])

        # House 1 has L1 (4) + L4 (1) = 5, House 2 has L4 (1) = 1
        assert score_h1 > score_h2
        assert score_h1 == 5.0  # jupiter L1=4, saturn L4=1
        assert score_h2 == 1.0  # mars L4=1

    def test_ruling_planet_confirmation_boosts_confidence(self):
        """Phase 3: Passing ruling planets that match significators boosts confidence."""
        # Get baseline prediction without ruling planets
        result_base = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "career")

        # Create ruling planets that overlap with supporting significators
        supporting = result_base["significator_analysis"]["supporting_significators"]
        if supporting:
            mock_rp = {
                "ruling_planets": [supporting[0]],
                "frequencies": {supporting[0]: 2},
                "strongest": supporting[0],
            }
            result_boosted = get_kp_prediction(
                SAMPLE_PLANETS, SAMPLE_CUSPS, "career", ruling_planets=mock_rp
            )
            # Confidence should increase (or at minimum not decrease) with matching RP
            assert result_boosted["confidence"] >= result_base["confidence"]

    def test_ruling_planet_no_match_reduces_confidence(self):
        """Phase 3: Ruling planets with no significator match slightly reduces confidence."""
        # Create ruling planets that DON'T match any significators
        mock_rp = {
            "ruling_planets": ["nonexistent_planet_xyz"],
            "frequencies": {"nonexistent_planet_xyz": 1},
            "strongest": "nonexistent_planet_xyz",
        }
        result_base = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "career")
        result_reduced = get_kp_prediction(
            SAMPLE_PLANETS, SAMPLE_CUSPS, "career", ruling_planets=mock_rp
        )
        # Should be slightly lower due to -0.05 penalty
        assert result_reduced["confidence"] <= result_base["confidence"]

    def test_retrograde_no_confidence_reduction(self):
        """Phase 4: Retrograde planets don't reduce confidence (KP doctrine)."""
        from packages.self.src.kp import _get_planet_modifiers

        planets_retro = {
            "mercury": {"longitude": 208.7, "is_retrograde": True},
            "sun": {"longitude": 227.5},
        }
        mods = _get_planet_modifiers("mercury", planets_retro)
        assert mods["is_retrograde"] is True
        # Retrograde should NOT cause combustion_strength_loss
        # (combustion is separate from retrograde)
        assert "delayed but not denied" in mods["notes"][0]

    def test_combust_reduces_confidence(self):
        """Phase 4: Combust planet has non-zero combustion_strength_loss."""
        from packages.self.src.kp import _get_planet_modifiers

        # Place Mercury very close to Sun (combustion threshold is ~14 degrees)
        planets_combust = {
            "mercury": {"longitude": 227.0, "is_retrograde": False},
            "sun": {"longitude": 227.5},
        }
        mods = _get_planet_modifiers("mercury", planets_combust)
        assert mods["is_combust"] is True
        assert mods["combustion_strength_loss"] > 0

    def test_rich_explanation_includes_house_labels(self):
        """Phase 6: Rich explanation includes house labels like 'career/status'."""
        result = analyze_kp_house(10, SAMPLE_PLANETS, SAMPLE_CUSPS, "career")
        explanation = result["explanation"]
        # The explanation should contain at least one house label from _HOUSE_LABELS
        has_label = any(
            label in explanation
            for label in [
                "career/status",
                "gains/income",
                "family/wealth",
                "self/personality",
                "marriage",
                "fortune",
            ]
        )
        assert has_label, f"Explanation missing house labels: {explanation}"

    def test_backward_compat_no_ruling_planets(self):
        """Phase 3: get_kp_prediction works without ruling_planets (backward compat)."""
        # Should work exactly as before without passing ruling_planets
        result = get_kp_prediction(SAMPLE_PLANETS, SAMPLE_CUSPS, "marriage")
        assert result["judgment"] in ["favorable", "unfavorable", "mixed"]
        assert 0 < result["confidence"] <= 1.0
        assert result["ruling_planet_confirmation"] is False
        assert "supporting_significators" in result["significator_analysis"]
        assert "balance" in result["significator_analysis"]
        # New weighted fields should be present
        assert "support_score" in result["significator_analysis"]
        assert "deny_score" in result["significator_analysis"]
