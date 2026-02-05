"""Unit tests for Narayana Dasha calculations."""

from datetime import UTC, datetime

from packages.context.src.narayana_dasha import (
    RASHI_LIST,
    calculate_narayana_sequence,
    calculate_period_duration,
    get_current_narayana_dasha,
    get_narayana_antardasha,
    get_progression_direction,
    get_sign_index,
    is_odd_sign,
)
from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import (
    BirthChart,
    BirthData,
    HouseCusps,
    NarayanaDashaPeriod,
    PlanetPosition,
)


def _make_chart(lagna_rashi=Rashi.ARIES, planet_positions=None):
    """Build a minimal BirthChart for testing.

    Args:
        lagna_rashi: Ascendant sign
        planet_positions: Optional dict of planet positions

    Returns:
        BirthChart object
    """
    default_planets = {
        Planet.SUN: PlanetPosition(
            planet=Planet.SUN,
            longitude=15.0,
            rashi=Rashi.ARIES,
            rashi_degree=15.0,
            nakshatra="ashwini",
            nakshatra_pada=2,
            nakshatra_lord=Planet.KETU,
            house=1,
        ),
        Planet.MOON: PlanetPosition(
            planet=Planet.MOON,
            longitude=45.0,
            rashi=Rashi.TAURUS,
            rashi_degree=15.0,
            nakshatra="rohini",
            nakshatra_pada=2,
            nakshatra_lord=Planet.MOON,
            house=2,
        ),
        Planet.MARS: PlanetPosition(
            planet=Planet.MARS,
            longitude=75.0,
            rashi=Rashi.GEMINI,
            rashi_degree=15.0,
            nakshatra="mrigashira",
            nakshatra_pada=2,
            nakshatra_lord=Planet.MARS,
            house=3,
        ),
        Planet.MERCURY: PlanetPosition(
            planet=Planet.MERCURY,
            longitude=105.0,
            rashi=Rashi.CANCER,
            rashi_degree=15.0,
            nakshatra="pushya",
            nakshatra_pada=2,
            nakshatra_lord=Planet.SATURN,
            house=4,
        ),
        Planet.JUPITER: PlanetPosition(
            planet=Planet.JUPITER,
            longitude=135.0,
            rashi=Rashi.LEO,
            rashi_degree=15.0,
            nakshatra="magha",
            nakshatra_pada=2,
            nakshatra_lord=Planet.KETU,
            house=5,
        ),
        Planet.VENUS: PlanetPosition(
            planet=Planet.VENUS,
            longitude=165.0,
            rashi=Rashi.VIRGO,
            rashi_degree=15.0,
            nakshatra="hasta",
            nakshatra_pada=2,
            nakshatra_lord=Planet.MOON,
            house=6,
        ),
        Planet.SATURN: PlanetPosition(
            planet=Planet.SATURN,
            longitude=195.0,
            rashi=Rashi.LIBRA,
            rashi_degree=15.0,
            nakshatra="swati",
            nakshatra_pada=2,
            nakshatra_lord=Planet.RAHU,
            house=7,
        ),
        Planet.RAHU: PlanetPosition(
            planet=Planet.RAHU,
            longitude=225.0,
            rashi=Rashi.SCORPIO,
            rashi_degree=15.0,
            nakshatra="jyeshtha",
            nakshatra_pada=2,
            nakshatra_lord=Planet.MERCURY,
            house=8,
        ),
        Planet.KETU: PlanetPosition(
            planet=Planet.KETU,
            longitude=45.0,
            rashi=Rashi.TAURUS,
            rashi_degree=15.0,
            nakshatra="rohini",
            nakshatra_pada=2,
            nakshatra_lord=Planet.MOON,
            house=2,
        ),
    }

    planets = planet_positions or default_planets

    return BirthChart(
        user_id="test",
        birth_data=BirthData(
            datetime_utc=datetime(1992, 12, 3, tzinfo=UTC),
            latitude=16.7,
            longitude=81.3,
            timezone="Asia/Kolkata",
        ),
        planets=planets,
        houses=HouseCusps(
            ascendant=get_sign_index(lagna_rashi) * 30.0,
            mc=270.0,
            cusps=[i * 30 for i in range(12)],
        ),
        lagna_rashi=lagna_rashi,
        moon_rashi=Rashi.TAURUS,
        moon_nakshatra="rohini",
        ayanamsa=23.45,
        calculated_at=datetime.now(UTC),
    )


class TestOddEvenSign:
    """Test odd/even sign classification."""

    def test_aries_is_odd(self):
        """Test that Aries (index 0) is odd."""
        assert is_odd_sign(Rashi.ARIES) is True

    def test_taurus_is_even(self):
        """Test that Taurus (index 1) is even."""
        assert is_odd_sign(Rashi.TAURUS) is False

    def test_gemini_is_odd(self):
        """Test that Gemini (index 2) is odd."""
        assert is_odd_sign(Rashi.GEMINI) is True

    def test_cancer_is_even(self):
        """Test that Cancer (index 3) is even."""
        assert is_odd_sign(Rashi.CANCER) is False

    def test_all_odd_signs(self):
        """Test all odd signs."""
        odd_signs = [
            Rashi.ARIES,
            Rashi.GEMINI,
            Rashi.LEO,
            Rashi.LIBRA,
            Rashi.SAGITTARIUS,
            Rashi.AQUARIUS,
        ]
        for sign in odd_signs:
            assert is_odd_sign(sign) is True

    def test_all_even_signs(self):
        """Test all even signs."""
        even_signs = [
            Rashi.TAURUS,
            Rashi.CANCER,
            Rashi.VIRGO,
            Rashi.SCORPIO,
            Rashi.CAPRICORN,
            Rashi.PISCES,
        ]
        for sign in even_signs:
            assert is_odd_sign(sign) is False


class TestSignIndex:
    """Test sign index retrieval."""

    def test_aries_index(self):
        """Test Aries is index 0."""
        assert get_sign_index(Rashi.ARIES) == 0

    def test_taurus_index(self):
        """Test Taurus is index 1."""
        assert get_sign_index(Rashi.TAURUS) == 1

    def test_pisces_index(self):
        """Test Pisces is index 11."""
        assert get_sign_index(Rashi.PISCES) == 11

    def test_all_signs_have_unique_index(self):
        """Test all signs have unique indices 0-11."""
        indices = [get_sign_index(rashi) for rashi in RASHI_LIST]
        assert sorted(indices) == list(range(12))


class TestProgressionDirection:
    """Test progression direction based on lagna."""

    def test_aries_lagna_forward(self):
        """Test Aries lagna gives forward progression."""
        assert get_progression_direction(Rashi.ARIES) is True

    def test_taurus_lagna_reverse(self):
        """Test Taurus lagna gives reverse progression."""
        assert get_progression_direction(Rashi.TAURUS) is False

    def test_leo_lagna_forward(self):
        """Test Leo lagna gives forward progression."""
        assert get_progression_direction(Rashi.LEO) is True

    def test_scorpio_lagna_reverse(self):
        """Test Scorpio lagna gives reverse progression."""
        assert get_progression_direction(Rashi.SCORPIO) is False


class TestPeriodDuration:
    """Test period duration calculation."""

    def test_lord_in_own_sign(self):
        """Test that lord in own sign gives 12 years."""
        # Mars in Aries
        planets = {
            Planet.MARS: PlanetPosition(
                planet=Planet.MARS,
                longitude=15.0,
                rashi=Rashi.ARIES,
                rashi_degree=15.0,
                nakshatra="ashwini",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=1,
            ),
            Planet.SUN: PlanetPosition(
                planet=Planet.SUN,
                longitude=45.0,
                rashi=Rashi.TAURUS,
                rashi_degree=15.0,
                nakshatra="rohini",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MOON,
                house=2,
            ),
            Planet.MOON: PlanetPosition(
                planet=Planet.MOON,
                longitude=75.0,
                rashi=Rashi.GEMINI,
                rashi_degree=15.0,
                nakshatra="mrigashira",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MARS,
                house=3,
            ),
            Planet.MERCURY: PlanetPosition(
                planet=Planet.MERCURY,
                longitude=105.0,
                rashi=Rashi.CANCER,
                rashi_degree=15.0,
                nakshatra="pushya",
                nakshatra_pada=2,
                nakshatra_lord=Planet.SATURN,
                house=4,
            ),
            Planet.JUPITER: PlanetPosition(
                planet=Planet.JUPITER,
                longitude=135.0,
                rashi=Rashi.LEO,
                rashi_degree=15.0,
                nakshatra="magha",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=5,
            ),
            Planet.VENUS: PlanetPosition(
                planet=Planet.VENUS,
                longitude=165.0,
                rashi=Rashi.VIRGO,
                rashi_degree=15.0,
                nakshatra="hasta",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MOON,
                house=6,
            ),
            Planet.SATURN: PlanetPosition(
                planet=Planet.SATURN,
                longitude=195.0,
                rashi=Rashi.LIBRA,
                rashi_degree=15.0,
                nakshatra="swati",
                nakshatra_pada=2,
                nakshatra_lord=Planet.RAHU,
                house=7,
            ),
            Planet.RAHU: PlanetPosition(
                planet=Planet.RAHU,
                longitude=225.0,
                rashi=Rashi.SCORPIO,
                rashi_degree=15.0,
                nakshatra="jyeshtha",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MERCURY,
                house=8,
            ),
            Planet.KETU: PlanetPosition(
                planet=Planet.KETU,
                longitude=255.0,
                rashi=Rashi.SAGITTARIUS,
                rashi_degree=15.0,
                nakshatra="mula",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=9,
            ),
        }
        chart = _make_chart(lagna_rashi=Rashi.ARIES, planet_positions=planets)
        duration = calculate_period_duration(Rashi.ARIES, chart)
        assert duration == 12

    def test_duration_range(self):
        """Test that duration is always 1-12."""
        chart = _make_chart()
        for sign in RASHI_LIST:
            duration = calculate_period_duration(sign, chart)
            assert 1 <= duration <= 12

    def test_odd_sign_duration(self):
        """Test duration calculation for odd sign."""
        # Aries (odd), Mars lord in Gemini (2 signs forward)
        # Count from Aries to Gemini = 3 (Aries, Taurus, Gemini)
        # Duration = 3
        planets = {
            Planet.MARS: PlanetPosition(
                planet=Planet.MARS,
                longitude=75.0,
                rashi=Rashi.GEMINI,
                rashi_degree=15.0,
                nakshatra="mrigashira",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MARS,
                house=3,
            ),
            Planet.SUN: PlanetPosition(
                planet=Planet.SUN,
                longitude=15.0,
                rashi=Rashi.ARIES,
                rashi_degree=15.0,
                nakshatra="ashwini",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=1,
            ),
            Planet.MOON: PlanetPosition(
                planet=Planet.MOON,
                longitude=45.0,
                rashi=Rashi.TAURUS,
                rashi_degree=15.0,
                nakshatra="rohini",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MOON,
                house=2,
            ),
            Planet.MERCURY: PlanetPosition(
                planet=Planet.MERCURY,
                longitude=105.0,
                rashi=Rashi.CANCER,
                rashi_degree=15.0,
                nakshatra="pushya",
                nakshatra_pada=2,
                nakshatra_lord=Planet.SATURN,
                house=4,
            ),
            Planet.JUPITER: PlanetPosition(
                planet=Planet.JUPITER,
                longitude=135.0,
                rashi=Rashi.LEO,
                rashi_degree=15.0,
                nakshatra="magha",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=5,
            ),
            Planet.VENUS: PlanetPosition(
                planet=Planet.VENUS,
                longitude=165.0,
                rashi=Rashi.VIRGO,
                rashi_degree=15.0,
                nakshatra="hasta",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MOON,
                house=6,
            ),
            Planet.SATURN: PlanetPosition(
                planet=Planet.SATURN,
                longitude=195.0,
                rashi=Rashi.LIBRA,
                rashi_degree=15.0,
                nakshatra="swati",
                nakshatra_pada=2,
                nakshatra_lord=Planet.RAHU,
                house=7,
            ),
            Planet.RAHU: PlanetPosition(
                planet=Planet.RAHU,
                longitude=225.0,
                rashi=Rashi.SCORPIO,
                rashi_degree=15.0,
                nakshatra="jyeshtha",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MERCURY,
                house=8,
            ),
            Planet.KETU: PlanetPosition(
                planet=Planet.KETU,
                longitude=255.0,
                rashi=Rashi.SAGITTARIUS,
                rashi_degree=15.0,
                nakshatra="mula",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=9,
            ),
        }
        chart = _make_chart(lagna_rashi=Rashi.ARIES, planet_positions=planets)
        duration = calculate_period_duration(Rashi.ARIES, chart)
        assert duration == 3

    def test_even_sign_duration(self):
        """Test duration calculation for even sign."""
        # Taurus (even), Venus lord in Virgo (4 signs forward)
        # Count from Taurus to Virgo = 5
        # Duration = 12 - 5 = 7
        planets = {
            Planet.VENUS: PlanetPosition(
                planet=Planet.VENUS,
                longitude=165.0,
                rashi=Rashi.VIRGO,
                rashi_degree=15.0,
                nakshatra="hasta",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MOON,
                house=6,
            ),
            Planet.SUN: PlanetPosition(
                planet=Planet.SUN,
                longitude=15.0,
                rashi=Rashi.ARIES,
                rashi_degree=15.0,
                nakshatra="ashwini",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=1,
            ),
            Planet.MOON: PlanetPosition(
                planet=Planet.MOON,
                longitude=45.0,
                rashi=Rashi.TAURUS,
                rashi_degree=15.0,
                nakshatra="rohini",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MOON,
                house=2,
            ),
            Planet.MARS: PlanetPosition(
                planet=Planet.MARS,
                longitude=75.0,
                rashi=Rashi.GEMINI,
                rashi_degree=15.0,
                nakshatra="mrigashira",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MARS,
                house=3,
            ),
            Planet.MERCURY: PlanetPosition(
                planet=Planet.MERCURY,
                longitude=105.0,
                rashi=Rashi.CANCER,
                rashi_degree=15.0,
                nakshatra="pushya",
                nakshatra_pada=2,
                nakshatra_lord=Planet.SATURN,
                house=4,
            ),
            Planet.JUPITER: PlanetPosition(
                planet=Planet.JUPITER,
                longitude=135.0,
                rashi=Rashi.LEO,
                rashi_degree=15.0,
                nakshatra="magha",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=5,
            ),
            Planet.SATURN: PlanetPosition(
                planet=Planet.SATURN,
                longitude=195.0,
                rashi=Rashi.LIBRA,
                rashi_degree=15.0,
                nakshatra="swati",
                nakshatra_pada=2,
                nakshatra_lord=Planet.RAHU,
                house=7,
            ),
            Planet.RAHU: PlanetPosition(
                planet=Planet.RAHU,
                longitude=225.0,
                rashi=Rashi.SCORPIO,
                rashi_degree=15.0,
                nakshatra="jyeshtha",
                nakshatra_pada=2,
                nakshatra_lord=Planet.MERCURY,
                house=8,
            ),
            Planet.KETU: PlanetPosition(
                planet=Planet.KETU,
                longitude=255.0,
                rashi=Rashi.SAGITTARIUS,
                rashi_degree=15.0,
                nakshatra="mula",
                nakshatra_pada=2,
                nakshatra_lord=Planet.KETU,
                house=9,
            ),
        }
        chart = _make_chart(lagna_rashi=Rashi.TAURUS, planet_positions=planets)
        duration = calculate_period_duration(Rashi.TAURUS, chart)
        assert duration == 7


class TestNarayanaSequence:
    """Test Narayana dasha sequence generation."""

    def test_sequence_count_one_cycle(self):
        """Test that one cycle generates 12 periods."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)
        assert len(periods) == 12

    def test_sequence_count_two_cycles(self):
        """Test that two cycles generate 24 periods."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=2)
        assert len(periods) == 24

    def test_sequence_starts_at_birth(self):
        """Test that sequence starts at birth datetime."""
        birth_dt = datetime(1992, 12, 3, 3, 0, 0, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)
        assert periods[0].start_date == birth_dt

    def test_sequence_starts_with_lagna(self):
        """Test that sequence starts with lagna sign."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.LEO)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)
        assert periods[0].rashi == Rashi.LEO

    def test_sequence_no_overlaps(self):
        """Test that periods don't overlap."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)
        for i in range(len(periods) - 1):
            assert periods[i].end_date == periods[i + 1].start_date

    def test_forward_progression_for_odd_lagna(self):
        """Test forward progression for odd sign lagna."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)

        # Aries is odd, should progress forward: Aries -> Taurus -> Gemini...
        assert periods[0].rashi == Rashi.ARIES
        assert periods[1].rashi == Rashi.TAURUS
        assert periods[2].rashi == Rashi.GEMINI
        assert periods[0].is_forward is True

    def test_reverse_progression_for_even_lagna(self):
        """Test reverse progression for even sign lagna."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.TAURUS)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)

        # Taurus is even, should progress reverse: Taurus -> Aries -> Pisces...
        assert periods[0].rashi == Rashi.TAURUS
        assert periods[1].rashi == Rashi.ARIES
        assert periods[2].rashi == Rashi.PISCES
        assert periods[0].is_forward is False

    def test_all_signs_covered_in_cycle(self):
        """Test that all 12 signs are covered in one cycle."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)

        signs_covered = [period.rashi for period in periods]
        assert len(set(signs_covered)) == 12
        assert set(signs_covered) == set(RASHI_LIST)


class TestCurrentNarayanaDasha:
    """Test current Narayana dasha lookup."""

    def test_current_in_first_period(self):
        """Test query date in first period."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        # Query 1 year after birth
        query_dt = datetime(1993, 12, 3, tzinfo=UTC)

        current = get_current_narayana_dasha(birth_dt, chart, query_dt)
        # Should still be in first period
        assert current["rashi"] == Rashi.ARIES
        assert current["remaining_days"] > 0

    def test_current_in_later_period(self):
        """Test query date in a later period."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        # Query 30 years after birth
        query_dt = datetime(2022, 12, 3, tzinfo=UTC)

        current = get_current_narayana_dasha(birth_dt, chart, query_dt)
        assert current["rashi"] in RASHI_LIST
        assert current["remaining_days"] >= 0

    def test_current_defaults_to_now(self):
        """Test that query_dt defaults to now."""
        birth_dt = datetime(1992, 12, 3, tzinfo=UTC)
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        current = get_current_narayana_dasha(birth_dt, chart)
        assert "rashi" in current
        assert "remaining_days" in current


class TestNarayanaAntardasha:
    """Test Narayana antardasha subdivision."""

    def test_antardasha_count(self):
        """Test that 12 antardashas are generated."""
        maha = NarayanaDashaPeriod(
            rashi=Rashi.ARIES,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2032, 1, 1, tzinfo=UTC),
            duration_years=12,
            is_forward=True,
        )
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        antardashas = get_narayana_antardasha(maha, chart)
        assert len(antardashas) == 12

    def test_antardasha_starts_with_maha_sign(self):
        """Test that antardasha sequence starts with maha sign."""
        maha = NarayanaDashaPeriod(
            rashi=Rashi.LEO,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2032, 1, 1, tzinfo=UTC),
            duration_years=12,
            is_forward=True,
        )
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        antardashas = get_narayana_antardasha(maha, chart)
        assert antardashas[0]["rashi"] == Rashi.LEO

    def test_antardasha_covers_maha_period(self):
        """Test that antardashas cover the entire maha period."""
        maha = NarayanaDashaPeriod(
            rashi=Rashi.ARIES,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2032, 1, 1, tzinfo=UTC),
            duration_years=12,
            is_forward=True,
        )
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        antardashas = get_narayana_antardasha(maha, chart)

        assert antardashas[0]["start_date"] == maha.start_date
        assert antardashas[-1]["end_date"] <= maha.end_date

    def test_antardasha_no_overlaps(self):
        """Test that antardashas don't overlap."""
        maha = NarayanaDashaPeriod(
            rashi=Rashi.ARIES,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2032, 1, 1, tzinfo=UTC),
            duration_years=12,
            is_forward=True,
        )
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        antardashas = get_narayana_antardasha(maha, chart)

        for i in range(len(antardashas) - 1):
            assert antardashas[i]["end_date"] == antardashas[i + 1]["start_date"]

    def test_antardasha_forward_progression(self):
        """Test antardasha follows forward progression."""
        maha = NarayanaDashaPeriod(
            rashi=Rashi.ARIES,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2032, 1, 1, tzinfo=UTC),
            duration_years=12,
            is_forward=True,
        )
        chart = _make_chart(lagna_rashi=Rashi.ARIES)
        antardashas = get_narayana_antardasha(maha, chart)

        # Forward: Aries -> Taurus -> Gemini
        assert antardashas[0]["rashi"] == Rashi.ARIES
        assert antardashas[1]["rashi"] == Rashi.TAURUS
        assert antardashas[2]["rashi"] == Rashi.GEMINI

    def test_antardasha_reverse_progression(self):
        """Test antardasha follows reverse progression."""
        maha = NarayanaDashaPeriod(
            rashi=Rashi.TAURUS,
            start_date=datetime(2020, 1, 1, tzinfo=UTC),
            end_date=datetime(2032, 1, 1, tzinfo=UTC),
            duration_years=12,
            is_forward=False,
        )
        chart = _make_chart(lagna_rashi=Rashi.TAURUS)
        antardashas = get_narayana_antardasha(maha, chart)

        # Reverse: Taurus -> Aries -> Pisces
        assert antardashas[0]["rashi"] == Rashi.TAURUS
        assert antardashas[1]["rashi"] == Rashi.ARIES
        assert antardashas[2]["rashi"] == Rashi.PISCES
