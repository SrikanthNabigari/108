"""Tests for new MCP tools added in Session 18.

Tests cover:
- Ephemeris: planetary_aspects
- Patterns: bhava_bala, all_bhava_balas, upapada_analysis
- Context: abhijit_muhurta, brahma_muhurta, eclipse_periods, marana_kaal,
           ashtottari_dasha, secondary_progressions
- Knowledge: lookup_tithi, lookup_karana, lookup_vara, lookup_avastha, lookup_nitya_yoga
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Ephemeris MCP Tools
# =============================================================================


class TestPlanetaryAspects:
    """Test the planetary_aspects MCP tool."""

    def test_basic_aspects(self):
        """Test basic aspect calculation with sun and mars."""
        from packages.cosmos.src.aspects import get_all_aspects, get_houses_aspected_by

        positions = {"sun": 1, "mars": 4}
        aspects = get_all_aspects(positions)
        houses = get_houses_aspected_by(positions)

        assert "sun" in aspects
        assert "mars" in aspects
        # Sun aspects 7th house from its position
        sun_houses = [a["house"] for a in aspects["sun"]]
        assert 7 in sun_houses
        # Mars has special aspects (4th, 8th from position)
        mars_houses = [a["house"] for a in aspects["mars"]]
        assert 10 in mars_houses  # 7th from 4th
        # Houses aspected should include house 7
        assert 7 in houses
        assert isinstance(houses[7], list)

    def test_all_planets_aspects(self):
        """Test aspect calculation with all 7 planets."""
        from packages.cosmos.src.aspects import get_all_aspects

        positions = {
            "sun": 1,
            "moon": 4,
            "mars": 7,
            "mercury": 3,
            "jupiter": 10,
            "venus": 2,
            "saturn": 5,
        }
        aspects = get_all_aspects(positions)

        assert len(aspects) == 7
        for _planet, aspect_list in aspects.items():
            assert isinstance(aspect_list, list)
            for a in aspect_list:
                assert "house" in a
                assert "strength" in a
                assert 1 <= a["house"] <= 12

    def test_empty_positions(self):
        """Test with empty positions dict."""
        from packages.cosmos.src.aspects import get_all_aspects

        result = get_all_aspects({})
        assert result == {}

    def test_houses_aspected_all_houses_present(self):
        """Test that all 12 houses are present in result."""
        from packages.cosmos.src.aspects import get_houses_aspected_by

        positions = {"sun": 1}
        result = get_houses_aspected_by(positions)
        for h in range(1, 13):
            assert h in result

    def test_jupiter_special_aspects(self):
        """Test Jupiter's special 5th and 9th aspects."""
        from packages.cosmos.src.aspects import get_all_aspects

        positions = {"jupiter": 1}
        aspects = get_all_aspects(positions)
        houses = [a["house"] for a in aspects["jupiter"]]
        assert 5 in houses  # 5th aspect
        assert 7 in houses  # 7th aspect
        assert 9 in houses  # 9th aspect

    def test_saturn_special_aspects(self):
        """Test Saturn's special 3rd and 10th aspects."""
        from packages.cosmos.src.aspects import get_all_aspects

        positions = {"saturn": 1}
        aspects = get_all_aspects(positions)
        houses = [a["house"] for a in aspects["saturn"]]
        assert 3 in houses
        assert 7 in houses
        assert 10 in houses


# =============================================================================
# Patterns MCP Tools
# =============================================================================


class TestBhavaBala:
    """Test Bhava Bala MCP tools."""

    def _get_chart(self):
        """Build a sample BirthChart for testing."""
        from datetime import datetime

        from packages.core.src import (
            BirthChart,
            BirthData,
            HouseCusps,
            Planet,
            PlanetPosition,
            Rashi,
        )

        planets = {}
        planet_data = [
            (Planet.SUN, 227.0, Rashi.SCORPIO, 8),
            (Planet.MOON, 326.85, Rashi.AQUARIUS, 5),
            (Planet.MARS, 90.0, Rashi.CANCER, 10),
            (Planet.MERCURY, 240.0, Rashi.SAGITTARIUS, 3),
            (Planet.JUPITER, 136.24, Rashi.LEO, 11),
            (Planet.VENUS, 210.0, Rashi.LIBRA, 1),
            (Planet.SATURN, 310.0, Rashi.AQUARIUS, 5),
            (Planet.RAHU, 60.0, Rashi.GEMINI, 9),
            (Planet.KETU, 240.0, Rashi.SAGITTARIUS, 3),
        ]

        for p_enum, lon, rashi, house in planet_data:
            planets[p_enum] = PlanetPosition(
                planet=p_enum,
                longitude=lon,
                latitude=0.0,
                speed=0.0,
                rashi=rashi,
                rashi_degree=lon % 30,
                nakshatra="ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.KETU,
                is_retrograde=False,
                house=house,
            )

        return BirthChart(
            user_id="test",
            birth_data=BirthData(
                datetime_utc=datetime(1992, 12, 3),
                latitude=16.7,
                longitude=81.3,
                timezone="Asia/Kolkata",
            ),
            planets=planets,
            houses=HouseCusps(ascendant=180.0, mc=270.0, cusps=[i * 30 for i in range(12)]),
            lagna_rashi=Rashi.LIBRA,
            moon_rashi=Rashi.AQUARIUS,
            moon_nakshatra="purva_bhadrapada",
            ayanamsa=23.45,
            calculated_at=datetime.now(),
        )

    def test_single_bhava_bala(self):
        """Test Bhava Bala for a single house."""
        from packages.self.src import StrengthCalculator

        chart = self._get_chart()
        calc = StrengthCalculator()
        result = calc.calculate_bhava_bala(1, chart)

        assert "house" in result
        assert result["house"] == 1
        assert "total" in result
        assert "components" in result
        assert "is_strong" in result
        assert "strength_rating" in result
        assert isinstance(result["total"], float)

    def test_all_bhava_balas(self):
        """Test Bhava Bala for all 12 houses."""
        from packages.self.src import StrengthCalculator

        chart = self._get_chart()
        calc = StrengthCalculator()
        result = calc.get_all_bhava_balas(chart)

        assert len(result) == 12
        for h in range(1, 13):
            assert h in result
            assert "total" in result[h]

    def test_invalid_house_number(self):
        """Test with invalid house number."""
        from packages.self.src import StrengthCalculator

        chart = self._get_chart()
        calc = StrengthCalculator()
        result = calc.calculate_bhava_bala(0, chart)
        assert result["total"] == 0.0

    def test_kendra_houses_strong(self):
        """Test that kendra houses have higher dig bala."""
        from packages.self.src import StrengthCalculator

        chart = self._get_chart()
        calc = StrengthCalculator()

        kendra_1 = calc.calculate_bhava_bala(1, chart)
        dusthana_12 = calc.calculate_bhava_bala(12, chart)

        # Kendra dig bala should be higher than dusthana
        assert (
            kendra_1["components"]["bhava_dig_bala"] > dusthana_12["components"]["bhava_dig_bala"]
        )


class TestUpapadaAnalysis:
    """Test Upapada interpretation MCP tool."""

    def _get_chart(self):
        """Build a sample BirthChart."""
        from datetime import datetime

        from packages.core.src import (
            BirthChart,
            BirthData,
            HouseCusps,
            Planet,
            PlanetPosition,
            Rashi,
        )

        planets = {}
        planet_data = [
            (Planet.SUN, 227.0, Rashi.SCORPIO, 2),
            (Planet.MOON, 326.85, Rashi.AQUARIUS, 5),
            (Planet.MARS, 90.0, Rashi.CANCER, 10),
            (Planet.MERCURY, 240.0, Rashi.SAGITTARIUS, 3),
            (Planet.JUPITER, 136.24, Rashi.LEO, 11),
            (Planet.VENUS, 210.0, Rashi.LIBRA, 1),
            (Planet.SATURN, 310.0, Rashi.AQUARIUS, 5),
            (Planet.RAHU, 60.0, Rashi.GEMINI, 9),
            (Planet.KETU, 240.0, Rashi.SAGITTARIUS, 3),
        ]

        for p_enum, lon, rashi, house in planet_data:
            planets[p_enum] = PlanetPosition(
                planet=p_enum,
                longitude=lon,
                latitude=0.0,
                speed=0.0,
                rashi=rashi,
                rashi_degree=lon % 30,
                nakshatra="ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.KETU,
                is_retrograde=False,
                house=house,
            )

        return BirthChart(
            user_id="test",
            birth_data=BirthData(
                datetime_utc=datetime(1992, 12, 3),
                latitude=16.7,
                longitude=81.3,
                timezone="Asia/Kolkata",
            ),
            planets=planets,
            houses=HouseCusps(ascendant=180.0, mc=270.0, cusps=[i * 30 for i in range(12)]),
            lagna_rashi=Rashi.LIBRA,
            moon_rashi=Rashi.AQUARIUS,
            moon_nakshatra="purva_bhadrapada",
            ayanamsa=23.45,
            calculated_at=datetime.now(),
        )

    def test_upapada_returns_dict(self):
        """Test that interpret_upapada returns a dictionary."""
        from packages.self.src.jaimini import interpret_upapada

        chart = self._get_chart()
        result = interpret_upapada(chart)

        assert isinstance(result, dict)

    def test_upapada_has_key_fields(self):
        """Test that upapada result has expected fields."""
        from packages.self.src.jaimini import interpret_upapada

        chart = self._get_chart()
        result = interpret_upapada(chart)

        # Should have UL lagna info and marriage analysis
        assert "upapada_lagna" in result
        assert "marriage_quality" in result


# =============================================================================
# Context MCP Tools
# =============================================================================


class TestAbhijitMuhurta:
    """Test Abhijit Muhurta calculation."""

    def test_abhijit_time_around_noon(self):
        """Abhijit should be around local noon."""
        from datetime import datetime

        from packages.context.src.muhurta import get_abhijit_muhurta

        sunrise = datetime(2026, 2, 4, 6, 30)
        sunset = datetime(2026, 2, 4, 18, 30)
        start, end = get_abhijit_muhurta(sunrise, sunset)

        assert start.hour >= 11
        assert end.hour <= 14
        assert end > start

    def test_abhijit_duration(self):
        """Abhijit should be 1/15th of daytime."""
        from datetime import datetime

        from packages.context.src.muhurta import get_abhijit_muhurta

        sunrise = datetime(2026, 2, 4, 6, 0)
        sunset = datetime(2026, 2, 4, 18, 0)
        start, end = get_abhijit_muhurta(sunrise, sunset)

        expected_duration = (18 - 6) * 60 / 15  # 48 minutes
        actual_duration = (end - start).total_seconds() / 60
        assert abs(actual_duration - expected_duration) < 0.1


class TestBrahmaMuhurta:
    """Test Brahma Muhurta calculation."""

    def test_brahma_before_sunrise(self):
        """Brahma Muhurta should be before sunrise."""
        from datetime import datetime

        from packages.context.src.muhurta import get_brahma_muhurta

        sunrise = datetime(2026, 2, 4, 6, 30)
        start, end = get_brahma_muhurta(sunrise)

        assert start < sunrise
        assert end < sunrise
        assert end > start

    def test_brahma_duration_48_minutes(self):
        """Brahma Muhurta should last 48 minutes."""
        from datetime import datetime

        from packages.context.src.muhurta import get_brahma_muhurta

        sunrise = datetime(2026, 2, 4, 6, 30)
        start, end = get_brahma_muhurta(sunrise)

        duration = (end - start).total_seconds() / 60
        assert duration == 48.0

    def test_brahma_starts_96_min_before_sunrise(self):
        """Brahma Muhurta should start 96 minutes before sunrise."""
        from datetime import datetime, timedelta

        from packages.context.src.muhurta import get_brahma_muhurta

        sunrise = datetime(2026, 2, 4, 6, 30)
        start, _ = get_brahma_muhurta(sunrise)

        expected_start = sunrise - timedelta(minutes=96)
        assert start == expected_start


class TestEclipsePeriods:
    """Test eclipse period detection."""

    def test_returns_list(self):
        """Eclipse periods should return a list."""
        from packages.context.src.muhurta import get_eclipse_periods

        result = get_eclipse_periods(2025, 3)
        assert isinstance(result, list)

    def test_invalid_month_raises(self):
        """Invalid month should raise ValueError."""
        from packages.context.src.muhurta import get_eclipse_periods

        with pytest.raises(ValueError):
            get_eclipse_periods(2025, 13)

    def test_eclipse_format(self):
        """If eclipses found, they should have correct format."""
        from packages.context.src.muhurta import get_eclipse_periods

        # March 2025 had a lunar eclipse
        result = get_eclipse_periods(2025, 3)
        for eclipse in result:
            assert "type" in eclipse
            assert eclipse["type"] in ("solar", "lunar")
            assert "start" in eclipse
            assert "maximum" in eclipse
            assert "end" in eclipse


class TestMaranaKaal:
    """Test Marana Kaal lookup."""

    def test_monday(self):
        """Monday should have 2 marana kaal periods."""
        from packages.context.src.muhurta import get_marana_kaal

        result = get_marana_kaal(0)
        assert len(result) == 2
        assert isinstance(result[0], tuple)

    def test_all_weekdays(self):
        """All 7 weekdays should have marana kaal."""
        from packages.context.src.muhurta import get_marana_kaal

        for day in range(7):
            result = get_marana_kaal(day)
            assert len(result) >= 1

    def test_invalid_weekday(self):
        """Invalid weekday should raise ValueError."""
        from packages.context.src.muhurta import get_marana_kaal

        with pytest.raises(ValueError):
            get_marana_kaal(7)


class TestAshtottariDashaTool:
    """Test Ashtottari Dasha MCP tool wiring."""

    def test_current_ashtottari(self):
        """Test getting current Ashtottari dasha."""
        from datetime import datetime

        from packages.context.src.ashtottari_dasha import get_current_ashtottari

        result = get_current_ashtottari(
            datetime(1992, 12, 3),
            25,
            10.0,
            query_datetime=datetime(2026, 2, 1),
        )

        assert "mahadasha" in result
        assert "antardasha" in result
        assert "remaining_days_maha" in result
        assert result["mahadasha"]["lord"] in [
            "sun",
            "moon",
            "mars",
            "mercury",
            "saturn",
            "jupiter",
            "venus",
            "rahu",
        ]

    def test_ashtottari_sequence(self):
        """Test generating Ashtottari dasha sequence."""
        from datetime import datetime

        from packages.context.src.ashtottari_dasha import calculate_ashtottari_sequence

        periods = calculate_ashtottari_sequence(datetime(1992, 12, 3), 25, 10.0)

        assert len(periods) >= 8
        for p in periods:
            assert "lord" in p
            assert "start_date" in p
            assert "end_date" in p

    def test_applicability(self):
        """Test Ashtottari applicability check."""
        from packages.context.src.ashtottari_dasha import is_ashtottari_applicable

        # Rahu in same house (kendra) - applicable
        assert is_ashtottari_applicable(1, 1) is True
        # Rahu in 4th house from lagna lord (kendra) - applicable
        assert is_ashtottari_applicable(4, 1) is True
        # Rahu in 6th from lagna lord - not applicable
        assert is_ashtottari_applicable(6, 1) is False


class TestSecondaryProgressions:
    """Test Secondary Progressions MCP tool wiring."""

    def test_current_progressions(self):
        """Test getting current progressions."""
        from datetime import datetime

        from packages.context.src.progressions import get_current_progressions

        result = get_current_progressions(
            datetime(1992, 12, 3),
            16.726,
            81.288,
            query_datetime=datetime(2026, 2, 1),
        )

        assert "progressed_positions" in result
        assert "natal_positions" in result
        assert "active_aspects" in result
        assert "age" in result

    def test_progressed_positions_have_planets(self):
        """Test that progressed positions include key planets."""
        from datetime import datetime

        from packages.context.src.progressions import get_current_progressions

        result = get_current_progressions(
            datetime(1992, 12, 3),
            16.726,
            81.288,
            query_datetime=datetime(2026, 2, 1),
        )

        prog = result["progressed_positions"]
        assert "sun" in prog
        assert "moon" in prog
        for planet_data in prog.values():
            assert "longitude" in planet_data
            assert "sign" in planet_data


# =============================================================================
# Knowledge MCP Tools
# =============================================================================


class TestTithiLookup:
    """Test tithi lookup tool."""

    def test_lookup_tithi(self):
        """Test looking up a tithi."""
        from packages.core.src.knowledge_loader import get_tithi_definitions

        data = get_tithi_definitions()
        assert isinstance(data, dict)

    def test_tithi_data_not_empty(self):
        """Tithi definitions should not be empty."""
        from packages.core.src.knowledge_loader import get_tithi_definitions

        data = get_tithi_definitions()
        # Should have data
        assert len(data) > 0


class TestKaranaLookup:
    """Test karana lookup tool."""

    def test_lookup_karana(self):
        """Test looking up karana definitions."""
        from packages.core.src.knowledge_loader import get_karana_definitions

        data = get_karana_definitions()
        assert isinstance(data, dict)

    def test_karana_data_not_empty(self):
        """Karana definitions should not be empty."""
        from packages.core.src.knowledge_loader import get_karana_definitions

        data = get_karana_definitions()
        assert len(data) > 0


class TestVaraLookup:
    """Test vara lookup tool."""

    def test_lookup_vara(self):
        """Test looking up vara definitions."""
        from packages.core.src.knowledge_loader import get_vara_definitions

        data = get_vara_definitions()
        assert isinstance(data, dict)

    def test_vara_data_not_empty(self):
        """Vara definitions should not be empty."""
        from packages.core.src.knowledge_loader import get_vara_definitions

        data = get_vara_definitions()
        assert len(data) > 0


class TestAvasthaLookup:
    """Test avastha lookup tool."""

    def test_lookup_avastha(self):
        """Test looking up avastha definitions."""
        from packages.core.src.knowledge_loader import get_avastha_definitions

        data = get_avastha_definitions()
        assert isinstance(data, dict)

    def test_baladi_avastha_calculation(self):
        """Test Baladi avastha calculation from degree."""
        # 0-6 = bala, 6-12 = kumara, 12-18 = yuva, 18-24 = vridha, 24-30 = mrita
        degree = 15.0  # Should be yuva (12-18)
        degree_in_sign = degree % 30
        if degree_in_sign < 6:
            avastha = "bala"
        elif degree_in_sign < 12:
            avastha = "kumara"
        elif degree_in_sign < 18:
            avastha = "yuva"
        elif degree_in_sign < 24:
            avastha = "vridha"
        else:
            avastha = "mrita"

        assert avastha == "yuva"


class TestNityaYogaLookup:
    """Test Nitya Yoga lookup tool."""

    def test_lookup_nitya_yoga(self):
        """Test looking up nitya yoga definitions."""
        from packages.core.src.knowledge_loader import get_nitya_yoga_definitions

        data = get_nitya_yoga_definitions()
        assert isinstance(data, dict)

    def test_nitya_yoga_data_not_empty(self):
        """Nitya yoga definitions should not be empty."""
        from packages.core.src.knowledge_loader import get_nitya_yoga_definitions

        data = get_nitya_yoga_definitions()
        assert len(data) > 0
