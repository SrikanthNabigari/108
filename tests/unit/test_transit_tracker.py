"""Tests for packages/context/src/transit_tracker.py — Real-Time Transit Trigger Tracker."""

from datetime import datetime

from packages.context.src.transit_tracker import (
    RASHI_NAMES,
    _angular_distance,
    _detect_aspects,
    _detect_conjunctions,
    _detect_dasha_changes,
    _detect_retrograde_stations,
    _detect_sign_ingresses,
    _get_rashi,
    get_upcoming_triggers,
)

# Srikanth's birth data
BIRTH_DT = datetime(1992, 12, 3, 3, 0)
MOON_LON = 326.85
LAGNA_RASHI = 6  # Libra

NATAL_PLANETS = {
    "sun": {"longitude": 227.5, "rashi": 7},
    "moon": {"longitude": 326.85, "rashi": 10},
    "mars": {"longitude": 85.0, "rashi": 2},
    "mercury": {"longitude": 240.0, "rashi": 8},
    "jupiter": {"longitude": 145.0, "rashi": 4},
    "venus": {"longitude": 210.0, "rashi": 7},
    "saturn": {"longitude": 310.0, "rashi": 10},
}


class TestHelpers:
    """Test helper functions."""

    def test_get_rashi_aries(self):
        assert _get_rashi(15.0) == 0

    def test_get_rashi_pisces(self):
        assert _get_rashi(350.0) == 11

    def test_get_rashi_boundary(self):
        assert _get_rashi(30.0) == 1

    def test_angular_distance_same(self):
        assert _angular_distance(100.0, 100.0) == 0.0

    def test_angular_distance_wrap(self):
        assert abs(_angular_distance(5.0, 355.0) - 10.0) < 0.01

    def test_rashi_names_count(self):
        assert len(RASHI_NAMES) == 12


class TestDetectSignIngresses:
    """Test sign ingress detection."""

    def test_sign_change_detected(self):
        prev = {"mars": {"longitude": 29.0}}
        curr = {"mars": {"longitude": 31.0}}
        check_date = datetime(2026, 2, 10)
        result = _detect_sign_ingresses(prev, curr, check_date, 6, 5)
        assert len(result) == 1
        assert result[0]["type"] == "sign_ingress"
        assert result[0]["planet"] == "mars"
        assert "Taurus" in result[0]["new_sign"]

    def test_no_sign_change(self):
        prev = {"mars": {"longitude": 25.0}}
        curr = {"mars": {"longitude": 28.0}}
        result = _detect_sign_ingresses(prev, curr, datetime(2026, 2, 10), 6, 5)
        assert len(result) == 0

    def test_multiple_planets_ingress(self):
        prev = {"mars": {"longitude": 29.0}, "venus": {"longitude": 59.0}}
        curr = {"mars": {"longitude": 31.0}, "venus": {"longitude": 61.0}}
        result = _detect_sign_ingresses(prev, curr, datetime(2026, 2, 10), 6, 5)
        assert len(result) == 2

    def test_ingress_has_house(self):
        prev = {"sun": {"longitude": 29.0}}
        curr = {"sun": {"longitude": 31.0}}
        result = _detect_sign_ingresses(prev, curr, datetime(2026, 2, 10), 6, 5)
        assert result[0]["house"] >= 1
        assert result[0]["house"] <= 12


class TestDetectConjunctions:
    """Test conjunction detection."""

    def test_conjunction_within_orb(self):
        curr = {"jupiter": {"longitude": 228.0}}
        result = _detect_conjunctions(curr, NATAL_PLANETS, datetime(2026, 2, 10), 5)
        # Jupiter at 228 is close to natal Sun at 227.5
        sun_conj = [t for t in result if t["natal_planet"] == "sun"]
        assert len(sun_conj) > 0

    def test_conjunction_outside_orb(self):
        curr = {"jupiter": {"longitude": 200.0}}
        result = _detect_conjunctions(curr, NATAL_PLANETS, datetime(2026, 2, 10), 5, orb=2.0)
        # Jupiter at 200 is far from all natal planets
        assert len(result) == 0

    def test_conjunction_has_orb(self):
        curr = {"jupiter": {"longitude": 228.0}}
        result = _detect_conjunctions(curr, NATAL_PLANETS, datetime(2026, 2, 10), 5)
        if result:
            assert "orb" in result[0]

    def test_conjunction_significance(self):
        curr = {"saturn": {"longitude": 310.5}}
        result = _detect_conjunctions(curr, NATAL_PLANETS, datetime(2026, 2, 10), 5)
        if result:
            assert result[0]["significance"] == "high"


class TestDetectAspects:
    """Test aspect detection."""

    def test_seventh_aspect_found(self):
        # Saturn at rashi 0 (Aries, lon 15), natal Moon at rashi 6 (Libra, lon 195) -> 7th house
        curr = {"saturn": {"longitude": 15.0}}
        natal = {"moon": {"longitude": 195.0}}
        result = _detect_aspects(curr, natal, datetime(2026, 2, 10), 5)
        # rashi(15)=0, rashi(195)=6, dist = (6-0)%12 = 6, but we need ||12 = 6
        # 7th aspect: house_dist must be 7. So natal needs to be 7 signs ahead.
        # rashi 0 + 7 = rashi 7 (Scorpio). Moon at lon 225 -> rashi 7
        natal_fixed = {"moon": {"longitude": 225.0}}
        result = _detect_aspects(curr, natal_fixed, datetime(2026, 2, 10), 5)
        assert any(t["aspect_house"] == 7 for t in result)

    def test_saturn_special_3rd(self):
        # Saturn at rashi 0 (lon 15), natal at rashi 2 (Gemini, lon 75) -> dist=(2-0)%12=2, ||12=2
        # Need dist=3 for Saturn special. Rashi 0 + 3 = rashi 3 (Cancer)
        curr = {"saturn": {"longitude": 15.0}}
        natal = {"mars": {"longitude": 105.0}}  # rashi 3 (Cancer)
        result = _detect_aspects(curr, natal, datetime(2026, 2, 10), 5)
        assert any(t["aspect_house"] == 3 for t in result)

    def test_jupiter_special_5th(self):
        # Jupiter at rashi 0 (lon 15), need natal at rashi 4 (Leo, lon 135) -> dist=(4-0)%12=4, ||12=4
        # Need dist=5 for Jupiter special. Rashi 0 + 5 = rashi 5 (Virgo, lon 165)
        curr = {"jupiter": {"longitude": 15.0}}
        natal = {"sun": {"longitude": 165.0}}  # rashi 5 (Virgo)
        result = _detect_aspects(curr, natal, datetime(2026, 2, 10), 5)
        assert any(t["aspect_house"] == 5 for t in result)

    def test_aspect_significance_slow_planet(self):
        curr = {"saturn": {"longitude": 15.0}}
        natal = {"moon": {"longitude": 195.0}}
        result = _detect_aspects(curr, natal, datetime(2026, 2, 10), 5)
        if result:
            assert result[0]["significance"] == "high"

    def test_aspect_has_effect(self):
        curr = {"jupiter": {"longitude": 15.0}}
        natal = {"sun": {"longitude": 135.0}}
        result = _detect_aspects(curr, natal, datetime(2026, 2, 10), 5)
        if result:
            assert "effect" in result[0]


class TestDetectRetrogadeStations:
    """Test retrograde station detection."""

    def test_direct_to_retrograde(self):
        prev = {"mars": {"longitude": 100.0, "is_retrograde": False}}
        curr = {"mars": {"longitude": 99.5, "is_retrograde": True}}
        result = _detect_retrograde_stations(prev, curr, datetime(2026, 2, 10), 5)
        assert len(result) == 1
        assert result[0]["station"] == "retrograde"

    def test_retrograde_to_direct(self):
        prev = {"saturn": {"longitude": 340.0, "is_retrograde": True}}
        curr = {"saturn": {"longitude": 340.1, "is_retrograde": False}}
        result = _detect_retrograde_stations(prev, curr, datetime(2026, 2, 10), 5)
        assert len(result) == 1
        assert result[0]["station"] == "direct"

    def test_no_change(self):
        prev = {"mars": {"longitude": 100.0, "is_retrograde": False}}
        curr = {"mars": {"longitude": 101.0, "is_retrograde": False}}
        result = _detect_retrograde_stations(prev, curr, datetime(2026, 2, 10), 5)
        assert len(result) == 0

    def test_only_retrogradable_planets(self):
        # Sun and Moon cannot retrograde
        prev = {"sun": {"longitude": 100.0, "is_retrograde": False}}
        curr = {"sun": {"longitude": 101.0, "is_retrograde": True}}
        result = _detect_retrograde_stations(prev, curr, datetime(2026, 2, 10), 5)
        assert len(result) == 0

    def test_station_significance(self):
        prev = {"jupiter": {"longitude": 200.0, "is_retrograde": False}}
        curr = {"jupiter": {"longitude": 199.9, "is_retrograde": True}}
        result = _detect_retrograde_stations(prev, curr, datetime(2026, 2, 10), 5)
        assert result[0]["significance"] == "high"


class TestDetectDashaChanges:
    """Test dasha change detection."""

    def test_finds_pd_changes(self):
        # Within a 90-day window, there should be PD changes
        start = datetime(2026, 2, 1)
        result = _detect_dasha_changes(BIRTH_DT, MOON_LON, start, 90)
        pd_changes = [t for t in result if t["dasha_level"] == "pratyantardasha"]
        assert len(pd_changes) > 0

    def test_dasha_change_has_lord(self):
        start = datetime(2026, 2, 1)
        result = _detect_dasha_changes(BIRTH_DT, MOON_LON, start, 90)
        if result:
            assert "new_lord" in result[0]

    def test_dasha_change_has_date(self):
        start = datetime(2026, 2, 1)
        result = _detect_dasha_changes(BIRTH_DT, MOON_LON, start, 90)
        if result:
            assert "date" in result[0]

    def test_dasha_change_significance(self):
        start = datetime(2026, 2, 1)
        result = _detect_dasha_changes(BIRTH_DT, MOON_LON, start, 90)
        if result:
            assert result[0]["significance"] in ("high", "medium")


class TestGetUpcomingTriggers:
    """Test the main trigger finder (uses Swiss Ephemeris)."""

    def test_returns_list(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=10,
            start_date="2026-02-06",
            days_ahead=14,
        )
        assert isinstance(result, list)

    def test_triggers_have_expected_fields(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=10,
            start_date="2026-02-06",
            days_ahead=14,
        )
        if result:
            t = result[0]
            assert "date" in t
            assert "days_from_now" in t
            assert "trigger" in t
            assert "type" in t
            assert "significance" in t
            assert "effect" in t

    def test_sorted_by_date(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=10,
            start_date="2026-02-06",
            days_ahead=14,
        )
        if len(result) >= 2:
            assert result[0]["days_from_now"] <= result[1]["days_from_now"]

    def test_with_dasha_changes(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=10,
            start_date="2026-02-06",
            days_ahead=90,
            birth_datetime=BIRTH_DT,
            moon_longitude=MOON_LON,
        )
        dasha_triggers = [t for t in result if t["type"] == "dasha_change"]
        assert len(dasha_triggers) > 0

    def test_string_lagna(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi="libra",
            moon_rashi="aquarius",
            start_date="2026-02-06",
            days_ahead=7,
        )
        assert isinstance(result, list)

    def test_datetime_input(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=10,
            start_date=datetime(2026, 2, 6),
            days_ahead=7,
        )
        assert isinstance(result, list)

    def test_no_duplicate_triggers(self):
        result = get_upcoming_triggers(
            NATAL_PLANETS,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=10,
            start_date="2026-02-06",
            days_ahead=14,
        )
        # Check that trigger descriptions are unique
        # Some triggers may have same text for different dates, but the combination should be unique
        trigger_keys = [(t["trigger"], t["date"]) for t in result]
        assert len(trigger_keys) == len(set(trigger_keys))
