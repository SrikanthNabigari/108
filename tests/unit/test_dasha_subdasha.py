"""Tests for Sookshma, Prana, and Deha Dasha subdivisions in dasha.py."""

from datetime import datetime, timedelta

import pytest

from packages.context.src.dasha import (
    DASHA_SEQUENCE,
    get_current_dasha,
    get_deha_dasha_sequence,
    get_prana_dasha_sequence,
    get_sookshma_dasha_sequence,
)

# ---------- Test data ----------

# Mercury MD -> Venus AD -> Sun PD (typical mid-range period)
PD_LORD = "sun"
PD_START = datetime(2026, 3, 1)
PD_END = datetime(2026, 5, 30)  # ~90 days

# Short period: Ketu-Ketu chain
SHORT_LORD = "ketu"
SHORT_START = datetime(2026, 1, 1)
SHORT_END = datetime(2026, 1, 15)  # ~14 days

# Long period: Venus-Venus chain
LONG_LORD = "venus"
LONG_START = datetime(2025, 1, 1)
LONG_END = datetime(2025, 7, 15)  # ~195 days

# User birth data
BIRTH_DT = datetime(1992, 12, 3, 3, 0, 0)
MOON_LON = 326.85


# Helper: expected sequence starting from a given lord
def _expected_lords(start_lord: str) -> list[str]:
    """Return the 9-planet sequence starting from start_lord."""
    idx = DASHA_SEQUENCE.index(start_lord)
    return [DASHA_SEQUENCE[(idx + i) % 9] for i in range(9)]


# ======================================================================
# Sookshma Dasha Tests (Level 5)
# ======================================================================
class TestSookshmaDasha:
    """Test get_sookshma_dasha_sequence()."""

    def test_returns_9_periods(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        assert len(result) == 9

    def test_periods_sum_to_parent(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        total_days = sum((p["end_date"] - p["start_date"]).total_seconds() / 86400 for p in result)
        expected_days = (PD_END - PD_START).total_seconds() / 86400
        assert abs(total_days - expected_days) < 0.01

    def test_starts_with_parent_lord(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        assert result[0]["lord"] == PD_LORD

    def test_sequence_order(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        lords = [p["lord"] for p in result]
        assert lords == _expected_lords(PD_LORD)

    def test_contiguous_dates(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        for i in range(len(result) - 1):
            diff = abs((result[i]["end_date"] - result[i + 1]["start_date"]).total_seconds())
            assert diff < 1, f"Gap between period {i} and {i + 1}: {diff}s"

    def test_first_start_matches_parent(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        assert result[0]["start_date"] == PD_START

    def test_last_end_matches_parent(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        diff = abs((result[-1]["end_date"] - PD_END).total_seconds())
        assert diff < 1, f"Last end_date off by {diff}s"

    def test_invalid_lord_raises(self):
        with pytest.raises(ValueError, match="pluto"):
            get_sookshma_dasha_sequence("pluto", PD_START, PD_END)

    def test_duration_range(self):
        """Each Sookshma period should be 2-32 days for a ~90-day PD."""
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        for p in result:
            days = (p["end_date"] - p["start_date"]).total_seconds() / 86400
            assert 0.5 < days < 40, f"{p['lord']} SD has {days:.2f} days"

    def test_with_short_pd(self):
        """Ketu PD produces valid 9 periods even when very short."""
        result = get_sookshma_dasha_sequence(SHORT_LORD, SHORT_START, SHORT_END)
        assert len(result) == 9
        # Even shortest period should be positive
        for p in result:
            days = (p["end_date"] - p["start_date"]).total_seconds() / 86400
            assert days > 0, f"{p['lord']} SD has non-positive duration"

    def test_with_long_pd(self):
        """Venus PD produces valid 9 periods."""
        result = get_sookshma_dasha_sequence(LONG_LORD, LONG_START, LONG_END)
        assert len(result) == 9
        total_days = sum((p["end_date"] - p["start_date"]).total_seconds() / 86400 for p in result)
        expected_days = (LONG_END - LONG_START).total_seconds() / 86400
        assert abs(total_days - expected_days) < 0.01

    def test_has_required_keys(self):
        result = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        required_keys = {"lord", "start_date", "end_date", "years"}
        for p in result:
            assert required_keys.issubset(p.keys()), f"Missing keys: {required_keys - p.keys()}"


# ======================================================================
# Prana Dasha Tests (Level 6)
# ======================================================================
class TestPranaDasha:
    """Test get_prana_dasha_sequence()."""

    @pytest.fixture()
    def sd_period(self):
        """Get first Sookshma period from a standard PD to use as parent."""
        sookshmas = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        return sookshmas[0]

    def test_returns_9_periods(self, sd_period):
        result = get_prana_dasha_sequence(
            sd_period["lord"], sd_period["start_date"], sd_period["end_date"]
        )
        assert len(result) == 9

    def test_periods_sum_to_parent(self, sd_period):
        result = get_prana_dasha_sequence(
            sd_period["lord"], sd_period["start_date"], sd_period["end_date"]
        )
        total_secs = sum((p["end_date"] - p["start_date"]).total_seconds() for p in result)
        expected_secs = (sd_period["end_date"] - sd_period["start_date"]).total_seconds()
        assert abs(total_secs - expected_secs) < 1

    def test_starts_with_parent_lord(self, sd_period):
        result = get_prana_dasha_sequence(
            sd_period["lord"], sd_period["start_date"], sd_period["end_date"]
        )
        assert result[0]["lord"] == sd_period["lord"]

    def test_contiguous_dates(self, sd_period):
        result = get_prana_dasha_sequence(
            sd_period["lord"], sd_period["start_date"], sd_period["end_date"]
        )
        for i in range(len(result) - 1):
            diff = abs((result[i]["end_date"] - result[i + 1]["start_date"]).total_seconds())
            assert diff < 1, f"Gap between period {i} and {i + 1}: {diff}s"

    def test_duration_range(self, sd_period):
        """Prana periods typically span hours to a few days."""
        result = get_prana_dasha_sequence(
            sd_period["lord"], sd_period["start_date"], sd_period["end_date"]
        )
        for p in result:
            hours = (p["end_date"] - p["start_date"]).total_seconds() / 3600
            assert hours > 0, f"{p['lord']} Prana has non-positive duration"

    def test_invalid_lord_raises(self):
        with pytest.raises(ValueError):
            get_prana_dasha_sequence("pluto", datetime(2026, 1, 1), datetime(2026, 1, 5))

    def test_smallest_period(self):
        """Ketu-Ketu chain should still have valid positive durations."""
        sookshmas = get_sookshma_dasha_sequence(SHORT_LORD, SHORT_START, SHORT_END)
        sd = sookshmas[0]  # Ketu SD (shortest)
        result = get_prana_dasha_sequence(sd["lord"], sd["start_date"], sd["end_date"])
        assert len(result) == 9
        for p in result:
            secs = (p["end_date"] - p["start_date"]).total_seconds()
            assert secs > 0, f"{p['lord']} Prana has non-positive duration"

    def test_largest_period(self):
        """Venus-Venus chain should produce the longest Prana periods."""
        sookshmas = get_sookshma_dasha_sequence(LONG_LORD, LONG_START, LONG_END)
        # Venus SD is first (longest in Venus-Venus chain)
        sd = sookshmas[0]
        result = get_prana_dasha_sequence(sd["lord"], sd["start_date"], sd["end_date"])
        assert len(result) == 9
        # Longest Prana in Venus chain should be > 1 day
        max_hours = max((p["end_date"] - p["start_date"]).total_seconds() / 3600 for p in result)
        assert max_hours > 24, f"Max Prana is only {max_hours:.1f} hours"


# ======================================================================
# Deha Dasha Tests (Level 7)
# ======================================================================
class TestDehaDasha:
    """Test get_deha_dasha_sequence()."""

    @pytest.fixture()
    def prana_period(self):
        """Get first Prana period from a standard chain to use as parent."""
        sookshmas = get_sookshma_dasha_sequence(PD_LORD, PD_START, PD_END)
        pranas = get_prana_dasha_sequence(
            sookshmas[0]["lord"], sookshmas[0]["start_date"], sookshmas[0]["end_date"]
        )
        return pranas[0]

    def test_returns_9_periods(self, prana_period):
        result = get_deha_dasha_sequence(
            prana_period["lord"],
            prana_period["start_date"],
            prana_period["end_date"],
        )
        assert len(result) == 9

    def test_periods_sum_to_parent(self, prana_period):
        result = get_deha_dasha_sequence(
            prana_period["lord"],
            prana_period["start_date"],
            prana_period["end_date"],
        )
        total_secs = sum((p["end_date"] - p["start_date"]).total_seconds() for p in result)
        expected_secs = (prana_period["end_date"] - prana_period["start_date"]).total_seconds()
        assert abs(total_secs - expected_secs) < 1

    def test_starts_with_parent_lord(self, prana_period):
        result = get_deha_dasha_sequence(
            prana_period["lord"],
            prana_period["start_date"],
            prana_period["end_date"],
        )
        assert result[0]["lord"] == prana_period["lord"]

    def test_contiguous_dates(self, prana_period):
        result = get_deha_dasha_sequence(
            prana_period["lord"],
            prana_period["start_date"],
            prana_period["end_date"],
        )
        for i in range(len(result) - 1):
            diff = abs((result[i]["end_date"] - result[i + 1]["start_date"]).total_seconds())
            assert diff < 1, f"Gap between period {i} and {i + 1}: {diff}s"

    def test_duration_range(self, prana_period):
        """Deha periods typically span minutes to hours."""
        result = get_deha_dasha_sequence(
            prana_period["lord"],
            prana_period["start_date"],
            prana_period["end_date"],
        )
        for p in result:
            secs = (p["end_date"] - p["start_date"]).total_seconds()
            assert secs > 0, f"{p['lord']} Deha has non-positive duration"

    def test_invalid_lord_raises(self):
        with pytest.raises(ValueError):
            get_deha_dasha_sequence("pluto", datetime(2026, 1, 1), datetime(2026, 1, 2))

    def test_smallest_practical(self):
        """Very short parent period should still yield positive durations."""
        # Use a 1-hour parent
        start = datetime(2026, 6, 1, 10, 0, 0)
        end = datetime(2026, 6, 1, 11, 0, 0)
        result = get_deha_dasha_sequence("mars", start, end)
        assert len(result) == 9
        for p in result:
            secs = (p["end_date"] - p["start_date"]).total_seconds()
            assert secs > 0, f"{p['lord']} Deha has non-positive duration"


# ======================================================================
# get_current_dasha with Sookshma level
# ======================================================================
class TestCurrentDashaWithSookshma:
    """Test that get_current_dasha returns the new sookshma_dasha key."""

    @pytest.fixture()
    def current(self):
        return get_current_dasha(BIRTH_DT, MOON_LON, datetime(2026, 3, 15))

    def test_has_sookshma_key(self, current):
        assert current is not None
        assert "sookshma_dasha" in current

    def test_lord_is_valid(self, current):
        sd = current["sookshma_dasha"]
        assert sd is not None
        assert sd["lord"] in DASHA_SEQUENCE

    def test_within_pd_range(self, current):
        pd = current["pratyantardasha"]
        sd = current["sookshma_dasha"]
        assert sd["start_date"] >= pd["start_date"]
        assert sd["end_date"] <= pd["end_date"] + timedelta(seconds=2)

    def test_has_days_remaining(self, current):
        sd = current["sookshma_dasha"]
        assert "days_remaining" in sd
        assert sd["days_remaining"] > 0

    def test_backward_compat(self, current):
        """Original keys must still be present."""
        assert "mahadasha" in current
        assert "antardasha" in current
        assert "pratyantardasha" in current
        assert "current_datetime" in current
