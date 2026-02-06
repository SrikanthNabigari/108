"""Unit tests for Yogini Dasha calculations."""

from datetime import UTC, datetime, timedelta

import pytest

from packages.context.src.yogini_dasha import (
    TOTAL_CYCLE,
    YOGINI_DATA,
    YOGINI_EFFECTS,
    calculate_yogini_sequence,
    get_current_yogini_dasha,
    get_starting_yogini,
    get_yogini_antardasha,
    get_yogini_balance_at_birth,
    get_yogini_effects,
    get_yogini_pratyantardasha,
)
from packages.core.src.constants import Planet, YoginiName
from packages.core.src.models import YoginiDashaPeriod


class TestStartingYogini:
    """Test starting yogini calculation."""

    def test_ashwini_pada1(self):
        """Test Ashwini pada 1."""
        # Nakshatra 1, Pada 1: (1-1)*4 + 1 = 1, (1+3)%8 = 4
        result = get_starting_yogini(1, 1)
        assert result == 4
        assert YOGINI_DATA[result][0] == YoginiName.BHADRIKA

    def test_bharani_pada2(self):
        """Test Bharani pada 2."""
        # Nakshatra 2, Pada 2: (2-1)*4 + 2 = 6, (6+3)%8 = 1
        result = get_starting_yogini(2, 2)
        assert result == 1
        assert YOGINI_DATA[result][0] == YoginiName.PINGALA

    def test_purva_bhadrapada_pada3(self):
        """Test Purva Bhadrapada pada 3."""
        # Nakshatra 25, Pada 3: (25-1)*4 + 3 = 99, (99+3)%8 = 6
        result = get_starting_yogini(25, 3)
        assert result == 6
        assert YOGINI_DATA[result][0] == YoginiName.SIDDHA

    def test_revati_pada4(self):
        """Test Revati pada 4 (last nakshatra-pada)."""
        # Nakshatra 27, Pada 4: (27-1)*4 + 4 = 108, (108+3)%8 = 7
        result = get_starting_yogini(27, 4)
        assert result == 7
        assert YOGINI_DATA[result][0] == YoginiName.SANKATA

    def test_invalid_nakshatra(self):
        """Test with invalid nakshatra number."""
        with pytest.raises(ValueError, match="Nakshatra number must be 1-27"):
            get_starting_yogini(0, 1)

        with pytest.raises(ValueError, match="Nakshatra number must be 1-27"):
            get_starting_yogini(28, 1)

    def test_invalid_pada(self):
        """Test with invalid pada number."""
        with pytest.raises(ValueError, match="Pada must be 1-4"):
            get_starting_yogini(1, 0)

        with pytest.raises(ValueError, match="Pada must be 1-4"):
            get_starting_yogini(1, 5)


class TestYoginiBalance:
    """Test yogini balance at birth calculation."""

    def test_beginning_of_nakshatra(self):
        """Test at the beginning of nakshatra (0 degrees)."""
        balance = get_yogini_balance_at_birth(1, 1, 0.0)
        assert balance["yogini_index"] == 4
        assert balance["yogini"] == YoginiName.BHADRIKA
        assert balance["lord"] == Planet.MERCURY
        assert balance["total_years"] == 5
        assert balance["elapsed_years"] == pytest.approx(0.0)
        assert balance["remaining_years"] == pytest.approx(5.0)

    def test_middle_of_nakshatra(self):
        """Test at the middle of nakshatra (6.666 degrees)."""
        balance = get_yogini_balance_at_birth(25, 3, 6.666)
        assert balance["yogini"] == YoginiName.SIDDHA
        assert balance["total_years"] == 7
        # 6.666 / 13.333 ≈ 0.5
        assert balance["elapsed_years"] == pytest.approx(3.5, abs=0.1)
        assert balance["remaining_years"] == pytest.approx(3.5, abs=0.1)

    def test_end_of_nakshatra(self):
        """Test near the end of nakshatra (13.0 degrees)."""
        balance = get_yogini_balance_at_birth(10, 2, 13.0)
        yogini_index = get_starting_yogini(10, 2)
        total_years = YOGINI_DATA[yogini_index][2]
        # 13.0 / 13.333 ≈ 0.975
        elapsed = balance["elapsed_years"]
        remaining = balance["remaining_years"]
        assert elapsed + remaining == pytest.approx(total_years, abs=0.01)
        assert remaining < 0.5  # Very little remaining

    def test_invalid_degree(self):
        """Test with invalid degree value."""
        with pytest.raises(ValueError, match="Degree in nakshatra must be"):
            get_yogini_balance_at_birth(1, 1, -1.0)

        with pytest.raises(ValueError, match="Degree in nakshatra must be"):
            get_yogini_balance_at_birth(1, 1, 14.0)


class TestYoginiSequence:
    """Test yogini dasha sequence generation."""

    def test_sequence_count_one_cycle(self):
        """Test that one cycle generates 8 periods."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        periods = calculate_yogini_sequence(birth_dt, 25, 3, 10.0, cycles=1)
        # First period is partial, then 7 more to complete the cycle
        assert len(periods) == 8

    def test_sequence_count_three_cycles(self):
        """Test that three cycles generate 24 periods."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        periods = calculate_yogini_sequence(birth_dt, 25, 3, 10.0, cycles=3)
        # 8 periods per cycle x 3 cycles = 24
        assert len(periods) == 24

    def test_sequence_starts_at_birth(self):
        """Test that sequence starts at birth datetime."""
        birth_dt = datetime(1992, 12, 3, 3, 0, 0, tzinfo=UTC)
        periods = calculate_yogini_sequence(birth_dt, 1, 1, 0.0, cycles=1)
        assert periods[0].start_date == birth_dt

    def test_sequence_no_overlaps(self):
        """Test that periods don't overlap."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        periods = calculate_yogini_sequence(birth_dt, 10, 2, 5.0, cycles=2)
        for i in range(len(periods) - 1):
            # End of one period should equal start of next
            assert periods[i].end_date == periods[i + 1].start_date

    def test_sequence_yogini_cycle(self):
        """Test that yoginis cycle in correct order."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        # Start at Bhadrika (index 4)
        periods = calculate_yogini_sequence(birth_dt, 1, 1, 0.0, cycles=1)

        expected_order = [
            YoginiName.BHADRIKA,  # Starting yogini (index 4)
            YoginiName.ULKA,  # index 5
            YoginiName.SIDDHA,  # index 6
            YoginiName.SANKATA,  # index 7
            YoginiName.MANGALA,  # index 0 (wrap around)
            YoginiName.PINGALA,  # index 1
            YoginiName.DHANYA,  # index 2
            YoginiName.BHRAMARI,  # index 3
        ]

        for i, period in enumerate(periods):
            assert period.yogini == expected_order[i]

    def test_first_period_duration(self):
        """Test that first period uses remaining years correctly."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        # At middle of nakshatra, should have ~3.5 years remaining for 7-year yogini
        periods = calculate_yogini_sequence(birth_dt, 25, 3, 6.666, cycles=1)

        first_period_days = (periods[0].end_date - periods[0].start_date).days
        # Approximately 3.5 years = ~1278 days
        assert abs(first_period_days - 1278) < 10  # Allow small tolerance

    def test_total_cycle_duration(self):
        """Test that one complete cycle is approximately 36 years."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        # Start at beginning of nakshatra for clean calculation
        periods = calculate_yogini_sequence(birth_dt, 1, 1, 0.0, cycles=1)

        first_start = periods[0].start_date
        last_end = periods[-1].end_date
        total_days = (last_end - first_start).days

        # 36 years = 13149 days (accounting for leap years)
        expected_days = int(36 * 365.25)
        assert abs(total_days - expected_days) < 50  # Allow small tolerance


class TestCurrentYoginiDasha:
    """Test current yogini dasha lookup."""

    def test_current_in_first_period(self):
        """Test query date in first period."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        # Query 6 months after birth
        query_dt = birth_dt + timedelta(days=180)

        current = get_current_yogini_dasha(birth_dt, 25, 3, 10.0, query_dt)
        assert current["yogini"] == YoginiName.SIDDHA
        assert current["lord"] == Planet.VENUS
        assert current["start_date"] == birth_dt
        assert 0 < current["remaining_days"] < 365 * 7

    def test_current_in_later_period(self):
        """Test query date in a later period."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        # Query 10 years after birth
        query_dt = birth_dt + timedelta(days=10 * 365)

        current = get_current_yogini_dasha(birth_dt, 25, 3, 10.0, query_dt)
        assert current["yogini"] in [y[0] for y in YOGINI_DATA]
        assert current["remaining_days"] >= 0

    def test_current_defaults_to_now(self):
        """Test that query_dt defaults to now."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        current = get_current_yogini_dasha(birth_dt, 25, 3, 10.0)
        assert "yogini" in current
        assert "remaining_days" in current

    def test_remaining_days_calculation(self):
        """Test remaining days calculation."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        periods = calculate_yogini_sequence(birth_dt, 25, 3, 10.0, cycles=2)

        # Query in the middle of second period
        query_dt = periods[1].start_date + timedelta(days=100)
        current = get_current_yogini_dasha(birth_dt, 25, 3, 10.0, query_dt)

        expected_remaining = (periods[1].end_date - query_dt).days
        assert current["remaining_days"] == expected_remaining


class TestYoginiAntardasha:
    """Test yogini antardasha subdivision."""

    def test_antardasha_count(self):
        """Test that 8 antardashas are generated."""
        maha = YoginiDashaPeriod(
            yogini=YoginiName.BHADRIKA,
            planet_lord=Planet.MERCURY,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, tzinfo=UTC),
            duration_years=5,
        )
        antardashas = get_yogini_antardasha(maha)
        assert len(antardashas) == 8

    def test_antardasha_sequence_starts_with_maha(self):
        """Test that antardasha sequence starts with maha yogini."""
        maha = YoginiDashaPeriod(
            yogini=YoginiName.BHADRIKA,
            planet_lord=Planet.MERCURY,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, tzinfo=UTC),
            duration_years=5,
        )
        antardashas = get_yogini_antardasha(maha)
        assert antardashas[0]["yogini"] == YoginiName.BHADRIKA

    def test_antardasha_covers_maha_period(self):
        """Test that antardashas cover the entire maha period."""
        maha = YoginiDashaPeriod(
            yogini=YoginiName.ULKA,
            planet_lord=Planet.SATURN,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 1, 1, tzinfo=UTC),
            duration_years=6,
        )
        antardashas = get_yogini_antardasha(maha)

        assert antardashas[0]["start_date"] == maha.start_date
        assert antardashas[-1]["end_date"] <= maha.end_date

    def test_antardasha_no_overlaps(self):
        """Test that antardashas don't overlap."""
        maha = YoginiDashaPeriod(
            yogini=YoginiName.SIDDHA,
            planet_lord=Planet.VENUS,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2027, 1, 1, tzinfo=UTC),
            duration_years=7,
        )
        antardashas = get_yogini_antardasha(maha)

        for i in range(len(antardashas) - 1):
            assert antardashas[i]["end_date"] == antardashas[i + 1]["start_date"]

    def test_antardasha_proportional_duration(self):
        """Test that antardasha durations are proportional."""
        maha = YoginiDashaPeriod(
            yogini=YoginiName.MANGALA,
            planet_lord=Planet.MOON,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2021, 1, 1, tzinfo=UTC),
            duration_years=1,
        )
        antardashas = get_yogini_antardasha(maha)
        maha_days = (maha.end_date - maha.start_date).days

        # First antardasha (Mangala) = 1/36 of maha
        first_days = (antardashas[0]["end_date"] - antardashas[0]["start_date"]).days
        expected_first = int((1 / TOTAL_CYCLE) * maha_days)
        assert abs(first_days - expected_first) <= 1

        # Second antardasha (Pingala) = 2/36 of maha
        second_days = (antardashas[1]["end_date"] - antardashas[1]["start_date"]).days
        expected_second = int((2 / TOTAL_CYCLE) * maha_days)
        assert abs(second_days - expected_second) <= 1

    def test_antardasha_with_different_starting_yogini(self):
        """Test antardasha with different starting yogini."""
        maha = YoginiDashaPeriod(
            yogini=YoginiName.SANKATA,
            planet_lord=Planet.RAHU,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2028, 1, 1, tzinfo=UTC),
            duration_years=8,
        )
        antardashas = get_yogini_antardasha(maha)

        # Should start with Sankata (index 7) and cycle
        expected_sequence = [
            YoginiName.SANKATA,  # index 7
            YoginiName.MANGALA,  # index 0 (wrap)
            YoginiName.PINGALA,  # index 1
            YoginiName.DHANYA,  # index 2
            YoginiName.BHRAMARI,  # index 3
            YoginiName.BHADRIKA,  # index 4
            YoginiName.ULKA,  # index 5
            YoginiName.SIDDHA,  # index 6
        ]

        for i, antardasha in enumerate(antardashas):
            assert antardasha["yogini"] == expected_sequence[i]


class TestYoginiEffects:
    """Tests for YOGINI_EFFECTS and get_yogini_effects."""

    def test_all_eight_yoginis_present(self):
        expected = [
            "mangala",
            "pingala",
            "dhanya",
            "bhramari",
            "bhadrika",
            "ulka",
            "siddha",
            "sankata",
        ]
        for name in expected:
            assert name in YOGINI_EFFECTS

    def test_each_effect_has_required_fields(self):
        required_fields = [
            "planet",
            "years",
            "general",
            "positive",
            "negative",
            "health",
            "career",
            "relationships",
            "spiritual",
        ]
        for name, effects in YOGINI_EFFECTS.items():
            for field in required_fields:
                assert field in effects, f"Missing '{field}' for {name}"

    def test_mangala_planet_is_moon(self):
        assert YOGINI_EFFECTS["mangala"]["planet"] == "moon"

    def test_mangala_years_is_1(self):
        assert YOGINI_EFFECTS["mangala"]["years"] == 1

    def test_sankata_planet_is_rahu(self):
        assert YOGINI_EFFECTS["sankata"]["planet"] == "rahu"

    def test_sankata_years_is_8(self):
        assert YOGINI_EFFECTS["sankata"]["years"] == 8

    def test_positive_is_list(self):
        for name, effects in YOGINI_EFFECTS.items():
            assert isinstance(effects["positive"], list), f"positive not list for {name}"
            assert len(effects["positive"]) > 0, f"Empty positive for {name}"

    def test_negative_is_list(self):
        for name, effects in YOGINI_EFFECTS.items():
            assert isinstance(effects["negative"], list), f"negative not list for {name}"
            assert len(effects["negative"]) > 0, f"Empty negative for {name}"

    def test_get_yogini_effects_valid_name(self):
        result = get_yogini_effects("mangala")
        assert result["planet"] == "moon"
        assert result["years"] == 1

    def test_get_yogini_effects_case_insensitive(self):
        result = get_yogini_effects("MANGALA")
        assert result["planet"] == "moon"

    def test_get_yogini_effects_invalid_name(self):
        result = get_yogini_effects("nonexistent")
        assert result == {}

    def test_year_totals_match_cycle(self):
        total = sum(YOGINI_EFFECTS[name]["years"] for name in YOGINI_EFFECTS)
        assert total == TOTAL_CYCLE  # 36


class TestYoginiPratyantardasha:
    """Tests for get_yogini_pratyantardasha (3rd level)."""

    def test_pratyantardasha_count(self):
        ad = {
            "yogini": YoginiName.BHADRIKA,
            "lord": Planet.MERCURY,
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),
            "end_date": datetime(2020, 7, 1, tzinfo=UTC),
        }
        pads = get_yogini_pratyantardasha(ad)
        assert len(pads) == 8

    def test_pratyantardasha_starts_with_antardasha_yogini(self):
        ad = {
            "yogini": YoginiName.ULKA,
            "lord": Planet.SATURN,
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),
            "end_date": datetime(2020, 6, 1, tzinfo=UTC),
        }
        pads = get_yogini_pratyantardasha(ad)
        assert pads[0]["yogini"] == YoginiName.ULKA

    def test_pratyantardasha_no_overlaps(self):
        ad = {
            "yogini": YoginiName.SIDDHA,
            "lord": Planet.VENUS,
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),
            "end_date": datetime(2021, 1, 1, tzinfo=UTC),
        }
        pads = get_yogini_pratyantardasha(ad)
        for i in range(len(pads) - 1):
            assert pads[i]["end_date"] == pads[i + 1]["start_date"]

    def test_pratyantardasha_within_antardasha_bounds(self):
        ad = {
            "yogini": YoginiName.MANGALA,
            "lord": Planet.MOON,
            "start_date": datetime(2020, 3, 1, tzinfo=UTC),
            "end_date": datetime(2020, 6, 1, tzinfo=UTC),
        }
        pads = get_yogini_pratyantardasha(ad)
        assert pads[0]["start_date"] == ad["start_date"]
        assert pads[-1]["end_date"] <= ad["end_date"]

    def test_pratyantardasha_proportional_duration(self):
        ad = {
            "yogini": YoginiName.MANGALA,
            "lord": Planet.MOON,
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),
            "end_date": datetime(2021, 1, 1, tzinfo=UTC),
        }
        pads = get_yogini_pratyantardasha(ad)
        ad_days = (ad["end_date"] - ad["start_date"]).days

        # First PAD (Mangala) = 1/36 of AD duration
        first_days = (pads[0]["end_date"] - pads[0]["start_date"]).days
        expected = int((1 / TOTAL_CYCLE) * ad_days)
        assert abs(first_days - expected) <= 1

    def test_pratyantardasha_cycles_correctly(self):
        ad = {
            "yogini": YoginiName.SANKATA,
            "lord": Planet.RAHU,
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),
            "end_date": datetime(2020, 12, 1, tzinfo=UTC),
        }
        pads = get_yogini_pratyantardasha(ad)
        expected = [
            YoginiName.SANKATA,
            YoginiName.MANGALA,
            YoginiName.PINGALA,
            YoginiName.DHANYA,
            YoginiName.BHRAMARI,
            YoginiName.BHADRIKA,
            YoginiName.ULKA,
            YoginiName.SIDDHA,
        ]
        for i, pad in enumerate(pads):
            assert pad["yogini"] == expected[i]

    def test_pratyantardasha_invalid_yogini_raises(self):
        ad = {
            "yogini": "invalid",
            "lord": Planet.MOON,
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),
            "end_date": datetime(2020, 6, 1, tzinfo=UTC),
        }
        with pytest.raises(ValueError, match="Invalid yogini"):
            get_yogini_pratyantardasha(ad)
