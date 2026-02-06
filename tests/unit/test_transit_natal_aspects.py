"""Tests for packages/context/src/transit_aspects.py — Transit-to-Natal Aspect Engine."""

from datetime import datetime

from packages.context.src.transit_aspects import (
    ASPECT_TYPES,
    PARASHARI_SPECIAL,
    _angular_distance,
    _check_aspect,
    _get_effect,
    _is_applying,
    find_upcoming_aspects,
    get_transit_natal_aspects,
)

# Standard natal positions for testing
NATAL_PLANETS = {
    "sun": {"longitude": 227.5, "rashi": 7},
    "moon": {"longitude": 326.85, "rashi": 10},
    "mars": {"longitude": 85.0, "rashi": 2},
    "mercury": {"longitude": 240.0, "rashi": 8},
    "jupiter": {"longitude": 145.0, "rashi": 4},
    "venus": {"longitude": 210.0, "rashi": 7},
    "saturn": {"longitude": 310.0, "rashi": 10},
}


class TestAngularDistance:
    """Test angular distance helper."""

    def test_same_point(self):
        assert _angular_distance(100.0, 100.0) == 0.0

    def test_opposition(self):
        assert _angular_distance(0.0, 180.0) == 180.0

    def test_wrap_around(self):
        assert abs(_angular_distance(5.0, 355.0) - 10.0) < 0.01

    def test_quarter(self):
        assert _angular_distance(0.0, 90.0) == 90.0


class TestCheckAspect:
    """Test aspect detection."""

    def test_conjunction_detected(self):
        matches = _check_aspect(100.0, 102.0, 5.0)
        assert any(m["aspect_type"] == "conjunction" for m in matches)

    def test_opposition_detected(self):
        matches = _check_aspect(0.0, 178.0, 5.0)
        assert any(m["aspect_type"] == "opposition" for m in matches)

    def test_trine_detected(self):
        matches = _check_aspect(0.0, 122.0, 5.0)
        assert any(m["aspect_type"] == "trine" for m in matches)

    def test_square_detected(self):
        matches = _check_aspect(0.0, 88.0, 5.0)
        assert any(m["aspect_type"] == "square" for m in matches)

    def test_sextile_detected(self):
        matches = _check_aspect(0.0, 62.0, 5.0)
        assert any(m["aspect_type"] == "sextile" for m in matches)

    def test_no_aspect_far_apart(self):
        matches = _check_aspect(0.0, 45.0, 3.0)
        assert len(matches) == 0

    def test_exact_conjunction(self):
        matches = _check_aspect(100.0, 100.0, 5.0)
        assert any(m["exact"] for m in matches)

    def test_orb_calculation(self):
        matches = _check_aspect(0.0, 3.0, 5.0)
        conj = next(m for m in matches if m["aspect_type"] == "conjunction")
        assert conj["orb"] == 3.0


class TestIsApplying:
    """Test applying/separating determination."""

    def test_applying_forward(self):
        # Transit at 100, natal at 105, speed positive -> applying
        assert _is_applying(100.0, 105.0, 1.0) is True

    def test_separating_forward(self):
        # Transit at 110, natal at 105, speed positive -> separating
        assert _is_applying(110.0, 105.0, 1.0) is False

    def test_retrograde_applying(self):
        # Transit at 110, natal at 105, speed negative -> applying
        assert _is_applying(110.0, 105.0, -1.0) is True


class TestGetEffect:
    """Test effect description retrieval."""

    def test_saturn_moon_effect(self):
        effect = _get_effect("saturn", "moon")
        assert "emotional" in effect.lower() or "mental" in effect.lower()

    def test_jupiter_sun_effect(self):
        effect = _get_effect("jupiter", "sun")
        assert "expansion" in effect.lower() or "leadership" in effect.lower()

    def test_unknown_combination_fallback(self):
        effect = _get_effect("rahu", "ketu")
        assert "transit" in effect.lower()

    def test_reverse_lookup(self):
        # Should find effect even if planets are in reverse order
        effect = _get_effect("moon", "saturn")
        assert len(effect) > 0


class TestGetTransitNatalAspects:
    """Test main aspect calculation function."""

    def test_returns_list(self):
        transits = {"jupiter": {"longitude": 47.5, "rashi": 1}}
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=5.0)
        assert isinstance(result, list)

    def test_conjunction_found(self):
        # Transit Jupiter near natal Sun (227.5)
        transits = {"jupiter": {"longitude": 228.0, "rashi": 7}}
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=5.0)
        conjunctions = [a for a in result if a["aspect_type"] == "conjunction"]
        assert len(conjunctions) > 0
        assert conjunctions[0]["transit_planet"] == "jupiter"
        assert conjunctions[0]["natal_planet"] == "sun"

    def test_opposition_found(self):
        # Transit Saturn opposite natal Jupiter (145.0 + 180 = 325)
        transits = {"saturn": {"longitude": 325.0, "rashi": 10}}
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=5.0)
        oppositions = [a for a in result if a["aspect_type"] == "opposition"]
        assert any(a["natal_planet"] == "jupiter" for a in oppositions)

    def test_aspect_has_expected_fields(self):
        transits = {"jupiter": {"longitude": 228.0, "rashi": 7}}
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=5.0)
        if result:
            a = result[0]
            assert "transit_planet" in a
            assert "natal_planet" in a
            assert "aspect_type" in a
            assert "aspect_degree" in a
            assert "orb" in a
            assert "applying" in a
            assert "effect" in a

    def test_sorted_by_orb(self):
        transits = {
            "jupiter": {"longitude": 228.0, "rashi": 7},
            "saturn": {"longitude": 240.5, "rashi": 8},
        }
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=5.0)
        if len(result) >= 2:
            assert result[0]["orb"] <= result[1]["orb"]

    def test_parashari_special_aspect(self):
        # Saturn special: 3rd and 10th house aspects
        # Saturn at rashi 0 (Aries), natal planet at rashi 3 (Cancer) -> 3rd house dist
        # dist = (3 - 0) % 12 = 3, ||12 = 3 -> Saturn 3rd aspect
        # Longitudes chosen so no degree-based aspect matches (110 deg = no standard aspect)
        transits = {"saturn": {"longitude": 5.0, "rashi": 0}}
        natal = {"mars": {"longitude": 115.0, "rashi": 3}}
        result = get_transit_natal_aspects(natal, transits, orb=5.0)
        parashari = [a for a in result if "parashari" in a.get("aspect_type", "")]
        assert len(parashari) > 0

    def test_no_duplicate_aspects(self):
        # Should not add parashari if degree-based already found
        transits = {"jupiter": {"longitude": 228.0, "rashi": 7}}
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=8.0)
        # Allow some duplicates for different aspect types but not for same pair with same type
        type_keys = [(a["transit_planet"], a["natal_planet"], a["aspect_type"]) for a in result]
        assert len(type_keys) == len(set(type_keys))

    def test_empty_transits(self):
        result = get_transit_natal_aspects(NATAL_PLANETS, {}, orb=5.0)
        assert result == []

    def test_empty_natals(self):
        transits = {"jupiter": {"longitude": 228.0, "rashi": 7}}
        result = get_transit_natal_aspects({}, transits, orb=5.0)
        assert result == []

    def test_tight_orb_filters_more(self):
        transits = {"jupiter": {"longitude": 230.0, "rashi": 7}}
        wide = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=8.0)
        tight = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=1.0)
        assert len(tight) <= len(wide)

    def test_multiple_transit_planets(self):
        transits = {
            "jupiter": {"longitude": 228.0, "rashi": 7},
            "saturn": {"longitude": 146.0, "rashi": 4},
            "mars": {"longitude": 327.0, "rashi": 10},
        }
        result = get_transit_natal_aspects(NATAL_PLANETS, transits, orb=5.0)
        transit_planets_found = {a["transit_planet"] for a in result}
        assert len(transit_planets_found) >= 1


class TestFindUpcomingAspects:
    """Test upcoming aspect finder (uses Swiss Ephemeris)."""

    def test_returns_list(self):
        result = find_upcoming_aspects(
            NATAL_PLANETS,
            start_date="2026-02-06",
            days_ahead=7,
            orb=3.0,
        )
        assert isinstance(result, list)

    def test_aspects_have_date(self):
        result = find_upcoming_aspects(
            NATAL_PLANETS,
            start_date="2026-02-06",
            days_ahead=7,
            orb=3.0,
        )
        for asp in result:
            assert "date" in asp
            assert "days_from_now" in asp

    def test_sorted_by_days(self):
        result = find_upcoming_aspects(
            NATAL_PLANETS,
            start_date="2026-02-06",
            days_ahead=14,
            orb=3.0,
        )
        if len(result) >= 2:
            assert result[0]["days_from_now"] <= result[1]["days_from_now"]

    def test_datetime_input(self):
        result = find_upcoming_aspects(
            NATAL_PLANETS,
            start_date=datetime(2026, 2, 6),
            days_ahead=7,
            orb=3.0,
        )
        assert isinstance(result, list)


class TestAspectTypes:
    """Test aspect type definitions."""

    def test_all_major_aspects_defined(self):
        assert "conjunction" in ASPECT_TYPES
        assert "opposition" in ASPECT_TYPES
        assert "trine" in ASPECT_TYPES
        assert "square" in ASPECT_TYPES
        assert "sextile" in ASPECT_TYPES

    def test_parashari_special_defined(self):
        assert "mars" in PARASHARI_SPECIAL
        assert "jupiter" in PARASHARI_SPECIAL
        assert "saturn" in PARASHARI_SPECIAL
        assert 4 in PARASHARI_SPECIAL["mars"]
        assert 8 in PARASHARI_SPECIAL["mars"]
        assert 5 in PARASHARI_SPECIAL["jupiter"]
        assert 9 in PARASHARI_SPECIAL["jupiter"]
        assert 3 in PARASHARI_SPECIAL["saturn"]
        assert 10 in PARASHARI_SPECIAL["saturn"]
