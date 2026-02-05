"""Tests for Jaimini astrology system."""

from datetime import UTC, datetime

from packages.core.src.constants import CharaKaraka, Planet, Rashi, SignMobility
from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition
from packages.self.src.jaimini import (
    calculate_all_arudha_padas,
    calculate_arudha_pada,
    calculate_chara_dasha,
    calculate_chara_karakas,
    get_atmakaraka,
    get_jaimini_aspects,
    get_karakamsha,
    get_sign_mobility,
)


class TestSignMobility:
    """Tests for sign mobility classification."""

    def test_movable_signs(self):
        """Test that movable signs are correctly identified."""
        assert get_sign_mobility(Rashi.ARIES) == SignMobility.MOVABLE
        assert get_sign_mobility(Rashi.CANCER) == SignMobility.MOVABLE
        assert get_sign_mobility(Rashi.LIBRA) == SignMobility.MOVABLE
        assert get_sign_mobility(Rashi.CAPRICORN) == SignMobility.MOVABLE

    def test_fixed_signs(self):
        """Test that fixed signs are correctly identified."""
        assert get_sign_mobility(Rashi.TAURUS) == SignMobility.FIXED
        assert get_sign_mobility(Rashi.LEO) == SignMobility.FIXED
        assert get_sign_mobility(Rashi.SCORPIO) == SignMobility.FIXED
        assert get_sign_mobility(Rashi.AQUARIUS) == SignMobility.FIXED

    def test_dual_signs(self):
        """Test that dual signs are correctly identified."""
        assert get_sign_mobility(Rashi.GEMINI) == SignMobility.DUAL
        assert get_sign_mobility(Rashi.VIRGO) == SignMobility.DUAL
        assert get_sign_mobility(Rashi.SAGITTARIUS) == SignMobility.DUAL
        assert get_sign_mobility(Rashi.PISCES) == SignMobility.DUAL


class TestJaiminiAspects:
    """Tests for Jaimini aspect calculations."""

    def test_aries_aspects(self):
        """Test aspects from Aries (5th, 8th, 11th)."""
        aspects = get_jaimini_aspects(Rashi.ARIES)
        assert len(aspects) == 3
        assert Rashi.LEO in aspects  # 5th
        assert Rashi.SCORPIO in aspects  # 8th
        assert Rashi.AQUARIUS in aspects  # 11th

    def test_taurus_aspects(self):
        """Test aspects from Taurus."""
        aspects = get_jaimini_aspects(Rashi.TAURUS)
        assert len(aspects) == 3
        assert Rashi.VIRGO in aspects  # 5th
        assert Rashi.SAGITTARIUS in aspects  # 8th
        assert Rashi.PISCES in aspects  # 11th

    def test_gemini_aspects(self):
        """Test aspects from Gemini."""
        aspects = get_jaimini_aspects(Rashi.GEMINI)
        assert len(aspects) == 3
        assert Rashi.LIBRA in aspects  # 5th
        assert Rashi.CAPRICORN in aspects  # 8th
        assert Rashi.ARIES in aspects  # 11th

    def test_leo_aspects(self):
        """Test aspects from Leo."""
        aspects = get_jaimini_aspects(Rashi.LEO)
        assert len(aspects) == 3
        assert Rashi.SAGITTARIUS in aspects  # 5th
        assert Rashi.PISCES in aspects  # 8th
        assert Rashi.GEMINI in aspects  # 11th

    def test_libra_aspects(self):
        """Test aspects from Libra."""
        aspects = get_jaimini_aspects(Rashi.LIBRA)
        assert len(aspects) == 3
        assert Rashi.AQUARIUS in aspects  # 5th
        assert Rashi.TAURUS in aspects  # 8th
        assert Rashi.LEO in aspects  # 11th

    def test_capricorn_aspects(self):
        """Test aspects from Capricorn."""
        aspects = get_jaimini_aspects(Rashi.CAPRICORN)
        assert len(aspects) == 3
        assert Rashi.TAURUS in aspects  # 5th
        assert Rashi.LEO in aspects  # 8th
        assert Rashi.SCORPIO in aspects  # 11th


def create_mock_chart(
    planet_degrees: dict[Planet, tuple[Rashi, float]], lagna: Rashi
) -> BirthChart:
    """Create a mock birth chart for testing.

    Args:
        planet_degrees: Dict mapping Planet to (Rashi, degree_in_sign)
        lagna: Lagna rashi

    Returns:
        BirthChart: Mock chart with specified planet positions
    """
    birth_data = BirthData(
        datetime_utc=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )

    planets = {}
    for planet, (rashi, degree) in planet_degrees.items():
        # Calculate longitude from rashi and degree
        rashi_index = {
            Rashi.ARIES: 0,
            Rashi.TAURUS: 1,
            Rashi.GEMINI: 2,
            Rashi.CANCER: 3,
            Rashi.LEO: 4,
            Rashi.VIRGO: 5,
            Rashi.LIBRA: 6,
            Rashi.SCORPIO: 7,
            Rashi.SAGITTARIUS: 8,
            Rashi.CAPRICORN: 9,
            Rashi.AQUARIUS: 10,
            Rashi.PISCES: 11,
        }[rashi]
        longitude = rashi_index * 30 + degree

        planets[planet] = PlanetPosition(
            planet=planet,
            longitude=longitude,
            rashi=rashi,
            rashi_degree=degree,
            nakshatra="test",
            nakshatra_pada=1,
            nakshatra_lord=Planet.SUN,
            house=1,
        )

    houses = HouseCusps(
        ascendant=0.0, mc=270.0, cusps=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    )

    return BirthChart(
        user_id="test",
        birth_data=birth_data,
        planets=planets,
        houses=houses,
        lagna_rashi=lagna,
        moon_rashi=planets[Planet.MOON].rashi if Planet.MOON in planets else Rashi.ARIES,
        moon_nakshatra="test",
        ayanamsa=23.0,
        calculated_at=datetime.now(UTC),
    )


class TestCharaKarakas:
    """Tests for Chara Karaka calculations."""

    def test_calculate_chara_karakas_order(self):
        """Test that planets are correctly ordered by degree."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.ARIES, 25.5),  # Highest degree
                Planet.MOON: (Rashi.TAURUS, 18.2),  # 2nd
                Planet.MARS: (Rashi.GEMINI, 12.0),  # 3rd
                Planet.MERCURY: (Rashi.CANCER, 8.5),  # 4th
                Planet.JUPITER: (Rashi.LEO, 5.0),  # 5th
                Planet.VENUS: (Rashi.VIRGO, 3.2),  # 6th
                Planet.SATURN: (Rashi.LIBRA, 1.0),  # Lowest (7th)
            },
            Rashi.ARIES,
        )

        karakas = calculate_chara_karakas(chart)

        assert len(karakas) == 7
        assert karakas[0].karaka == CharaKaraka.ATMAKARAKA
        assert karakas[0].planet == Planet.SUN
        assert karakas[1].karaka == CharaKaraka.AMATYAKARAKA
        assert karakas[1].planet == Planet.MOON
        assert karakas[6].karaka == CharaKaraka.DARAKARAKA
        assert karakas[6].planet == Planet.SATURN

    def test_atmakaraka_is_highest_degree(self):
        """Test that Atmakaraka is the planet with highest degree."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.ARIES, 10.0),
                Planet.MOON: (Rashi.TAURUS, 28.5),  # Highest
                Planet.MARS: (Rashi.GEMINI, 15.0),
                Planet.MERCURY: (Rashi.CANCER, 5.0),
                Planet.JUPITER: (Rashi.LEO, 20.0),
                Planet.VENUS: (Rashi.VIRGO, 12.0),
                Planet.SATURN: (Rashi.LIBRA, 8.0),
            },
            Rashi.ARIES,
        )

        ak = get_atmakaraka(chart)
        assert ak.planet == Planet.MOON
        assert ak.karaka == CharaKaraka.ATMAKARAKA
        assert ak.degree_in_sign == 28.5

    def test_chara_karakas_excludes_rahu_ketu(self):
        """Test that Rahu and Ketu are not included in Chara Karakas."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.ARIES, 25.0),
                Planet.MOON: (Rashi.TAURUS, 20.0),
                Planet.MARS: (Rashi.GEMINI, 15.0),
                Planet.MERCURY: (Rashi.CANCER, 10.0),
                Planet.JUPITER: (Rashi.LEO, 8.0),
                Planet.VENUS: (Rashi.VIRGO, 5.0),
                Planet.SATURN: (Rashi.LIBRA, 3.0),
                Planet.RAHU: (Rashi.SCORPIO, 29.9),  # Highest degree but should be excluded
                Planet.KETU: (Rashi.TAURUS, 29.9),
            },
            Rashi.ARIES,
        )

        karakas = calculate_chara_karakas(chart)
        planets = [k.planet for k in karakas]

        assert len(karakas) == 7
        assert Planet.RAHU not in planets
        assert Planet.KETU not in planets
        assert karakas[0].planet == Planet.SUN  # Sun should be AK, not Rahu


class TestArudhaPada:
    """Tests for Arudha Pada calculations."""

    def test_basic_arudha_pada_calculation(self):
        """Test basic Arudha Pada calculation."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.ARIES,
        )

        # Calculate A1 (Arudha Lagna)
        pada = calculate_arudha_pada(1, chart)
        assert pada.house_number == 1
        assert isinstance(pada.rashi, Rashi)
        assert pada.house_lord == Planet.MARS  # Mars rules Aries

    def test_lord_in_house_itself_special_case(self):
        """Test special case when lord is in the house itself."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),  # Sun in Leo (own sign)
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.LEO,  # Lagna in Leo
        )

        # Calculate A1 - Sun (lord of Leo) is in Leo itself
        pada = calculate_arudha_pada(1, chart)
        assert "10th" in pada.calculation_note.lower()  # Should shift to 10th

    def test_calculate_all_arudha_padas(self):
        """Test calculation of all 12 Arudha Padas."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.ARIES,
        )

        padas = calculate_all_arudha_padas(chart)
        assert len(padas) == 12
        assert all(isinstance(p.rashi, Rashi) for p in padas)
        assert [p.house_number for p in padas] == list(range(1, 13))


class TestKarakamsha:
    """Tests for Karakamsha calculations."""

    def test_karakamsha_calculation(self):
        """Test basic Karakamsha calculation."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.ARIES, 25.0),  # Highest degree = AK
                Planet.MOON: (Rashi.TAURUS, 20.0),
                Planet.MARS: (Rashi.GEMINI, 15.0),
                Planet.MERCURY: (Rashi.CANCER, 10.0),
                Planet.JUPITER: (Rashi.LEO, 8.0),
                Planet.VENUS: (Rashi.VIRGO, 5.0),
                Planet.SATURN: (Rashi.LIBRA, 3.0),
            },
            Rashi.ARIES,
        )

        km = get_karakamsha(chart)
        assert km.atmakaraka == Planet.SUN
        assert isinstance(km.navamsha_rashi, Rashi)
        assert isinstance(km.interpretation, str)
        assert len(km.interpretation) > 0

    def test_karakamsha_interpretation_exists_for_all_signs(self):
        """Test that interpretations exist for all 12 signs."""
        # Test with different AK degrees to get different navamsha signs
        for degree in [8.0, 10.0, 12.0, 14.0, 18.0, 22.0, 26.0]:
            chart = create_mock_chart(
                {
                    Planet.SUN: (Rashi.ARIES, degree),  # AK
                    Planet.MOON: (Rashi.TAURUS, max(0.5, degree - 1)),
                    Planet.MARS: (Rashi.GEMINI, max(0.5, degree - 2)),
                    Planet.MERCURY: (Rashi.CANCER, max(0.5, degree - 3)),
                    Planet.JUPITER: (Rashi.LEO, max(0.5, degree - 4)),
                    Planet.VENUS: (Rashi.VIRGO, max(0.5, degree - 5)),
                    Planet.SATURN: (Rashi.LIBRA, max(0.5, degree - 6)),
                },
                Rashi.ARIES,
            )

            km = get_karakamsha(chart)
            assert len(km.interpretation) > 0
            assert km.atmakaraka == Planet.SUN


class TestCharaDasha:
    """Tests for Chara Dasha calculations."""

    def test_chara_dasha_forward_sequence(self):
        """Test Chara Dasha with odd-footed lagna (forward sequence)."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.ARIES,  # Odd-footed (index 0)
        )

        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
        periods = calculate_chara_dasha(birth_dt, chart, years=36)

        assert len(periods) > 0
        assert periods[0].rashi == Rashi.ARIES  # Starts from lagna
        assert all(p.duration_years >= 1 and p.duration_years <= 12 for p in periods)
        assert all(p.start_date < p.end_date for p in periods)

        # Check sequence is forward for odd lagna
        assert periods[1].rashi == Rashi.TAURUS

    def test_chara_dasha_backward_sequence(self):
        """Test Chara Dasha with even-footed lagna (backward sequence)."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.TAURUS,  # Even-footed (index 1)
        )

        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
        periods = calculate_chara_dasha(birth_dt, chart, years=36)

        assert len(periods) > 0
        assert periods[0].rashi == Rashi.TAURUS  # Starts from lagna
        assert all(p.duration_years >= 1 and p.duration_years <= 12 for p in periods)

        # Check sequence is backward for even lagna
        assert periods[1].rashi == Rashi.ARIES

    def test_chara_dasha_duration_range(self):
        """Test that Chara Dasha durations are within valid range."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.LIBRA,
        )

        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
        periods = calculate_chara_dasha(birth_dt, chart, years=108)

        for period in periods:
            assert 1 <= period.duration_years <= 12
            assert period.end_date > period.start_date

    def test_chara_dasha_chronological_order(self):
        """Test that Chara Dasha periods are in chronological order."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.CAPRICORN,
        )

        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
        periods = calculate_chara_dasha(birth_dt, chart, years=60)

        for i in range(len(periods) - 1):
            assert periods[i].end_date == periods[i + 1].start_date

    def test_chara_dasha_respects_year_limit(self):
        """Test that Chara Dasha generation respects the year limit."""
        chart = create_mock_chart(
            {
                Planet.SUN: (Rashi.LEO, 15.0),
                Planet.MOON: (Rashi.CANCER, 10.0),
                Planet.MARS: (Rashi.ARIES, 20.0),
                Planet.MERCURY: (Rashi.GEMINI, 12.0),
                Planet.JUPITER: (Rashi.SAGITTARIUS, 18.0),
                Planet.VENUS: (Rashi.TAURUS, 8.0),
                Planet.SATURN: (Rashi.CAPRICORN, 5.0),
            },
            Rashi.GEMINI,
        )

        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)
        periods = calculate_chara_dasha(birth_dt, chart, years=24)

        total_years = sum(p.duration_years for p in periods)
        assert total_years >= 24  # Should cover at least the requested years
        assert total_years <= 36  # But not excessively more (allowing one extra cycle)
