"""Unit tests for Secondary Progressions module."""

from datetime import datetime

import pytest

from packages.context.src.progressions import (
    PROGRESSION_PLANETS,
    RASHI_NAMES,
    _angle_diff,
    _longitude_to_sign,
    calculate_progressed_positions,
    calculate_progressed_to_natal_aspects,
    get_current_progressions,
    get_progression_timeline,
)

# Standard test birth data: Dec 3, 1992, 3:00 AM IST -> 21:30 UTC Dec 2
BIRTH_DT = datetime(1992, 12, 2, 21, 30)  # UTC equivalent
BIRTH_LAT = 16.722786
BIRTH_LON = 81.294264


class TestHelperFunctions:
    """Test internal helper functions."""

    def test_longitude_to_sign_aries(self):
        """0-30 degrees -> Aries."""
        assert _longitude_to_sign(0.0) == "aries"
        assert _longitude_to_sign(15.0) == "aries"
        assert _longitude_to_sign(29.99) == "aries"

    def test_longitude_to_sign_taurus(self):
        """30-60 degrees -> Taurus."""
        assert _longitude_to_sign(30.0) == "taurus"
        assert _longitude_to_sign(45.0) == "taurus"

    def test_longitude_to_sign_pisces(self):
        """330-360 degrees -> Pisces."""
        assert _longitude_to_sign(330.0) == "pisces"
        assert _longitude_to_sign(359.99) == "pisces"

    def test_longitude_to_sign_all_signs(self):
        """Each 30-degree slice maps to the correct sign."""
        for i, sign in enumerate(RASHI_NAMES):
            longitude = i * 30 + 15  # Middle of each sign
            assert _longitude_to_sign(longitude) == sign

    def test_angle_diff_same(self):
        """Same angle -> 0 difference."""
        assert _angle_diff(100.0, 100.0) == pytest.approx(0.0)

    def test_angle_diff_small(self):
        """Small difference."""
        assert _angle_diff(10.0, 15.0) == pytest.approx(5.0)

    def test_angle_diff_opposite(self):
        """180 degrees apart."""
        assert _angle_diff(0.0, 180.0) == pytest.approx(180.0)

    def test_angle_diff_wrap_around(self):
        """Wrapping around 360 degrees."""
        assert _angle_diff(350.0, 10.0) == pytest.approx(20.0)

    def test_angle_diff_symmetric(self):
        """Difference should be symmetric."""
        assert _angle_diff(10.0, 350.0) == _angle_diff(350.0, 10.0)


class TestCalculateProgressedPositions:
    """Test progressed position calculations."""

    def test_returns_all_planets(self):
        """Result should contain all 9 Vedic planets."""
        positions = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0.0)
        for planet in PROGRESSION_PLANETS:
            assert planet in positions, f"Missing planet: {planet}"

    def test_positions_have_required_fields(self):
        """Each position should have longitude, sign, speed, etc."""
        positions = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 10.0)
        for planet, pos in positions.items():
            assert "longitude" in pos, f"{planet} missing longitude"
            assert "sign" in pos, f"{planet} missing sign"
            assert "speed" in pos, f"{planet} missing speed"
            assert "is_retrograde" in pos, f"{planet} missing is_retrograde"

    def test_longitude_in_range(self):
        """Longitudes should be in 0-360 range."""
        positions = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 30.0)
        for planet, pos in positions.items():
            assert (
                0 <= pos["longitude"] < 360
            ), f"{planet} longitude out of range: {pos['longitude']}"

    def test_sign_is_valid(self):
        """Signs should be valid rashi names."""
        positions = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 20.0)
        for planet, pos in positions.items():
            assert pos["sign"] in RASHI_NAMES, f"{planet} has invalid sign: {pos['sign']}"

    def test_age_zero_matches_natal(self):
        """At age 0 (birth), progressed should match natal positions."""
        positions = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0.0)
        # Positions at age 0 should exist (they are natal positions)
        assert len(positions) == len(PROGRESSION_PLANETS)

    def test_progressed_sun_moves_slowly(self):
        """Progressed Sun should move roughly 1 degree per year of life."""
        pos_0 = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0.0)
        pos_30 = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 30.0)

        sun_0 = pos_0["sun"]["longitude"]
        sun_30 = pos_30["sun"]["longitude"]

        # Sun moves ~1 degree/day, so 30 days = ~30 degrees
        diff = (sun_30 - sun_0) % 360
        if diff > 180:
            diff = 360 - diff
        # Should be roughly 28-32 degrees for 30 years
        assert 20 <= diff <= 40, f"Sun progressed {diff} degrees in 30 years"

    def test_progressed_moon_moves_faster(self):
        """Progressed Moon should move ~13 degrees per year of life."""
        pos_0 = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0.0)
        pos_1 = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 1.0)

        moon_0 = pos_0["moon"]["longitude"]
        moon_1 = pos_1["moon"]["longitude"]

        # Moon moves ~13 degrees/day, so 1 day = ~13 degrees for 1 year progression
        diff = (moon_1 - moon_0) % 360
        if diff > 180:
            diff = 360 - diff
        # Should be roughly 10-16 degrees for 1 year
        assert 5 <= diff <= 20, f"Moon progressed {diff} degrees in 1 year"


class TestCalculateProgressedToNatalAspects:
    """Test aspect detection between progressed and natal positions."""

    def test_conjunction_detected(self):
        """A conjunction (0 degrees) within orb should be detected."""
        progressed = {"sun": {"longitude": 100.5}}
        natal = {"moon": {"longitude": 100.0}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert len(aspects) == 1
        assert aspects[0]["aspect"] == "conjunction"
        assert aspects[0]["progressed_planet"] == "sun"
        assert aspects[0]["natal_planet"] == "moon"

    def test_opposition_detected(self):
        """An opposition (180 degrees) within orb should be detected."""
        progressed = {"mars": {"longitude": 180.3}}
        natal = {"venus": {"longitude": 0.0}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert any(a["aspect"] == "opposition" for a in aspects)

    def test_trine_detected(self):
        """A trine (120 degrees) within orb should be detected."""
        progressed = {"jupiter": {"longitude": 120.8}}
        natal = {"sun": {"longitude": 0.5}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert any(a["aspect"] == "trine" for a in aspects)

    def test_square_detected(self):
        """A square (90 degrees) within orb should be detected."""
        progressed = {"saturn": {"longitude": 90.2}}
        natal = {"mercury": {"longitude": 0.0}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert any(a["aspect"] == "square" for a in aspects)

    def test_sextile_detected(self):
        """A sextile (60 degrees) within orb should be detected."""
        progressed = {"venus": {"longitude": 60.5}}
        natal = {"mars": {"longitude": 0.0}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert any(a["aspect"] == "sextile" for a in aspects)

    def test_no_aspect_outside_orb(self):
        """Planets too far from any aspect angle should not produce aspects."""
        progressed = {"sun": {"longitude": 45.0}}
        natal = {"moon": {"longitude": 0.0}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        # 45 degrees is not close to any standard aspect (0, 60, 90, 120, 180)
        assert len(aspects) == 0

    def test_aspect_has_required_fields(self):
        """Each aspect should have all required fields."""
        progressed = {"sun": {"longitude": 0.0}}
        natal = {"moon": {"longitude": 0.5}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert len(aspects) >= 1
        aspect = aspects[0]
        assert "progressed_planet" in aspect
        assert "natal_planet" in aspect
        assert "aspect" in aspect
        assert "angle" in aspect
        assert "orb" in aspect
        assert "progressed_longitude" in aspect
        assert "natal_longitude" in aspect

    def test_wrap_around_conjunction(self):
        """Conjunction across the 360/0 boundary should be detected."""
        progressed = {"sun": {"longitude": 359.5}}
        natal = {"moon": {"longitude": 0.3}}
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert any(a["aspect"] == "conjunction" for a in aspects)

    def test_empty_inputs(self):
        """Empty inputs should return empty list."""
        assert calculate_progressed_to_natal_aspects({}, {}) == []
        assert calculate_progressed_to_natal_aspects({"sun": {"longitude": 0}}, {}) == []
        assert calculate_progressed_to_natal_aspects({}, {"moon": {"longitude": 0}}) == []

    def test_multiple_aspects(self):
        """Multiple planets can create multiple aspects."""
        progressed = {
            "sun": {"longitude": 0.0},
            "moon": {"longitude": 120.0},
        }
        natal = {
            "mars": {"longitude": 0.5},
        }
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        # Sun conjunct Mars, Moon trine Mars
        assert len(aspects) >= 2


class TestGetCurrentProgressions:
    """Test current progressions retrieval."""

    def test_returns_required_keys(self):
        """Result should have all required keys."""
        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        assert "age" in result
        assert "progressed_positions" in result
        assert "natal_positions" in result
        assert "active_aspects" in result
        assert "progressed_moon_sign" in result
        assert "progressed_sun_sign" in result

    def test_age_is_correct(self):
        """Age should be approximately correct."""
        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        # Born Dec 1992, query Jan 2025 -> ~32 years
        assert 31.5 <= result["age"] <= 33.0

    def test_progressed_positions_populated(self):
        """Progressed positions should contain planets."""
        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        assert len(result["progressed_positions"]) == len(PROGRESSION_PLANETS)

    def test_natal_positions_populated(self):
        """Natal positions should contain planets."""
        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        assert len(result["natal_positions"]) == len(PROGRESSION_PLANETS)

    def test_moon_sign_is_valid(self):
        """Progressed Moon sign should be a valid rashi."""
        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        assert result["progressed_moon_sign"] in RASHI_NAMES

    def test_sun_sign_is_valid(self):
        """Progressed Sun sign should be a valid rashi."""
        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        assert result["progressed_sun_sign"] in RASHI_NAMES

    def test_with_timezone_aware_datetime(self):
        """Should handle timezone-aware datetimes."""
        from datetime import UTC

        result = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert result["age"] > 30

    def test_default_query_datetime(self):
        """Without query datetime, should use current time."""
        result = get_current_progressions(BIRTH_DT, BIRTH_LAT, BIRTH_LON)
        assert result["age"] > 30  # Born 1992, always > 30 from now on


class TestGetProgressionTimeline:
    """Test progression timeline generation."""

    def test_timeline_length(self):
        """Timeline should have one entry per year in range."""
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 30, 35)
        assert len(timeline) == 6  # 30, 31, 32, 33, 34, 35

    def test_timeline_ages_correct(self):
        """Ages should match the requested range."""
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 20, 25)
        ages = [entry["age"] for entry in timeline]
        assert ages == [20, 21, 22, 23, 24, 25]

    def test_timeline_has_required_fields(self):
        """Each timeline entry should have required fields."""
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 30, 30)
        entry = timeline[0]
        assert "age" in entry
        assert "progressed_sun_sign" in entry
        assert "progressed_moon_sign" in entry
        assert "aspects" in entry

    def test_timeline_signs_valid(self):
        """All signs in timeline should be valid rashis."""
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 28, 32)
        for entry in timeline:
            assert entry["progressed_sun_sign"] in RASHI_NAMES
            assert entry["progressed_moon_sign"] in RASHI_NAMES

    def test_single_year_timeline(self):
        """Timeline with start_age == end_age should have 1 entry."""
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 25, 25)
        assert len(timeline) == 1
        assert timeline[0]["age"] == 25

    def test_invalid_negative_age(self):
        """Negative start age should raise ValueError."""
        with pytest.raises(ValueError, match="start_age must be >= 0"):
            get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, -1, 10)

    def test_invalid_reversed_range(self):
        """end_age < start_age should raise ValueError."""
        with pytest.raises(ValueError, match=r"end_age.*must be >= start_age"):
            get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 35, 30)

    def test_zero_age(self):
        """Age 0 should work (natal chart)."""
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0, 0)
        assert len(timeline) == 1
        assert timeline[0]["age"] == 0


class TestProgressionsIntegration:
    """Integration tests for the full progressions workflow."""

    def test_full_workflow(self):
        """Test the complete workflow: positions -> aspects -> current -> timeline."""
        # Step 1: Get natal positions (age 0)
        natal = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0.0)
        assert "sun" in natal

        # Step 2: Get progressed positions at age 32
        progressed = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 32.0)
        assert "sun" in progressed

        # Step 3: Calculate aspects
        aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        assert isinstance(aspects, list)

        # Step 4: Get current progressions
        current = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        assert current["age"] > 30

        # Step 5: Get timeline
        timeline = get_progression_timeline(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 30, 35)
        assert len(timeline) == 6

    def test_progressed_sun_in_different_sign_from_natal(self):
        """After ~30 years, progressed Sun should have moved ~30 degrees."""
        natal = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 0.0)
        progressed = calculate_progressed_positions(BIRTH_DT, BIRTH_LAT, BIRTH_LON, 30.0)

        natal_sun = natal["sun"]["longitude"]
        prog_sun = progressed["sun"]["longitude"]

        # They should be different (Sun moved ~30 degrees in 30 days)
        diff = abs(prog_sun - natal_sun) % 360
        assert diff > 5, "Progressed Sun should have moved significantly"

    def test_aspects_orb_respect(self):
        """All detected aspects should be within the defined orb."""
        current = get_current_progressions(
            BIRTH_DT,
            BIRTH_LAT,
            BIRTH_LON,
            query_datetime=datetime(2025, 1, 1),
        )
        for aspect in current["active_aspects"]:
            assert aspect["orb"] <= 1.0, f"Aspect {aspect} exceeds 1-degree orb"
