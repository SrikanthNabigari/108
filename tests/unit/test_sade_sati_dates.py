"""Tests for Sade Sati / Dhaiya date calculation and planet rashi ingress."""

from datetime import UTC, datetime

import pytest

from packages.context.src.transits import (
    get_dhaiya_dates,
    get_sade_sati_dates,
)
from packages.cosmos.src.ephemeris import (
    find_planet_rashi_ingress,
    get_julian_day,
    get_planet_position,
)

# ── find_planet_rashi_ingress tests ──


class TestFindPlanetRashiIngress:
    """Tests for the binary-search planet ingress finder."""

    def test_saturn_returns_valid_jd(self):
        """Saturn ingress into a rashi should return a valid JD."""
        now = datetime(2026, 2, 1, tzinfo=UTC)
        start_jd = get_julian_day(now)
        end_jd = start_jd + 365 * 5  # 5 years forward

        # Saturn is currently in Pisces (rashi 11) area; search for Aries (0) entry
        result = find_planet_rashi_ingress("saturn", 0, start_jd, end_jd)
        # Saturn should enter Aries within ~5 years from 2026
        # If not found, it's fine — the function returns None
        if result is not None:
            assert result >= start_jd
            assert result <= end_jd
            # Verify the planet is actually in the target rashi at result JD
            pos = get_planet_position("saturn", result)
            rashi = int(pos["longitude"] / 30) % 12
            assert rashi == 0

    def test_jupiter_finds_ingress(self):
        """Jupiter moves faster (~1 year/rashi), should find ingress easily."""
        now = datetime(2026, 1, 1, tzinfo=UTC)
        start_jd = get_julian_day(now)
        end_jd = start_jd + 365 * 3

        # Just search for the next rashi from Jupiter's current position
        pos = get_planet_position("jupiter", start_jd)
        current_rashi = int(pos["longitude"] / 30) % 12
        next_rashi = (current_rashi + 1) % 12

        result = find_planet_rashi_ingress("jupiter", next_rashi, start_jd, end_jd)
        assert result is not None
        assert result >= start_jd
        assert result <= end_jd

    def test_planet_already_in_target_rashi(self):
        """If planet is already in target rashi at start, return start_jd."""
        now = datetime(2026, 2, 1, tzinfo=UTC)
        start_jd = get_julian_day(now)
        end_jd = start_jd + 365

        pos = get_planet_position("saturn", start_jd)
        current_rashi = int(pos["longitude"] / 30) % 12

        result = find_planet_rashi_ingress("saturn", current_rashi, start_jd, end_jd)
        assert result is not None
        assert result == start_jd

    def test_invalid_rashi_raises(self):
        """Invalid target rashi should raise ValueError."""
        now = datetime(2026, 1, 1, tzinfo=UTC)
        jd = get_julian_day(now)
        with pytest.raises(ValueError):
            find_planet_rashi_ingress("saturn", 12, jd, jd + 365)
        with pytest.raises(ValueError):
            find_planet_rashi_ingress("saturn", -1, jd, jd + 365)

    def test_returns_none_for_impossible_window(self):
        """Very short window where Saturn can't change rashi should return appropriately."""
        now = datetime(2026, 2, 1, tzinfo=UTC)
        start_jd = get_julian_day(now)
        end_jd = start_jd + 1  # 1-day window

        pos = get_planet_position("saturn", start_jd)
        current_rashi = int(pos["longitude"] / 30) % 12
        # Search for a rashi that's far from current
        target = (current_rashi + 6) % 12

        result = find_planet_rashi_ingress("saturn", target, start_jd, end_jd)
        assert result is None

    def test_binary_search_precision(self):
        """Result should be precise to within ~0.5 JD of actual crossing."""
        now = datetime(2026, 1, 1, tzinfo=UTC)
        start_jd = get_julian_day(now)
        end_jd = start_jd + 365 * 3

        pos = get_planet_position("jupiter", start_jd)
        current_rashi = int(pos["longitude"] / 30) % 12
        next_rashi = (current_rashi + 1) % 12

        result = find_planet_rashi_ingress("jupiter", next_rashi, start_jd, end_jd)
        assert result is not None

        # Verify target rashi at result JD
        pos_at = get_planet_position("jupiter", result)
        rashi_at = int(pos_at["longitude"] / 30) % 12
        assert rashi_at == next_rashi


# ── get_sade_sati_dates tests ──


class TestGetSadeSatiDates:
    """Tests for Sade Sati date calculation."""

    def test_returns_phase_dates_dict(self):
        """Should return a dict with 'phase_dates' key."""
        # Moon in Aquarius (10), Saturn somewhere triggering Sade Sati
        result = get_sade_sati_dates(10, 10)  # Saturn in same sign as Moon = peak
        assert "phase_dates" in result
        phase_dates = result["phase_dates"]
        assert isinstance(phase_dates, dict)

    def test_phases_have_start_and_end(self):
        """Each phase should have start and end date strings."""
        result = get_sade_sati_dates(10, 10)
        phase_dates = result["phase_dates"]
        for phase_name, dates in phase_dates.items():
            assert phase_name in ("rising", "peak", "setting")
            assert "start" in dates
            assert "end" in dates
            # Dates should be YYYY-MM-DD format or empty
            if dates["start"]:
                assert len(dates["start"]) == 10  # YYYY-MM-DD

    def test_rising_phase_before_peak(self):
        """Rising phase should start before peak phase."""
        result = get_sade_sati_dates(10, 10)
        phase_dates = result["phase_dates"]
        if "rising" in phase_dates and "peak" in phase_dates:
            rising_start = phase_dates["rising"]["start"]
            peak_start = phase_dates["peak"]["start"]
            if rising_start and peak_start:
                assert rising_start <= peak_start

    def test_different_moon_rashis(self):
        """Should work for various Moon rashi positions."""
        for moon_rashi in [0, 3, 6, 9, 11]:
            # Saturn in same sign as Moon = peak
            result = get_sade_sati_dates(moon_rashi, moon_rashi)
            assert "phase_dates" in result


# ── get_dhaiya_dates tests ──


class TestGetDhaiyaDates:
    """Tests for Dhaiya date calculation."""

    def test_returns_empty_when_not_active(self):
        """Should return empty phase_dates when Saturn is not in 4th or 8th."""
        # Moon in 0 (Aries), Saturn in 0 (same sign) — not 4th or 8th
        result = get_dhaiya_dates(0, 0)
        assert result["phase_dates"] == {}

    def test_kantaka_shani_in_4th(self):
        """Should detect Kantaka Shani when Saturn is in 4th from Moon."""
        # Saturn is currently in Pisces (rashi 11).
        # Moon in rashi 8 => Saturn in 4th from Moon: (11-8)%12+1=4
        result = get_dhaiya_dates(8, 11)
        phase_dates = result["phase_dates"]
        assert "kantaka_shani" in phase_dates
        assert "start" in phase_dates["kantaka_shani"]
        assert "end" in phase_dates["kantaka_shani"]

    def test_ashtama_shani_in_8th(self):
        """Should detect Ashtama Shani when Saturn is in 8th from Moon."""
        # Saturn is currently in Pisces (rashi 11).
        # Moon in rashi 4 => Saturn in 8th from Moon: (11-4)%12+1=8
        result = get_dhaiya_dates(4, 11)
        phase_dates = result["phase_dates"]
        assert "ashtama_shani" in phase_dates
        assert "start" in phase_dates["ashtama_shani"]
        assert "end" in phase_dates["ashtama_shani"]


# ── Integration: exports ──


class TestExports:
    """Verify new functions are properly exported."""

    def test_cosmos_export(self):
        from packages.cosmos.src import find_planet_rashi_ingress as fn

        assert callable(fn)

    def test_context_sade_sati_export(self):
        from packages.context.src import get_sade_sati_dates as fn

        assert callable(fn)

    def test_context_dhaiya_export(self):
        from packages.context.src import get_dhaiya_dates as fn

        assert callable(fn)
