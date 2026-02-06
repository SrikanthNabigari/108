"""Tests for packages/self/src/strength.py enhancements.

Tests Tribhaga Bala, Varsha/Masa/Dina/Hora Bala, Yuddha Bala,
and Bhava Bala (house strength).
"""

from datetime import UTC, datetime

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition
from packages.self.src.strength import StrengthCalculator


def create_chart(
    planet_data: dict[Planet, tuple[Rashi, float, int]],
    lagna: Rashi = Rashi.ARIES,
    birth_dt: datetime | None = None,
) -> BirthChart:
    """Create a mock birth chart for testing.

    Args:
        planet_data: Dict mapping Planet to (rashi, degree_in_sign, house)
        lagna: Lagna rashi
        birth_dt: Birth datetime (defaults to 2000-01-01 12:00 UTC)
    """
    if birth_dt is None:
        birth_dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)

    bd = BirthData(
        datetime_utc=birth_dt,
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
    )

    planets = {}
    for planet, (rashi, degree, house) in planet_data.items():
        rashi_index = list(Rashi).index(rashi)
        longitude = rashi_index * 30 + degree

        planets[planet] = PlanetPosition(
            planet=planet,
            longitude=longitude,
            rashi=rashi,
            rashi_degree=degree,
            nakshatra="test",
            nakshatra_pada=1,
            nakshatra_lord=Planet.SUN,
            house=house,
        )

    houses = HouseCusps(
        ascendant=0.0,
        mc=270.0,
        cusps=[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
    )

    return BirthChart(
        user_id="test",
        birth_data=bd,
        planets=planets,
        houses=houses,
        lagna_rashi=lagna,
        moon_rashi=planets[Planet.MOON].rashi if Planet.MOON in planets else Rashi.ARIES,
        moon_nakshatra="test",
        ayanamsa=23.0,
        calculated_at=datetime.now(UTC),
    )


def _default_planet_data() -> dict[Planet, tuple[Rashi, float, int]]:
    """Standard planet data for testing."""
    return {
        Planet.SUN: (Rashi.ARIES, 15.0, 1),
        Planet.MOON: (Rashi.TAURUS, 10.0, 2),
        Planet.MARS: (Rashi.GEMINI, 20.0, 3),
        Planet.MERCURY: (Rashi.CANCER, 8.0, 4),
        Planet.JUPITER: (Rashi.LEO, 12.0, 5),
        Planet.VENUS: (Rashi.VIRGO, 5.0, 6),
        Planet.SATURN: (Rashi.LIBRA, 25.0, 7),
        Planet.RAHU: (Rashi.SCORPIO, 18.0, 8),
        Planet.KETU: (Rashi.TAURUS, 18.0, 2),
    }


class TestTribhagaBala:
    """Tests for Tribhaga Bala calculation."""

    def test_jupiter_always_has_tribhaga(self):
        """Jupiter always gets Tribhaga Bala regardless of time."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        result = calc._calculate_tribhaga_bala(Planet.JUPITER, chart)
        assert result == 60.0

    def test_jupiter_at_night(self):
        """Jupiter always gets Tribhaga Bala, even at night."""
        calc = StrengthCalculator()
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 22, 0, 0, tzinfo=UTC),
        )
        result = calc._calculate_tribhaga_bala(Planet.JUPITER, chart)
        assert result == 60.0

    def test_moon_strong_during_day(self):
        """Moon always gets Tribhaga Bala during daytime."""
        calc = StrengthCalculator()
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 14, 0, 0, tzinfo=UTC),
        )
        result = calc._calculate_tribhaga_bala(Planet.MOON, chart)
        assert result == 60.0

    def test_mars_strong_during_night(self):
        """Mars always gets Tribhaga Bala during nighttime."""
        calc = StrengthCalculator()
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 22, 0, 0, tzinfo=UTC),
        )
        result = calc._calculate_tribhaga_bala(Planet.MARS, chart)
        assert result == 60.0

    def test_mercury_first_third_day(self):
        """Mercury gets Tribhaga Bala in first third of day (6-10)."""
        calc = StrengthCalculator()
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 7, 0, 0, tzinfo=UTC),
        )
        result = calc._calculate_tribhaga_bala(Planet.MERCURY, chart)
        assert result == 60.0

    def test_sun_second_third_day(self):
        """Sun gets Tribhaga Bala in second third of day (10-14)."""
        calc = StrengthCalculator()
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 11, 0, 0, tzinfo=UTC),
        )
        result = calc._calculate_tribhaga_bala(Planet.SUN, chart)
        assert result == 60.0

    def test_planet_without_tribhaga_returns_zero(self):
        """A planet in wrong third gets 0."""
        calc = StrengthCalculator()
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 14, 0, 0, tzinfo=UTC),
        )
        # Mercury in 3rd third of day should NOT get Tribhaga
        result = calc._calculate_tribhaga_bala(Planet.MERCURY, chart)
        assert result == 0.0


class TestVarshaMasaDinaHoraBala:
    """Tests for Varsha/Masa/Dina/Hora Bala calculation."""

    def test_returns_float(self):
        """Should return a float value."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        result = calc._calculate_varsha_masa_dina_hora_bala(Planet.SUN, chart)
        assert isinstance(result, float)

    def test_maximum_60_virupas(self):
        """Maximum should be 60 (15 * 4 components)."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        for planet in [
            Planet.SUN,
            Planet.MOON,
            Planet.MARS,
            Planet.MERCURY,
            Planet.JUPITER,
            Planet.VENUS,
            Planet.SATURN,
        ]:
            result = calc._calculate_varsha_masa_dina_hora_bala(planet, chart)
            assert 0.0 <= result <= 60.0

    def test_dina_bala_saturday(self):
        """Saturn should get Dina Bala on Saturday."""
        calc = StrengthCalculator()
        # 2000-01-01 is a Saturday
        chart = create_chart(
            _default_planet_data(),
            birth_dt=datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
        )
        result = calc._calculate_varsha_masa_dina_hora_bala(Planet.SATURN, chart)
        # Should include at least 15 for Dina Bala
        assert result >= 15.0

    def test_different_planets_get_different_scores(self):
        """Different planets should generally get different scores."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        scores = {}
        for planet in [
            Planet.SUN,
            Planet.MOON,
            Planet.MARS,
            Planet.MERCURY,
            Planet.JUPITER,
            Planet.VENUS,
            Planet.SATURN,
        ]:
            scores[planet] = calc._calculate_varsha_masa_dina_hora_bala(planet, chart)
        # Not all should be the same
        assert len(set(scores.values())) > 1


class TestYuddhaBala:
    """Tests for Yuddha Bala (planetary war) calculation."""

    def test_no_war_when_distant(self):
        """No war when planets are more than 1 degree apart."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MARS, Planet.JUPITER, 100.0, 105.0)
        assert result == 0.0

    def test_war_within_one_degree(self):
        """War occurs when planets are within 1 degree."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MARS, Planet.JUPITER, 100.0, 100.5)
        assert result != 0.0

    def test_winner_gets_positive(self):
        """Planet with higher longitude wins (positive value)."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MARS, Planet.JUPITER, 100.5, 100.0)
        assert result == 60.0

    def test_loser_gets_negative(self):
        """Planet with lower longitude loses (negative value)."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MARS, Planet.JUPITER, 100.0, 100.5)
        assert result == -60.0

    def test_no_war_with_sun(self):
        """Sun cannot participate in planetary war."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.SUN, Planet.MARS, 100.0, 100.5)
        assert result == 0.0

    def test_no_war_with_moon(self):
        """Moon cannot participate in planetary war."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MOON, Planet.MARS, 100.0, 100.5)
        assert result == 0.0

    def test_no_war_with_rahu(self):
        """Rahu cannot participate in planetary war."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.RAHU, Planet.MARS, 100.0, 100.5)
        assert result == 0.0

    def test_no_war_with_ketu(self):
        """Ketu cannot participate in planetary war."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MARS, Planet.KETU, 100.0, 100.5)
        assert result == 0.0

    def test_exact_conjunction_draw(self):
        """Exact same longitude = draw (0)."""
        calc = StrengthCalculator()
        result = calc._calculate_yuddha_bala(Planet.MARS, Planet.JUPITER, 100.0, 100.0)
        assert result == 0.0


class TestBhavaBala:
    """Tests for Bhava Bala (house strength) calculation."""

    def test_valid_house_returns_result(self):
        """Valid house number should return a result dict."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        result = calc.calculate_bhava_bala(1, chart)
        assert result["house"] == 1
        assert "total" in result
        assert "components" in result

    def test_invalid_house_returns_error(self):
        """Invalid house number should return error."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        result = calc.calculate_bhava_bala(0, chart)
        assert result["total"] == 0.0
        assert "Invalid" in result["note"]

        result = calc.calculate_bhava_bala(13, chart)
        assert result["total"] == 0.0

    def test_has_four_components(self):
        """Bhava Bala should have 4 components."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        result = calc.calculate_bhava_bala(1, chart)
        components = result["components"]
        assert "bhavadhipati_bala" in components
        assert "bhava_dig_bala" in components
        assert "bhava_drishti_bala" in components
        assert "occupant_strength" in components

    def test_kendra_houses_have_higher_dig_bala(self):
        """Kendra houses (1, 4, 7, 10) should have higher directional strength."""
        calc = StrengthCalculator()

        kendra_dig = calc._calc_bhava_dig_bala(1)
        non_kendra_dig = calc._calc_bhava_dig_bala(8)

        assert kendra_dig > non_kendra_dig

    def test_all_houses_calculated(self):
        """Should calculate for all 12 houses."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())

        for house in range(1, 13):
            result = calc.calculate_bhava_bala(house, chart)
            assert result["house"] == house
            assert result["total"] > 0

    def test_get_all_bhava_balas(self):
        """Should return data for all 12 houses."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        all_balas = calc.get_all_bhava_balas(chart)

        assert len(all_balas) == 12
        for h in range(1, 13):
            assert h in all_balas
            assert all_balas[h]["house"] == h

    def test_strength_rating(self):
        """Should produce valid strength ratings."""
        calc = StrengthCalculator()
        valid_ratings = {"very_strong", "strong", "moderate", "weak", "very_weak"}

        chart = create_chart(_default_planet_data())
        for house in range(1, 13):
            result = calc.calculate_bhava_bala(house, chart)
            assert result["strength_rating"] in valid_ratings

    def test_benefic_occupant_adds_more_strength(self):
        """Houses with benefic planets should have more occupant strength."""
        calc = StrengthCalculator()

        # Jupiter in 1st house (benefic)
        data_benefic = _default_planet_data()
        data_benefic[Planet.JUPITER] = (Rashi.ARIES, 12.0, 1)
        chart_benefic = create_chart(data_benefic)
        strength_benefic = calc._calc_occupant_strength(1, chart_benefic)

        # Mars in 1st house (malefic) - move Jupiter elsewhere
        data_malefic = _default_planet_data()
        data_malefic[Planet.MARS] = (Rashi.ARIES, 20.0, 1)
        data_malefic[Planet.JUPITER] = (Rashi.LEO, 12.0, 5)
        chart_malefic = create_chart(data_malefic)
        strength_malefic = calc._calc_occupant_strength(1, chart_malefic)

        assert strength_benefic > strength_malefic


class TestShadbalaWithNewComponents:
    """Test that Shadbala integrates the new Kala Bala components."""

    def test_shadbala_includes_all_components(self):
        """Shadbala result should include all 6 components."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        result = calc.calculate_shadbala(Planet.SUN, chart)

        assert "components" in result
        components = result["components"]
        assert "sthana_bala" in components
        assert "dig_bala" in components
        assert "kala_bala" in components
        assert "chesta_bala" in components
        assert "naisargika_bala" in components
        assert "drik_bala" in components

    def test_kala_bala_includes_new_components(self):
        """Kala Bala should now be higher due to Tribhaga + VMDH components."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())

        # Jupiter should have high Kala Bala (always has Tribhaga)
        result = calc.calculate_shadbala(Planet.JUPITER, chart)
        kala_bala = result["components"]["kala_bala"]
        # With Tribhaga (60) + nathonnatha + paksha + ayana + VMDH, should be substantial
        assert kala_bala >= 60.0  # At minimum Jupiter gets 60 from Tribhaga

    def test_all_planets_shadbala(self):
        """All 7 main planets should have valid Shadbala."""
        calc = StrengthCalculator()
        chart = create_chart(_default_planet_data())
        strengths = calc.get_all_planet_strengths(chart)

        for planet_name in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
            assert planet_name in strengths
            assert strengths[planet_name]["total"] > 0
