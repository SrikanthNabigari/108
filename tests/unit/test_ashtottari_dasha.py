"""Unit tests for Ashtottari Dasha calculations."""

from datetime import datetime, timedelta

import pytest

from packages.context.src.ashtottari_dasha import (
    _ALL_NAKSHATRA_TO_LORD,
    ASHTOTTARI_DATA,
    TOTAL_CYCLE,
    calculate_ashtottari_balance,
    calculate_ashtottari_sequence,
    get_ashtottari_antardasha,
    get_current_ashtottari,
    get_starting_lord,
    is_ashtottari_applicable,
)

# Standard test birth data: Dec 3, 1992, 3:00 AM IST -> 21:30 UTC Dec 2
BIRTH_DT = datetime(1992, 12, 2, 21, 30)  # UTC equivalent
# Moon in Purva Bhadrapada (nakshatra 25), ~10 degrees into nakshatra
MOON_NAKSHATRA = 25
DEGREE_IN_NAKSHATRA = 10.0


class TestConstants:
    """Test Ashtottari constants."""

    def test_total_cycle_is_108(self):
        """Total cycle must equal 108 years."""
        total = sum(years for _, years in ASHTOTTARI_DATA)
        assert total == 108
        assert TOTAL_CYCLE == 108

    def test_eight_planets(self):
        """Must have exactly 8 planets (no Ketu)."""
        assert len(ASHTOTTARI_DATA) == 8
        lords = [name for name, _ in ASHTOTTARI_DATA]
        assert "ketu" not in lords

    def test_sequence_order(self):
        """Verify the correct sequence: Sun, Moon, Mars, Mercury, Saturn, Jupiter, Rahu, Venus."""
        expected = ["sun", "moon", "mars", "mercury", "saturn", "jupiter", "rahu", "venus"]
        actual = [name for name, _ in ASHTOTTARI_DATA]
        assert actual == expected

    def test_individual_years(self):
        """Test individual planet years."""
        years_map = dict(ASHTOTTARI_DATA)
        assert years_map["sun"] == 6
        assert years_map["moon"] == 15
        assert years_map["mars"] == 8
        assert years_map["mercury"] == 17
        assert years_map["saturn"] == 10
        assert years_map["jupiter"] == 19
        assert years_map["rahu"] == 12
        assert years_map["venus"] == 21

    def test_all_27_nakshatras_mapped(self):
        """All 27 nakshatras should have a lord mapping."""
        for i in range(1, 28):
            assert i in _ALL_NAKSHATRA_TO_LORD, f"Nakshatra {i} has no mapping"


class TestIsAshtottariApplicable:
    """Test applicability check for Ashtottari Dasha."""

    def test_rahu_in_same_house_as_lagna_lord(self):
        """Rahu conjunct Lagna lord (house 1 from itself) is kendra."""
        assert is_ashtottari_applicable(1, 1) is True

    def test_rahu_in_4th_from_lagna_lord(self):
        """Rahu in 4th from Lagna lord is kendra."""
        assert is_ashtottari_applicable(4, 1) is True

    def test_rahu_in_7th_from_lagna_lord(self):
        """Rahu in 7th from Lagna lord is kendra."""
        assert is_ashtottari_applicable(7, 1) is True

    def test_rahu_in_10th_from_lagna_lord(self):
        """Rahu in 10th from Lagna lord is kendra."""
        assert is_ashtottari_applicable(10, 1) is True

    def test_rahu_in_5th_from_lagna_lord(self):
        """Rahu in 5th from Lagna lord is trikona."""
        assert is_ashtottari_applicable(5, 1) is True

    def test_rahu_in_9th_from_lagna_lord(self):
        """Rahu in 9th from Lagna lord is trikona."""
        assert is_ashtottari_applicable(9, 1) is True

    def test_rahu_in_6th_not_applicable(self):
        """Rahu in 6th from Lagna lord is dusthana, not applicable."""
        assert is_ashtottari_applicable(6, 1) is False

    def test_rahu_in_8th_not_applicable(self):
        """Rahu in 8th from Lagna lord is dusthana, not applicable."""
        assert is_ashtottari_applicable(8, 1) is False

    def test_rahu_in_12th_not_applicable(self):
        """Rahu in 12th from Lagna lord is dusthana, not applicable."""
        assert is_ashtottari_applicable(12, 1) is False

    def test_rahu_in_2nd_not_applicable(self):
        """Rahu in 2nd from Lagna lord is maraka, not applicable."""
        assert is_ashtottari_applicable(2, 1) is False

    def test_rahu_in_3rd_not_applicable(self):
        """Rahu in 3rd from Lagna lord, not applicable."""
        assert is_ashtottari_applicable(3, 1) is False

    def test_rahu_in_11th_not_applicable(self):
        """Rahu in 11th from Lagna lord, not applicable."""
        assert is_ashtottari_applicable(11, 1) is False

    def test_different_base_house(self):
        """Test with Lagna lord in house 5, Rahu in house 9 (5th from 5)."""
        assert is_ashtottari_applicable(9, 5) is True

    def test_wrap_around(self):
        """Test house calculation wrap-around: Lagna lord in 10, Rahu in 1 (4th from 10)."""
        assert is_ashtottari_applicable(1, 10) is True

    def test_invalid_rahu_house(self):
        """Invalid Rahu house raises ValueError."""
        with pytest.raises(ValueError, match="Rahu house must be 1-12"):
            is_ashtottari_applicable(0, 1)
        with pytest.raises(ValueError, match="Rahu house must be 1-12"):
            is_ashtottari_applicable(13, 1)

    def test_invalid_lagna_lord_house(self):
        """Invalid Lagna lord house raises ValueError."""
        with pytest.raises(ValueError, match="Lagna lord house must be 1-12"):
            is_ashtottari_applicable(1, 0)
        with pytest.raises(ValueError, match="Lagna lord house must be 1-12"):
            is_ashtottari_applicable(1, 13)


class TestGetStartingLord:
    """Test starting lord determination from nakshatra."""

    def test_ardra(self):
        """Ardra (6) -> Sun."""
        assert get_starting_lord(6) == "sun"

    def test_punarvasu(self):
        """Punarvasu (7) -> Sun."""
        assert get_starting_lord(7) == "sun"

    def test_pushya(self):
        """Pushya (8) -> Moon."""
        assert get_starting_lord(8) == "moon"

    def test_ashlesha(self):
        """Ashlesha (9) -> Moon."""
        assert get_starting_lord(9) == "moon"

    def test_magha(self):
        """Magha (10) -> Mars."""
        assert get_starting_lord(10) == "mars"

    def test_purva_phalguni(self):
        """Purva Phalguni (11) -> Mars."""
        assert get_starting_lord(11) == "mars"

    def test_uttara_phalguni(self):
        """Uttara Phalguni (12) -> Mercury."""
        assert get_starting_lord(12) == "mercury"

    def test_hasta(self):
        """Hasta (13) -> Mercury."""
        assert get_starting_lord(13) == "mercury"

    def test_chitra(self):
        """Chitra (14) -> Saturn."""
        assert get_starting_lord(14) == "saturn"

    def test_swati(self):
        """Swati (15) -> Saturn."""
        assert get_starting_lord(15) == "saturn"

    def test_vishakha(self):
        """Vishakha (16) -> Jupiter."""
        assert get_starting_lord(16) == "jupiter"

    def test_anuradha(self):
        """Anuradha (17) -> Jupiter."""
        assert get_starting_lord(17) == "jupiter"

    def test_jyeshtha(self):
        """Jyeshtha (18) -> Rahu."""
        assert get_starting_lord(18) == "rahu"

    def test_moola(self):
        """Moola (19) -> Rahu."""
        assert get_starting_lord(19) == "rahu"

    def test_purva_ashadha(self):
        """Purva Ashadha (20) -> Venus."""
        assert get_starting_lord(20) == "venus"

    def test_uttara_ashadha(self):
        """Uttara Ashadha (21) -> Venus."""
        assert get_starting_lord(21) == "venus"

    def test_purva_bhadrapada(self):
        """Purva Bhadrapada (25) should return a valid lord."""
        lord = get_starting_lord(25)
        assert lord in [name for name, _ in ASHTOTTARI_DATA]

    def test_invalid_nakshatra_zero(self):
        """Nakshatra 0 raises ValueError."""
        with pytest.raises(ValueError, match="Nakshatra number must be 1-27"):
            get_starting_lord(0)

    def test_invalid_nakshatra_28(self):
        """Nakshatra 28 raises ValueError."""
        with pytest.raises(ValueError, match="Nakshatra number must be 1-27"):
            get_starting_lord(28)

    def test_all_nakshatras_valid(self):
        """All 27 nakshatras return a valid lord."""
        valid_lords = {name for name, _ in ASHTOTTARI_DATA}
        for i in range(1, 28):
            lord = get_starting_lord(i)
            assert lord in valid_lords, f"Nakshatra {i} returned invalid lord: {lord}"


class TestCalculateAshtottariBalance:
    """Test balance calculations at birth."""

    def test_beginning_of_nakshatra(self):
        """At the very start of nakshatra, full dasha remains."""
        balance = calculate_ashtottari_balance(8, 0.0)  # Pushya -> Moon (15 years)
        assert balance["lord"] == "moon"
        assert balance["total_years"] == 15
        assert balance["elapsed_years"] == pytest.approx(0.0, abs=0.01)
        assert balance["remaining_years"] == pytest.approx(15.0, abs=0.01)

    def test_middle_of_nakshatra(self):
        """At halfway through nakshatra, half dasha remains."""
        half = 13.333333333 / 2
        balance = calculate_ashtottari_balance(8, half)  # Pushya -> Moon (15 years)
        assert balance["lord"] == "moon"
        assert balance["remaining_years"] == pytest.approx(7.5, abs=0.1)
        assert balance["elapsed_years"] == pytest.approx(7.5, abs=0.1)

    def test_near_end_of_nakshatra(self):
        """Near the end of nakshatra, very little remains."""
        balance = calculate_ashtottari_balance(8, 13.0)  # Near end
        assert balance["remaining_years"] < 1.0
        assert balance["elapsed_years"] > 14.0

    def test_standard_birth_data(self):
        """Test with standard birth data."""
        balance = calculate_ashtottari_balance(MOON_NAKSHATRA, DEGREE_IN_NAKSHATRA)
        assert balance["lord"] in [name for name, _ in ASHTOTTARI_DATA]
        assert balance["remaining_years"] > 0
        assert balance["remaining_years"] <= balance["total_years"]
        assert balance["elapsed_years"] + balance["remaining_years"] == pytest.approx(
            balance["total_years"], abs=0.01
        )

    def test_invalid_nakshatra(self):
        """Invalid nakshatra raises ValueError."""
        with pytest.raises(ValueError):
            calculate_ashtottari_balance(0, 5.0)

    def test_invalid_degree(self):
        """Negative degree raises ValueError."""
        with pytest.raises(ValueError):
            calculate_ashtottari_balance(8, -1.0)


class TestCalculateAshtottariSequence:
    """Test full sequence generation."""

    def test_sequence_length(self):
        """Sequence should cover 108 years worth of periods."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 6.0)
        # First period is partial, then full periods follow
        assert len(periods) >= 8

    def test_first_period_is_partial(self):
        """First period should be partial based on balance."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 6.0)  # Pushya, halfway-ish
        first = periods[0]
        assert first["lord"] == "moon"
        # Should be less than full 15 years
        assert first["years"] < 15.0

    def test_first_period_starts_at_birth(self):
        """First period should start at birth datetime."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 0.0)
        assert periods[0]["start_date"] == BIRTH_DT

    def test_periods_are_contiguous(self):
        """Each period should start where the previous one ended."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 6.0)
        for i in range(1, len(periods)):
            assert periods[i]["start_date"] == periods[i - 1]["end_date"]

    def test_total_duration_approximately_108_years(self):
        """Total duration should approximate 108 years."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 0.0, years=108)
        total_days = sum((p["end_date"] - p["start_date"]).days for p in periods)
        total_years = total_days / 365.25
        assert total_years == pytest.approx(108.0, abs=1.0)

    def test_lords_cycle_correctly(self):
        """Lords should follow the Ashtottari sequence."""
        # Start from beginning of nakshatra so first period is full
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 0.0)  # Moon
        # Second period should be Mars (next in sequence after Moon)
        assert periods[1]["lord"] == "mars"

    def test_custom_years(self):
        """Custom year span should work."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 0.0, years=50)
        total_days = sum((p["end_date"] - p["start_date"]).days for p in periods)
        total_years = total_days / 365.25
        assert total_years == pytest.approx(50.0, abs=1.0)


class TestGetCurrentAshtottari:
    """Test current Mahadasha + Antardasha lookup."""

    def test_at_birth(self):
        """At birth, should return the first Mahadasha."""
        result = get_current_ashtottari(
            BIRTH_DT, 8, 0.0, query_datetime=BIRTH_DT + timedelta(days=1)
        )
        assert result["mahadasha"]["lord"] == "moon"

    def test_returns_mahadasha_and_antardasha(self):
        """Result should contain both mahadasha and antardasha."""
        result = get_current_ashtottari(
            BIRTH_DT,
            8,
            6.0,
            query_datetime=datetime(2025, 1, 1),
        )
        assert "mahadasha" in result
        assert "antardasha" in result
        assert "remaining_days_maha" in result
        assert "remaining_days_antar" in result

    def test_remaining_days_positive(self):
        """Remaining days should be positive."""
        result = get_current_ashtottari(
            BIRTH_DT,
            8,
            6.0,
            query_datetime=datetime(2025, 1, 1),
        )
        assert result["remaining_days_maha"] > 0
        assert result["remaining_days_antar"] >= 0

    def test_mahadasha_contains_query(self):
        """Query datetime should fall within the returned mahadasha period."""
        query = datetime(2010, 6, 15)
        result = get_current_ashtottari(
            BIRTH_DT,
            8,
            6.0,
            query_datetime=query,
        )
        maha = result["mahadasha"]
        maha_start = (
            maha["start_date"].replace(tzinfo=None)
            if maha["start_date"].tzinfo
            else maha["start_date"]
        )
        maha_end = (
            maha["end_date"].replace(tzinfo=None) if maha["end_date"].tzinfo else maha["end_date"]
        )
        assert maha_start <= query < maha_end

    def test_with_timezone_aware_query(self):
        """Should handle timezone-aware query datetimes."""
        from datetime import UTC

        result = get_current_ashtottari(
            BIRTH_DT,
            8,
            6.0,
            query_datetime=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert result["mahadasha"]["lord"] is not None

    def test_default_query_datetime(self):
        """Without query datetime, should use current time."""
        result = get_current_ashtottari(BIRTH_DT, 8, 6.0)
        assert result["mahadasha"]["lord"] is not None


class TestGetAshtottariAntardasha:
    """Test antardasha breakdown within a mahadasha."""

    def test_eight_antardashas(self):
        """Should produce 8 antardashas."""
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=int(6 * 365.25))  # Sun dasha (6 years)
        ads = get_ashtottari_antardasha("sun", start, end)
        assert len(ads) == 8

    def test_first_antardasha_is_mahadasha_lord(self):
        """First antardasha should be the same as the mahadasha lord."""
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=int(15 * 365.25))
        ads = get_ashtottari_antardasha("moon", start, end)
        assert ads[0]["lord"] == "moon"

    def test_antardashas_start_at_mahadasha_start(self):
        """First antardasha should start at mahadasha start."""
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=int(6 * 365.25))
        ads = get_ashtottari_antardasha("sun", start, end)
        assert ads[0]["start_date"] == start

    def test_antardashas_are_contiguous(self):
        """Antardashas should be contiguous."""
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=int(17 * 365.25))
        ads = get_ashtottari_antardasha("mercury", start, end)
        for i in range(1, len(ads)):
            assert ads[i]["start_date"] == ads[i - 1]["end_date"]

    def test_antardashas_proportional(self):
        """Antardasha durations should be proportional to their lord's total years."""
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=int(10 * 365.25))
        ads = get_ashtottari_antardasha("saturn", start, end)

        # Saturn dasha: the antardasha for Sun (6 yrs) should be ~6/108 of total
        # and for Venus (21 yrs) should be ~21/108 of total
        sun_ad = next(ad for ad in ads if ad["lord"] == "sun")
        venus_ad = next(ad for ad in ads if ad["lord"] == "venus")

        sun_days = (sun_ad["end_date"] - sun_ad["start_date"]).days
        venus_days = (venus_ad["end_date"] - venus_ad["start_date"]).days

        # Venus should be 21/6 = 3.5x longer than Sun
        ratio = venus_days / sun_days if sun_days > 0 else 0
        assert ratio == pytest.approx(21 / 6, abs=0.3)

    def test_invalid_lord_raises_error(self):
        """Invalid lord should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid Ashtottari lord"):
            get_ashtottari_antardasha("ketu", datetime(2020, 1, 1), datetime(2025, 1, 1))

    def test_sequence_follows_ashtottari_order(self):
        """Antardashas should follow the Ashtottari sequence from the mahadasha lord."""
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=int(8 * 365.25))
        ads = get_ashtottari_antardasha("mars", start, end)

        # Mars is at index 2, so sequence should be:
        # mars(2), mercury(3), saturn(4), jupiter(5), rahu(6), venus(7), sun(0), moon(1)
        expected = ["mars", "mercury", "saturn", "jupiter", "rahu", "venus", "sun", "moon"]
        actual = [ad["lord"] for ad in ads]
        assert actual == expected


class TestAshtottariIntegration:
    """Integration tests using standard birth data."""

    def test_full_lifecycle(self):
        """Test complete lifecycle: balance -> sequence -> current."""
        balance = calculate_ashtottari_balance(MOON_NAKSHATRA, DEGREE_IN_NAKSHATRA)
        assert balance["lord"] is not None

        periods = calculate_ashtottari_sequence(BIRTH_DT, MOON_NAKSHATRA, DEGREE_IN_NAKSHATRA)
        assert len(periods) > 0

        result = get_current_ashtottari(
            BIRTH_DT,
            MOON_NAKSHATRA,
            DEGREE_IN_NAKSHATRA,
            query_datetime=datetime(2025, 1, 1),
        )
        assert result["mahadasha"]["lord"] is not None
        assert result["antardasha"]["lord"] is not None

    def test_different_nakshatras_give_different_starts(self):
        """Different nakshatras should give different starting lords."""
        lord_6 = get_starting_lord(6)  # Ardra -> Sun
        lord_8 = get_starting_lord(8)  # Pushya -> Moon
        lord_10 = get_starting_lord(10)  # Magha -> Mars
        assert lord_6 != lord_8
        assert lord_8 != lord_10

    def test_sequence_covers_entire_life(self):
        """Sequence should span from birth to 108 years later."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 0.0, years=108)
        last_end = periods[-1]["end_date"]
        span_days = (last_end - BIRTH_DT).days
        span_years = span_days / 365.25
        assert span_years == pytest.approx(108.0, abs=1.0)

    def test_no_gaps_in_sequence(self):
        """There should be no gaps between periods."""
        periods = calculate_ashtottari_sequence(BIRTH_DT, 8, 0.0)
        for i in range(1, len(periods)):
            gap = (periods[i]["start_date"] - periods[i - 1]["end_date"]).total_seconds()
            assert abs(gap) < 1, f"Gap between period {i - 1} and {i}: {gap} seconds"
