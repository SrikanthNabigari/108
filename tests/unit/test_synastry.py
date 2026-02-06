"""Tests for Synastry & Composite Chart Analysis."""

import pytest

from packages.self.src.synastry import (
    _angular_distance,
    _longitude_to_sign,
    _midpoint,
    calculate_composite_chart,
    calculate_cross_aspects,
    calculate_house_overlay,
    get_synastry_report,
)

# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------


def _make_planets(**kwargs: float) -> dict[str, dict[str, float]]:
    """Build a minimal planet dict from name=longitude pairs."""
    return {name: {"longitude": lon} for name, lon in kwargs.items()}


# Libra Lagna native (user's chart approximation)
NATIVE_PLANETS = _make_planets(
    sun=227.0,  # Scorpio ~17 deg
    moon=326.85,  # Aquarius ~27 deg
    mars=109.5,  # Cancer ~19 deg (retrograde)
    mercury=213.0,  # Scorpio ~3 deg
    jupiter=152.0,  # Virgo ~2 deg
    venus=260.0,  # Sagittarius ~20 deg
    saturn=313.0,  # Aquarius ~13 deg
)

NATIVE_CUSPS = [180, 210, 240, 270, 300, 330, 0, 30, 60, 90, 120, 150]

# A hypothetical partner chart
PARTNER_PLANETS = _make_planets(
    sun=45.0,  # Taurus ~15 deg
    moon=120.0,  # Leo ~0 deg
    mars=330.0,  # Pisces ~0 deg
    mercury=60.0,  # Gemini ~0 deg
    jupiter=280.0,  # Capricorn ~10 deg
    venus=325.0,  # Aquarius ~25 deg
    saturn=195.0,  # Libra ~15 deg
)

PARTNER_CUSPS = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]


# ---------------------------------------------------------------------------
# Unit tests: angular helpers
# ---------------------------------------------------------------------------


class TestAngularDistance:
    def test_same_point(self):
        assert _angular_distance(100.0, 100.0) == 0.0

    def test_opposite_points(self):
        assert _angular_distance(0.0, 180.0) == 180.0

    def test_wraparound_close(self):
        assert _angular_distance(350.0, 10.0) == 20.0

    def test_wraparound_far(self):
        assert _angular_distance(1.0, 359.0) == 2.0

    def test_symmetric(self):
        assert _angular_distance(30.0, 120.0) == _angular_distance(120.0, 30.0)

    def test_quarter_circle(self):
        assert _angular_distance(0.0, 90.0) == 90.0


class TestMidpoint:
    def test_same_point(self):
        assert _midpoint(100.0, 100.0) == 100.0

    def test_simple_midpoint(self):
        mid = _midpoint(60.0, 120.0)
        assert abs(mid - 90.0) < 0.01

    def test_wraparound_midpoint(self):
        mid = _midpoint(350.0, 10.0)
        assert abs(mid - 0.0) < 0.01 or abs(mid - 360.0) < 0.01

    def test_opposite_midpoint(self):
        mid = _midpoint(0.0, 180.0)
        assert abs(mid - 90.0) < 0.01

    def test_wraparound_large_gap(self):
        mid = _midpoint(10.0, 350.0)
        assert abs(mid - 0.0) < 0.01 or abs(mid - 360.0) < 0.01

    def test_result_in_range(self):
        for l1 in range(0, 360, 37):
            for l2 in range(0, 360, 41):
                mid = _midpoint(float(l1), float(l2))
                assert 0 <= mid < 360


class TestLongitudeToSign:
    def test_aries(self):
        assert _longitude_to_sign(15.0) == "aries"

    def test_taurus(self):
        assert _longitude_to_sign(45.0) == "taurus"

    def test_pisces(self):
        assert _longitude_to_sign(350.0) == "pisces"

    def test_boundary(self):
        assert _longitude_to_sign(30.0) == "taurus"

    def test_zero(self):
        assert _longitude_to_sign(0.0) == "aries"


# ---------------------------------------------------------------------------
# House overlay tests
# ---------------------------------------------------------------------------


class TestCalculateHouseOverlay:
    def test_returns_list(self):
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, PARTNER_PLANETS)
        assert isinstance(result, list)

    def test_all_partner_planets_present(self):
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, PARTNER_PLANETS)
        planet_names = {r["partner_planet"] for r in result}
        assert "sun" in planet_names
        assert "moon" in planet_names
        assert "venus" in planet_names

    def test_house_in_valid_range(self):
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, PARTNER_PLANETS)
        for r in result:
            assert 1 <= r["native_house"] <= 12

    def test_has_interpretation(self):
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, PARTNER_PLANETS)
        for r in result:
            assert r["interpretation"]
            assert isinstance(r["interpretation"], str)

    def test_has_significance(self):
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, PARTNER_PLANETS)
        significances = {r["significance"] for r in result}
        assert significances.issubset({"very_high", "high", "moderate", "low"})

    def test_invalid_cusps_raises(self):
        with pytest.raises(ValueError):
            calculate_house_overlay(NATIVE_PLANETS, [0, 30, 60], PARTNER_PLANETS)

    def test_empty_partner_returns_empty(self):
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, {})
        assert result == []

    def test_partner_longitude_preserved(self):
        partner = _make_planets(sun=123.45)
        result = calculate_house_overlay(NATIVE_PLANETS, NATIVE_CUSPS, partner)
        assert result[0]["partner_longitude"] == 123.45


# ---------------------------------------------------------------------------
# Cross-aspect tests
# ---------------------------------------------------------------------------


class TestCalculateCrossAspects:
    def test_returns_list(self):
        result = calculate_cross_aspects(NATIVE_PLANETS, PARTNER_PLANETS)
        assert isinstance(result, list)

    def test_conjunction_detected(self):
        """Two planets at same degree should find conjunction."""
        n = _make_planets(sun=100.0)
        p = _make_planets(moon=100.5)
        result = calculate_cross_aspects(n, p, orb=8.0)
        conjunctions = [a for a in result if a["aspect_type"] == "conjunction"]
        assert len(conjunctions) == 1
        assert conjunctions[0]["orb"] < 1.0

    def test_opposition_detected(self):
        n = _make_planets(sun=10.0)
        p = _make_planets(moon=190.0)
        result = calculate_cross_aspects(n, p, orb=8.0)
        oppositions = [a for a in result if a["aspect_type"] == "opposition"]
        assert len(oppositions) == 1

    def test_trine_detected(self):
        n = _make_planets(venus=0.0)
        p = _make_planets(jupiter=120.0)
        result = calculate_cross_aspects(n, p, orb=8.0)
        trines = [a for a in result if a["aspect_type"] == "trine"]
        assert len(trines) >= 1

    def test_square_detected(self):
        n = _make_planets(mars=50.0)
        p = _make_planets(saturn=140.0)
        result = calculate_cross_aspects(n, p, orb=8.0)
        squares = [a for a in result if a["aspect_type"] == "square"]
        assert len(squares) == 1

    def test_sorted_by_orb(self):
        result = calculate_cross_aspects(NATIVE_PLANETS, PARTNER_PLANETS)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]["orb"] <= result[i + 1]["orb"]

    def test_has_quality_and_interpretation(self):
        result = calculate_cross_aspects(NATIVE_PLANETS, PARTNER_PLANETS)
        for a in result:
            assert "quality" in a
            assert "interpretation" in a

    def test_narrower_orb_filters(self):
        wide = calculate_cross_aspects(NATIVE_PLANETS, PARTNER_PLANETS, orb=10.0)
        narrow = calculate_cross_aspects(NATIVE_PLANETS, PARTNER_PLANETS, orb=3.0)
        assert len(narrow) <= len(wide)

    def test_no_aspects_with_zero_orb(self):
        """With orb=0, very unlikely to find exact aspects."""
        n = _make_planets(sun=10.0)
        p = _make_planets(moon=55.0)
        result = calculate_cross_aspects(n, p, orb=0.0)
        assert len(result) == 0

    def test_empty_charts(self):
        result = calculate_cross_aspects({}, PARTNER_PLANETS)
        assert result == []


# ---------------------------------------------------------------------------
# Composite chart tests
# ---------------------------------------------------------------------------


class TestCalculateCompositeChart:
    def test_returns_dict(self):
        result = calculate_composite_chart(NATIVE_PLANETS, PARTNER_PLANETS, 180.0, 15.0)
        assert isinstance(result, dict)

    def test_has_composite_ascendant(self):
        result = calculate_composite_chart(NATIVE_PLANETS, PARTNER_PLANETS, 180.0, 15.0)
        assert "composite_ascendant" in result
        assert 0 <= result["composite_ascendant"] < 360

    def test_has_composite_planets(self):
        result = calculate_composite_chart(NATIVE_PLANETS, PARTNER_PLANETS, 180.0, 15.0)
        assert "composite_planets" in result
        assert len(result["composite_planets"]) > 0

    def test_composite_planet_has_sign(self):
        result = calculate_composite_chart(NATIVE_PLANETS, PARTNER_PLANETS, 180.0, 15.0)
        for _, data in result["composite_planets"].items():
            assert "sign" in data
            assert "longitude" in data
            assert "house" in data

    def test_wraparound_midpoint_correct(self):
        """Composite of 350 and 10 should be ~0, not ~180."""
        n = _make_planets(sun=350.0)
        p = _make_planets(sun=10.0)
        result = calculate_composite_chart(n, p, 0.0, 0.0)
        comp_sun_lon = result["composite_planets"]["sun"]["longitude"]
        assert comp_sun_lon < 30 or comp_sun_lon > 330

    def test_has_themes_and_strengths(self):
        result = calculate_composite_chart(NATIVE_PLANETS, PARTNER_PLANETS, 180.0, 15.0)
        assert "relationship_themes" in result
        assert "strengths" in result
        assert "challenges" in result

    def test_only_common_planets_included(self):
        n = _make_planets(sun=100.0, mars=200.0)
        p = _make_planets(sun=110.0, venus=50.0)
        result = calculate_composite_chart(n, p, 0.0, 0.0)
        assert "sun" in result["composite_planets"]
        assert "mars" not in result["composite_planets"]
        assert "venus" not in result["composite_planets"]


# ---------------------------------------------------------------------------
# Full synastry report tests
# ---------------------------------------------------------------------------


class TestGetSynastryReport:
    def test_returns_dict(self):
        result = get_synastry_report(
            NATIVE_PLANETS,
            NATIVE_CUSPS,
            PARTNER_PLANETS,
            PARTNER_CUSPS,
            180.0,
            15.0,
            20,
            10,
        )
        assert isinstance(result, dict)

    def test_has_all_sections(self):
        result = get_synastry_report(
            NATIVE_PLANETS,
            NATIVE_CUSPS,
            PARTNER_PLANETS,
            PARTNER_CUSPS,
            180.0,
            15.0,
            20,
            10,
        )
        assert "house_overlay" in result
        assert "cross_aspects" in result
        assert "composite_chart" in result
        assert "synastry_score" in result
        assert "verdict" in result

    def test_house_overlay_both_directions(self):
        result = get_synastry_report(
            NATIVE_PLANETS,
            NATIVE_CUSPS,
            PARTNER_PLANETS,
            PARTNER_CUSPS,
            180.0,
            15.0,
            20,
            10,
        )
        assert "partner_in_native" in result["house_overlay"]
        assert "native_in_partner" in result["house_overlay"]

    def test_synastry_score_in_range(self):
        result = get_synastry_report(
            NATIVE_PLANETS,
            NATIVE_CUSPS,
            PARTNER_PLANETS,
            PARTNER_CUSPS,
            180.0,
            15.0,
            20,
            10,
        )
        assert 0 <= result["synastry_score"] <= 100

    def test_verdict_is_string(self):
        result = get_synastry_report(
            NATIVE_PLANETS,
            NATIVE_CUSPS,
            PARTNER_PLANETS,
            PARTNER_CUSPS,
            180.0,
            15.0,
            20,
            10,
        )
        assert isinstance(result["verdict"], str)

    def test_cross_aspects_has_counts(self):
        result = get_synastry_report(
            NATIVE_PLANETS,
            NATIVE_CUSPS,
            PARTNER_PLANETS,
            PARTNER_CUSPS,
            180.0,
            15.0,
            20,
            10,
        )
        ca = result["cross_aspects"]
        assert "harmonious_count" in ca
        assert "challenging_count" in ca
        assert "total_count" in ca
        assert ca["harmonious_count"] + ca["challenging_count"] <= ca["total_count"]
