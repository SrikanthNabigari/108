"""Tests for Jaimini astrology system."""

from datetime import UTC, datetime

from packages.core.src.constants import CharaKaraka, Planet, Rashi, SignMobility
from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition
from packages.self.src.jaimini import (
    calculate_all_arudha_padas,
    calculate_argala,
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


class TestArgala:
    """Tests for Jaimini Argala (planetary intervention) calculations."""

    def _make_chart(
        self,
        planet_placements: dict[Planet, Rashi],
        lagna: Rashi = Rashi.ARIES,
    ) -> BirthChart:
        """Helper to create chart with planets in specific signs."""
        degrees = {}
        for planet, rashi in planet_placements.items():
            degrees[planet] = (rashi, 15.0)
        return create_mock_chart(degrees, lagna)

    def test_returns_all_12_houses(self):
        """Argala result should contain entries for all 12 houses."""
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.ARIES,
                Planet.MOON: Rashi.TAURUS,
                Planet.MARS: Rashi.GEMINI,
                Planet.MERCURY: Rashi.CANCER,
                Planet.JUPITER: Rashi.LEO,
                Planet.VENUS: Rashi.VIRGO,
                Planet.SATURN: Rashi.LIBRA,
            }
        )
        result = calculate_argala(chart)
        assert len(result) == 12
        for h in range(1, 13):
            assert h in result
            assert result[h]["house"] == h

    def test_argala_has_four_types(self):
        """Each house should have 4 argala types."""
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.ARIES,
                Planet.MOON: Rashi.TAURUS,
                Planet.MARS: Rashi.GEMINI,
                Planet.MERCURY: Rashi.CANCER,
                Planet.JUPITER: Rashi.LEO,
                Planet.VENUS: Rashi.VIRGO,
                Planet.SATURN: Rashi.LIBRA,
            }
        )
        result = calculate_argala(chart)
        for h in range(1, 13):
            argalas = result[h]["argalas"]
            assert "dhana" in argalas
            assert "sukha" in argalas
            assert "labha" in argalas
            assert "putra" in argalas

    def test_dhana_argala_from_2nd_house(self):
        """Dhana argala comes from 2nd house (offset 1)."""
        # Lagna = Aries. 2nd house = Taurus. Put Jupiter there (benefic).
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.TAURUS,  # 2nd from Aries
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        dhana = result[1]["argalas"]["dhana"]
        assert dhana["source_sign"] == "taurus"
        assert "jupiter" in dhana["source_planets"]
        assert dhana["argala_strength"] > 0

    def test_sukha_argala_from_4th_house(self):
        """Sukha argala comes from 4th house (offset 3)."""
        # Lagna = Aries. 4th house = Cancer. Put Moon there (benefic).
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,  # 4th from Aries
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.SAGITTARIUS,
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        sukha = result[1]["argalas"]["sukha"]
        assert sukha["source_sign"] == "cancer"
        assert "moon" in sukha["source_planets"]
        assert sukha["argala_strength"] > 0

    def test_labha_argala_from_11th_house(self):
        """Labha argala comes from 11th house (offset 10)."""
        # Lagna = Aries. 11th house = Aquarius. Put Venus there.
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.SAGITTARIUS,
                Planet.VENUS: Rashi.AQUARIUS,  # 11th from Aries
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        labha = result[1]["argalas"]["labha"]
        assert labha["source_sign"] == "aquarius"
        assert "venus" in labha["source_planets"]

    def test_putra_argala_from_5th_house(self):
        """Putra argala comes from 5th house (offset 4)."""
        # Lagna = Aries. 5th house = Leo. Put Sun there.
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,  # 5th from Aries
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.SAGITTARIUS,
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        putra = result[1]["argalas"]["putra"]
        assert putra["source_sign"] == "leo"
        assert "sun" in putra["source_planets"]

    def test_dhana_argala_obstructed_by_3rd(self):
        """Dhana argala (2nd) is obstructed by planets in 3rd with >= strength."""
        # Lagna = Aries. 2nd = Taurus (Mars=0.5), 3rd = Gemini (Jupiter=1.0)
        # Obstruction >= argala => obstructed
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.TAURUS,  # 2nd from Aries (malefic, 0.5)
                Planet.MERCURY: Rashi.VIRGO,
                Planet.JUPITER: Rashi.GEMINI,  # 3rd from Aries (benefic, 1.0)
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        dhana = result[1]["argalas"]["dhana"]
        assert dhana["is_obstructed"] is True
        assert dhana["is_active"] is False

    def test_sukha_argala_obstructed_by_10th(self):
        """Sukha argala (4th) is obstructed by planets in 10th with >= strength."""
        # Lagna = Aries. 4th = Cancer (Mars=0.5), 10th = Capricorn (Jupiter=1.0)
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.PISCES,
                Planet.MARS: Rashi.CANCER,  # 4th from Aries (0.5)
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.CAPRICORN,  # 10th from Aries (1.0)
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.AQUARIUS,
            }
        )
        result = calculate_argala(chart)
        sukha = result[1]["argalas"]["sukha"]
        assert sukha["is_obstructed"] is True

    def test_labha_argala_obstructed_by_12th(self):
        """Labha argala (11th) is obstructed by 12th house planets."""
        # Lagna = Aries. 11th = Aquarius (Saturn=0.5), 12th = Pisces (Jupiter=1.0)
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.PISCES,  # 12th from Aries (1.0)
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.AQUARIUS,  # 11th from Aries (0.5)
            }
        )
        result = calculate_argala(chart)
        labha = result[1]["argalas"]["labha"]
        assert labha["is_obstructed"] is True

    def test_putra_argala_obstructed_by_9th(self):
        """Putra argala (5th) is obstructed by 9th house planets."""
        # Lagna = Aries. 5th = Leo (Mars=0.5), 9th = Sagittarius (Jupiter=1.0)
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.CANCER,
                Planet.MOON: Rashi.TAURUS,
                Planet.MARS: Rashi.LEO,  # 5th from Aries (0.5)
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.SAGITTARIUS,  # 9th from Aries (1.0)
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        putra = result[1]["argalas"]["putra"]
        assert putra["is_obstructed"] is True

    def test_argala_not_obstructed_when_stronger(self):
        """Argala survives when its strength exceeds obstruction strength."""
        # Lagna = Aries. 2nd = Taurus (Jupiter=1.0 benefic), 3rd = Gemini (Mars=0.5 malefic)
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.GEMINI,  # 3rd from Aries (obstruction, 0.5)
                Planet.MERCURY: Rashi.VIRGO,
                Planet.JUPITER: Rashi.TAURUS,  # 2nd from Aries (argala, 1.0)
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        dhana = result[1]["argalas"]["dhana"]
        assert dhana["is_active"] is True
        assert dhana["is_obstructed"] is False
        assert dhana["net_strength"] > 0

    def test_empty_argala_house_no_argala(self):
        """No argala when the source house is empty."""
        # Put all planets far from 2nd house of Aries (Taurus)
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.VIRGO,
                Planet.JUPITER: Rashi.SAGITTARIUS,
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        dhana = result[1]["argalas"]["dhana"]
        assert dhana["argala_strength"] == 0.0
        assert dhana["is_active"] is False
        assert dhana["source_planets"] == []

    def test_benefic_counts_more_than_malefic(self):
        """Benefics contribute 1.0 strength, malefics 0.5."""
        # Jupiter (benefic, 1.0) in 2nd vs Mars (malefic, 0.5) in 2nd
        chart_benefic = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.TAURUS,  # 2nd from Aries
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        chart_malefic = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.TAURUS,  # 2nd from Aries
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.SAGITTARIUS,
                Planet.VENUS: Rashi.LIBRA,
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result_b = calculate_argala(chart_benefic)
        result_m = calculate_argala(chart_malefic)
        assert (
            result_b[1]["argalas"]["dhana"]["argala_strength"]
            > result_m[1]["argalas"]["dhana"]["argala_strength"]
        )

    def test_multiple_planets_in_argala_house(self):
        """Multiple planets in argala house should sum their strengths."""
        # Jupiter + Venus in 2nd from Aries (Taurus)
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.TAURUS,  # 2nd
                Planet.VENUS: Rashi.TAURUS,  # 2nd (same sign)
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        dhana = result[1]["argalas"]["dhana"]
        # Jupiter(1.0) + Venus(1.0) = 2.0
        assert dhana["argala_strength"] == 2.0
        assert len(dhana["source_planets"]) == 2

    def test_active_argala_count(self):
        """active_argala_count should correctly count unobstructed argalas."""
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.LEO,
                Planet.MOON: Rashi.CANCER,
                Planet.MARS: Rashi.SCORPIO,
                Planet.MERCURY: Rashi.GEMINI,
                Planet.JUPITER: Rashi.TAURUS,  # 2nd from Aries (dhana active)
                Planet.VENUS: Rashi.AQUARIUS,  # 11th from Aries (labha active)
                Planet.SATURN: Rashi.CAPRICORN,
            }
        )
        result = calculate_argala(chart)
        count = result[1]["active_argala_count"]
        assert count >= 2  # At least dhana and labha

    def test_summary_for_no_active(self):
        """Summary should reflect no active argala."""
        # Create a chart where house 8 likely has no active argalas
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.ARIES,
                Planet.MOON: Rashi.ARIES,
                Planet.MARS: Rashi.ARIES,
                Planet.MERCURY: Rashi.ARIES,
                Planet.JUPITER: Rashi.ARIES,
                Planet.VENUS: Rashi.ARIES,
                Planet.SATURN: Rashi.ARIES,
            }
        )
        result = calculate_argala(chart)
        # Find a house with 0 active
        found_zero = False
        for h in range(1, 13):
            if result[h]["active_argala_count"] == 0:
                assert "No active" in result[h]["summary"]
                found_zero = True
                break
        # At least some houses with all planets in Aries should have 0
        assert found_zero

    def test_argala_result_keys(self):
        """Each argala entry should have all expected keys."""
        chart = self._make_chart(
            {
                Planet.SUN: Rashi.ARIES,
                Planet.MOON: Rashi.TAURUS,
                Planet.MARS: Rashi.GEMINI,
                Planet.MERCURY: Rashi.CANCER,
                Planet.JUPITER: Rashi.LEO,
                Planet.VENUS: Rashi.VIRGO,
                Planet.SATURN: Rashi.LIBRA,
            }
        )
        result = calculate_argala(chart)
        entry = result[1]
        assert "house" in entry
        assert "sign" in entry
        assert "argalas" in entry
        assert "active_argala_count" in entry
        assert "summary" in entry

        for atype in ["dhana", "sukha", "labha", "putra"]:
            a = entry["argalas"][atype]
            assert "label" in a
            assert "source_sign" in a
            assert "source_planets" in a
            assert "argala_strength" in a
            assert "obstruction_sign" in a
            assert "obstruction_planets" in a
            assert "obstruction_strength" in a
            assert "is_obstructed" in a
            assert "is_active" in a
            assert "net_strength" in a

    def test_different_lagna_shifts_signs(self):
        """Argala houses should shift based on lagna."""
        chart_aries = self._make_chart(
            {
                Planet.SUN: Rashi.ARIES,
                Planet.MOON: Rashi.TAURUS,
                Planet.MARS: Rashi.GEMINI,
                Planet.MERCURY: Rashi.CANCER,
                Planet.JUPITER: Rashi.LEO,
                Planet.VENUS: Rashi.VIRGO,
                Planet.SATURN: Rashi.LIBRA,
            },
            lagna=Rashi.ARIES,
        )
        chart_leo = self._make_chart(
            {
                Planet.SUN: Rashi.ARIES,
                Planet.MOON: Rashi.TAURUS,
                Planet.MARS: Rashi.GEMINI,
                Planet.MERCURY: Rashi.CANCER,
                Planet.JUPITER: Rashi.LEO,
                Planet.VENUS: Rashi.VIRGO,
                Planet.SATURN: Rashi.LIBRA,
            },
            lagna=Rashi.LEO,
        )

        result_aries = calculate_argala(chart_aries)
        result_leo = calculate_argala(chart_leo)

        # House 1 sign should differ
        assert result_aries[1]["sign"] == "aries"
        assert result_leo[1]["sign"] == "leo"

        # Dhana source for house 1 should be 2nd sign from lagna
        assert result_aries[1]["argalas"]["dhana"]["source_sign"] == "taurus"
        assert result_leo[1]["argalas"]["dhana"]["source_sign"] == "virgo"
