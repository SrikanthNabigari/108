"""Tests for COSMOS layer bug fixes and new features.

Covers:
- Bug 1: _get_planet_index() correct own-sign mappings
- Bug 2: _get_exaltation_rashi() correct exaltation mappings
- Bug 3: panchanga.py get_panchanga() runtime fix, dead code removal, get_karana() logic
- Bug 4: houses.py get_house_lord_strength() implementation
- P1 Task 1: Parashari Aspects (Graha Drishti)
- P1 Task 2: Input validation in ephemeris.py
"""

from datetime import datetime

import pytest


# =============================================================================
# Bug 1 & 2: divisional.py planet index and exaltation fixes
# =============================================================================
class TestDivisionalPlanetMappings:
    """Tests for _get_planet_index() and _get_exaltation_rashi() correctness."""

    def test_planet_index_sun_is_leo(self):
        """Sun's own sign is Leo (index 4)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("sun") == 4

    def test_planet_index_moon_is_cancer(self):
        """Moon's own sign is Cancer (index 3)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("moon") == 3

    def test_planet_index_mars_is_aries(self):
        """Mars' own sign is Aries (index 0)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("mars") == 0

    def test_planet_index_mercury_is_gemini(self):
        """Mercury's own sign is Gemini (index 2)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("mercury") == 2

    def test_planet_index_jupiter_is_sagittarius(self):
        """Jupiter's own sign is Sagittarius (index 8)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("jupiter") == 8

    def test_planet_index_venus_is_taurus(self):
        """Venus' own sign is Taurus (index 1)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("venus") == 1

    def test_planet_index_saturn_is_capricorn(self):
        """Saturn's own sign is Capricorn (index 9)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("saturn") == 9

    def test_planet_index_rahu_is_aquarius(self):
        """Rahu is associated with Aquarius (index 10)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("rahu") == 10

    def test_planet_index_ketu_is_scorpio(self):
        """Ketu is associated with Scorpio (index 7)."""
        from packages.cosmos.src.divisional import _get_planet_index

        assert _get_planet_index("ketu") == 7

    def test_exaltation_sun_is_aries(self):
        """Sun is exalted in Aries (index 0), NOT Libra."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("sun") == 0  # Aries

    def test_exaltation_moon_is_taurus(self):
        """Moon is exalted in Taurus (index 1)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("moon") == 1

    def test_exaltation_mars_is_capricorn(self):
        """Mars is exalted in Capricorn (index 9)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("mars") == 9

    def test_exaltation_mercury_is_virgo(self):
        """Mercury is exalted in Virgo (index 5)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("mercury") == 5

    def test_exaltation_jupiter_is_cancer(self):
        """Jupiter is exalted in Cancer (index 3)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("jupiter") == 3

    def test_exaltation_venus_is_pisces(self):
        """Venus is exalted in Pisces (index 11)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("venus") == 11

    def test_exaltation_saturn_is_libra(self):
        """Saturn is exalted in Libra (index 6)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("saturn") == 6

    def test_exaltation_rahu_is_taurus(self):
        """Rahu is exalted in Taurus (index 1)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("rahu") == 1

    def test_exaltation_ketu_is_scorpio(self):
        """Ketu is exalted in Scorpio (index 7)."""
        from packages.cosmos.src.divisional import _get_exaltation_rashi

        assert _get_exaltation_rashi("ketu") == 7

    def test_vimshopaka_sun_exalted_in_aries(self):
        """Sun at 10 degrees Aries (longitude 10) should score 100 (exalted)."""
        from packages.cosmos.src.divisional import get_varga_vimshopaka

        planets = {"sun": 10.0}  # 10 degrees Aries = exaltation degree
        result = get_varga_vimshopaka(planets, divisions=[1])
        # Sun in Aries D1: rashi=0, own=4(Leo), exalt=0(Aries) -> match exaltation
        assert result["sun"]["strength_per_varga"][1] == 100
        assert 1 in result["sun"]["well_placed_vargas"]

    def test_vimshopaka_sun_debilitated_in_libra(self):
        """Sun at Libra (longitude 190) should score low (debilitated = 6th from exaltation)."""
        from packages.cosmos.src.divisional import get_varga_vimshopaka

        planets = {"sun": 190.0}  # Libra
        result = get_varga_vimshopaka(planets, divisions=[1])
        # Libra = index 6. Debilitation = (exalt 0 + 6) % 12 = 6 = Libra -> score 20
        assert result["sun"]["strength_per_varga"][1] == 20
        assert 1 in result["sun"]["badly_placed_vargas"]

    def test_vimshopaka_sun_in_own_sign_leo(self):
        """Sun at Leo (longitude 130) should score 100 (own sign)."""
        from packages.cosmos.src.divisional import get_varga_vimshopaka

        planets = {"sun": 130.0}  # Leo
        result = get_varga_vimshopaka(planets, divisions=[1])
        # Leo = index 4 = Sun's own sign -> score 100
        assert result["sun"]["strength_per_varga"][1] == 100
        assert 1 in result["sun"]["well_placed_vargas"]


# =============================================================================
# Bug 3: panchanga.py fixes
# =============================================================================
class TestPanchangaFixes:
    """Tests for panchanga.py bug fixes."""

    def test_tithi_calculation_basic(self):
        """Tithi calculation should work with valid Sun/Moon longitudes."""
        from packages.cosmos.src.panchanga import get_tithi

        # Moon 6 degrees ahead of Sun -> within first 12 degrees = Shukla Pratipada
        result = get_tithi(0.0, 6.0)
        assert result["number"] == 1
        assert result["paksha"] == "Shukla"
        assert result["name"] == "Pratipada"

    def test_tithi_purnima(self):
        """Moon ~180 degrees from Sun -> Purnima (just before exact 180)."""
        from packages.cosmos.src.panchanga import get_tithi

        # Purnima spans 168-180 degrees; 179 degrees = within Purnima
        result = get_tithi(0.0, 179.0)
        assert result["name"] == "Purnima"
        assert result["paksha"] == "Shukla"

    def test_tithi_amavasya(self):
        """Moon close to Sun (full cycle) -> Amavasya."""
        from packages.cosmos.src.panchanga import get_tithi

        # Distance ~348 degrees -> tithi_float = 29.0 -> Krishna Amavasya
        result = get_tithi(0.0, 348.0)
        assert result["paksha"] == "Krishna"

    def test_karana_pratipada_first_half(self):
        """First half of Shukla Pratipada should be Kimstughna (fixed)."""
        from packages.cosmos.src.panchanga import get_karana

        result = get_karana(1)
        assert result["name"] == "Kimstughna"
        assert result["type"] == "fixed"

    def test_karana_repeating(self):
        """Tithi 2 should produce a repeating karana."""
        from packages.cosmos.src.panchanga import get_karana

        result = get_karana(2)
        assert result["type"] == "repeating"
        assert result["name"] in [
            "Bava",
            "Balava",
            "Kaulava",
            "Taitila",
            "Gara",
            "Vanija",
            "Vishti",
        ]

    def test_karana_advanced_shukla(self):
        """Karana advanced for Shukla Paksha should work."""
        from packages.cosmos.src.panchanga import get_karana_advanced

        result = get_karana_advanced(1, 1)  # Shukla Pratipada
        assert result["name"] == "Kimstughna"
        assert result["type"] == "fixed"

    def test_karana_advanced_krishna(self):
        """Karana advanced for Krishna Paksha repeating karanas."""
        from packages.cosmos.src.panchanga import get_karana_advanced

        result = get_karana_advanced(5, 2)  # Krishna Panchami
        assert "name" in result
        assert result["type"] in ["fixed", "repeating"]

    def test_get_panchanga_runs_without_crash(self):
        """get_panchanga() should run without crashing with real ephemeris."""
        from packages.cosmos.src.panchanga import get_panchanga

        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = get_panchanga(dt, latitude=12.97, longitude=77.59)

        assert "tithi" in result
        assert "yoga" in result
        assert "karana" in result
        assert "vara" in result
        assert "nakshatra" in result
        assert result["tithi"]["number"] >= 1
        assert result["tithi"]["number"] <= 15
        assert result["yoga"]["number"] >= 1
        assert result["yoga"]["number"] <= 27

    def test_get_panchanga_sun_moon_longitudes(self):
        """get_panchanga() should include sun and moon longitude in output."""
        from packages.cosmos.src.panchanga import get_panchanga

        dt = datetime(2024, 6, 21, 12, 0, 0)
        result = get_panchanga(dt, latitude=28.61, longitude=77.21)

        assert "sun_longitude" in result
        assert "moon_longitude" in result
        assert 0 <= result["sun_longitude"] < 360
        assert 0 <= result["moon_longitude"] < 360

    def test_get_panchanga_nakshatra_populated(self):
        """Nakshatra data should be populated when ephemeris is available."""
        from packages.cosmos.src.panchanga import get_panchanga

        dt = datetime(2024, 3, 20, 12, 0, 0)
        result = get_panchanga(dt, latitude=12.97, longitude=77.59)

        nak = result["nakshatra"]
        assert nak["name"] != "Unavailable"
        assert nak["number"] is not None
        assert 1 <= nak["number"] <= 27


# =============================================================================
# Bug 4: houses.py get_house_lord_strength() implementation
# =============================================================================
class TestHouseLordStrength:
    """Tests for get_house_lord_strength() implementation."""

    def test_returns_float_not_none(self):
        """get_house_lord_strength() should return a float, not None."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"sun": {"longitude": 10.0}}  # Sun in Aries
        result = get_house_lord_strength("sun", positions, 1)
        assert result is not None
        assert isinstance(result, float)

    def test_sun_exalted_in_aries(self):
        """Sun in Aries should be exalted (score 100+)."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"sun": {"longitude": 10.0}}  # 10 degrees Aries
        result = get_house_lord_strength("sun", positions, 1)
        assert result >= 100  # exalted=100, Kendra+Trikona bonuses possible

    def test_sun_debilitated_in_libra(self):
        """Sun in Libra should be debilitated (score 0 + possible bonus)."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"sun": {"longitude": 190.0}}  # Libra
        result = get_house_lord_strength("sun", positions, 3)
        assert result <= 10  # debilitated=0, house 3 is not kendra/trikona

    def test_mars_in_own_sign_aries(self):
        """Mars in Aries should be in own sign (score ~80)."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"mars": {"longitude": 15.0}}  # Aries
        result = get_house_lord_strength("mars", positions, 7)
        assert result >= 80

    def test_jupiter_in_cancer_exalted(self):
        """Jupiter in Cancer should be exalted."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"jupiter": {"longitude": 95.0}}  # Cancer
        result = get_house_lord_strength("jupiter", positions, 5)
        assert result >= 100

    def test_venus_friendly_sign(self):
        """Venus in Mercury's sign (Gemini) should be friend."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"venus": {"longitude": 70.0}}  # Gemini
        result = get_house_lord_strength("venus", positions, 3)
        assert result >= 60  # friend=60

    def test_missing_planet_returns_none(self):
        """Missing planet should return None."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"sun": {"longitude": 10.0}}
        result = get_house_lord_strength("mars", positions, 1)
        assert result is None

    def test_invalid_house_raises(self):
        """Invalid house number should raise ValueError."""
        from packages.cosmos.src.houses import get_house_lord_strength

        positions = {"sun": {"longitude": 10.0}}
        with pytest.raises(ValueError):
            get_house_lord_strength("sun", positions, 0)
        with pytest.raises(ValueError):
            get_house_lord_strength("sun", positions, 13)

    def test_kendra_bonus(self):
        """House in Kendra (1,4,7,10) should get bonus."""
        from packages.cosmos.src.houses import get_house_lord_strength

        # Saturn in neutral sign for both cases
        positions = {"saturn": {"longitude": 250.0}}  # Sagittarius (Jupiter=neutral)
        score_kendra = get_house_lord_strength("saturn", positions, 1)  # Kendra house
        score_other = get_house_lord_strength("saturn", positions, 2)  # Non-kendra
        assert score_kendra > score_other


# =============================================================================
# P1 Task 1: Parashari Aspects (Graha Drishti)
# =============================================================================
class TestPlanetsAspects:
    """Tests for packages/cosmos/src/aspects.py."""

    def test_all_planets_aspect_7th(self):
        """All planets should aspect the 7th house from their position."""
        from packages.cosmos.src.aspects import get_planet_aspects

        for planet in [
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        ]:
            aspects = get_planet_aspects(planet, 1)
            assert 7 in aspects, f"{planet} should aspect 7th from house 1"

    def test_mars_special_aspects(self):
        """Mars should aspect 4th, 7th, and 8th from its position."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("mars", 1)
        assert aspects == [4, 7, 8]

    def test_jupiter_special_aspects(self):
        """Jupiter should aspect 5th, 7th, and 9th from its position."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("jupiter", 1)
        assert aspects == [5, 7, 9]

    def test_saturn_special_aspects(self):
        """Saturn should aspect 3rd, 7th, and 10th from its position."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("saturn", 1)
        assert aspects == [3, 7, 10]

    def test_rahu_ketu_aspects_like_jupiter(self):
        """Rahu and Ketu should aspect 5th, 7th, and 9th."""
        from packages.cosmos.src.aspects import get_planet_aspects

        for planet in ["rahu", "ketu"]:
            aspects = get_planet_aspects(planet, 1)
            assert aspects == [5, 7, 9], f"{planet} should aspect like Jupiter"

    def test_sun_only_7th(self):
        """Sun should only aspect the 7th house."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("sun", 3)
        assert aspects == [9]

    def test_mars_from_house_10(self):
        """Mars in house 10 should aspect 1, 4, 5 (wrapping around)."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("mars", 10)
        # 10 + 4 = 14 -> 2, 10 + 7 = 17 -> 5, 10 + 8 = 18 -> 6
        assert 1 in aspects  # 4th from 10 = (10-1+4)%12+1 = 1
        assert 4 in aspects  # 7th from 10 = (10-1+7)%12+1 = 4
        assert 5 in aspects  # 8th from 10 = (10-1+8)%12+1 = 5

    def test_jupiter_from_house_5(self):
        """Jupiter in house 5 wraps correctly."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("jupiter", 5)
        assert 9 in aspects  # 5th from 5
        assert 11 in aspects  # 7th from 5
        assert 1 in aspects  # 9th from 5

    def test_saturn_from_house_11(self):
        """Saturn in house 11 wraps correctly."""
        from packages.cosmos.src.aspects import get_planet_aspects

        aspects = get_planet_aspects("saturn", 11)
        assert 1 in aspects  # 3rd from 11 = (11-1+3)%12+1 = 1
        assert 5 in aspects  # 7th from 11
        assert 8 in aspects  # 10th from 11

    def test_invalid_house_raises(self):
        """Invalid house number should raise ValueError."""
        from packages.cosmos.src.aspects import get_planet_aspects

        with pytest.raises(ValueError):
            get_planet_aspects("mars", 0)
        with pytest.raises(ValueError):
            get_planet_aspects("mars", 13)

    def test_aspect_strength_7th_full(self):
        """7th house aspect should have full strength (1.0)."""
        from packages.cosmos.src.aspects import get_aspect_strength

        assert get_aspect_strength("sun", 7, 1) == 1.0
        assert get_aspect_strength("mars", 7, 1) == 1.0

    def test_aspect_strength_mars_4th_and_8th(self):
        """Mars 4th and 8th aspects should be 0.75 strength."""
        from packages.cosmos.src.aspects import get_aspect_strength

        assert get_aspect_strength("mars", 4, 1) == 0.75
        assert get_aspect_strength("mars", 8, 1) == 0.75

    def test_aspect_strength_jupiter_5th_9th_full(self):
        """Jupiter 5th and 9th aspects should be 1.0 strength."""
        from packages.cosmos.src.aspects import get_aspect_strength

        assert get_aspect_strength("jupiter", 5, 1) == 1.0
        assert get_aspect_strength("jupiter", 9, 1) == 1.0

    def test_aspect_strength_saturn_3rd_10th(self):
        """Saturn 3rd and 10th aspects should be 0.75 strength."""
        from packages.cosmos.src.aspects import get_aspect_strength

        assert get_aspect_strength("saturn", 3, 1) == 0.75
        assert get_aspect_strength("saturn", 10, 1) == 0.75

    def test_aspect_strength_no_aspect(self):
        """Sun aspecting a non-7th house should return 0.0."""
        from packages.cosmos.src.aspects import get_aspect_strength

        assert get_aspect_strength("sun", 3, 1) == 0.0
        assert get_aspect_strength("sun", 5, 1) == 0.0

    def test_aspect_strength_invalid_house(self):
        """Invalid house numbers should raise ValueError."""
        from packages.cosmos.src.aspects import get_aspect_strength

        with pytest.raises(ValueError):
            get_aspect_strength("mars", 0, 1)
        with pytest.raises(ValueError):
            get_aspect_strength("mars", 7, 0)

    def test_get_all_aspects(self):
        """get_all_aspects should return correct map for all planets."""
        from packages.cosmos.src.aspects import get_all_aspects

        positions = {"sun": 1, "mars": 4}
        result = get_all_aspects(positions)

        assert "sun" in result
        assert "mars" in result

        # Sun in house 1 aspects house 7
        sun_houses = [a["house"] for a in result["sun"]]
        assert 7 in sun_houses

        # Mars in house 4 aspects houses 7(4th), 10(7th), 11(8th)
        mars_houses = [a["house"] for a in result["mars"]]
        assert 7 in mars_houses  # 4th from 4
        assert 10 in mars_houses  # 7th from 4
        assert 11 in mars_houses  # 8th from 4

    def test_get_houses_aspected_by(self):
        """get_houses_aspected_by should correctly invert the aspect map."""
        from packages.cosmos.src.aspects import get_houses_aspected_by

        positions = {"sun": 1, "moon": 4}
        result = get_houses_aspected_by(positions)

        # House 7 should be aspected by sun (from 1)
        house7_planets = [a["planet"] for a in result[7]]
        assert "sun" in house7_planets

        # House 10 should be aspected by moon (7th from 4)
        house10_planets = [a["planet"] for a in result[10]]
        assert "moon" in house10_planets

    def test_get_houses_aspected_by_all_houses_present(self):
        """Result should have entries for all 12 houses."""
        from packages.cosmos.src.aspects import get_houses_aspected_by

        positions = {"sun": 1}
        result = get_houses_aspected_by(positions)
        assert len(result) == 12
        for h in range(1, 13):
            assert h in result

    def test_aspects_importable_from_cosmos(self):
        """Aspect functions should be importable from the cosmos package."""
        from packages.cosmos.src import (
            SPECIAL_ASPECTS,
            get_all_aspects,
            get_aspect_strength,
            get_houses_aspected_by,
            get_planet_aspects,
        )

        assert SPECIAL_ASPECTS is not None
        assert callable(get_planet_aspects)
        assert callable(get_aspect_strength)
        assert callable(get_all_aspects)
        assert callable(get_houses_aspected_by)


# =============================================================================
# P1 Task 2: Input Validation
# =============================================================================
class TestInputValidation:
    """Tests for input validation in ephemeris.py."""

    def test_validate_jd_too_low(self):
        """Julian Day before 1000 CE should raise ValueError."""
        from packages.cosmos.src.ephemeris import _validate_jd

        with pytest.raises(ValueError, match="Julian Day must be between"):
            _validate_jd(1000000.0)  # Way before 1000 CE

    def test_validate_jd_too_high(self):
        """Julian Day after 3000 CE should raise ValueError."""
        from packages.cosmos.src.ephemeris import _validate_jd

        with pytest.raises(ValueError, match="Julian Day must be between"):
            _validate_jd(3000000.0)  # Way after 3000 CE

    def test_validate_jd_valid(self):
        """Valid Julian Day should not raise."""
        from packages.cosmos.src.ephemeris import _validate_jd

        _validate_jd(2451545.0)  # J2000.0 epoch

    def test_validate_coordinates_valid(self):
        """Valid coordinates should not raise."""
        from packages.cosmos.src.ephemeris import _validate_coordinates

        _validate_coordinates(12.97, 77.59)  # Bangalore
        _validate_coordinates(-33.87, 151.21)  # Sydney
        _validate_coordinates(0.0, 0.0)  # Equator/Prime Meridian

    def test_validate_latitude_out_of_range(self):
        """Latitude outside -90 to 90 should raise ValueError."""
        from packages.cosmos.src.ephemeris import _validate_coordinates

        with pytest.raises(ValueError, match="Latitude"):
            _validate_coordinates(91.0, 0.0)
        with pytest.raises(ValueError, match="Latitude"):
            _validate_coordinates(-91.0, 0.0)

    def test_validate_longitude_out_of_range(self):
        """Longitude outside -180 to 180 should raise ValueError."""
        from packages.cosmos.src.ephemeris import _validate_coordinates

        with pytest.raises(ValueError, match="Longitude"):
            _validate_coordinates(0.0, 181.0)
        with pytest.raises(ValueError, match="Longitude"):
            _validate_coordinates(0.0, -181.0)

    def test_get_planet_position_validates_jd(self):
        """get_planet_position should validate jd range."""
        from packages.cosmos.src.ephemeris import get_planet_position

        with pytest.raises(ValueError):
            get_planet_position("sun", 1000000.0)

    def test_get_house_cusps_validates_coordinates(self):
        """get_house_cusps should validate latitude and longitude."""
        from packages.cosmos.src.ephemeris import get_house_cusps

        with pytest.raises(ValueError, match="Latitude"):
            get_house_cusps(2451545.0, 100.0, 0.0)
        with pytest.raises(ValueError, match="Longitude"):
            get_house_cusps(2451545.0, 0.0, 200.0)

    def test_get_house_cusps_validates_jd(self):
        """get_house_cusps should validate jd range."""
        from packages.cosmos.src.ephemeris import get_house_cusps

        with pytest.raises(ValueError, match="Julian Day"):
            get_house_cusps(1000000.0, 12.97, 77.59)


# =============================================================================
# Integration: Dignity lookup works with corrected planet mappings
# =============================================================================
class TestDignityIntegration:
    """Integration tests verifying dignity functions use correct mappings."""

    def test_sun_exalted_in_aries_via_dignity(self):
        """Dignity function should detect Sun exalted in Aries."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("sun", "aries") == "exalted"

    def test_sun_debilitated_in_libra_via_dignity(self):
        """Dignity function should detect Sun debilitated in Libra."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("sun", "libra") == "debilitated"

    def test_sun_moolatrikona_in_leo(self):
        """Sun in Leo should be moolatrikona."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("sun", "leo") == "moolatrikona"

    def test_mars_exalted_in_capricorn(self):
        """Mars exalted in Capricorn."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("mars", "capricorn") == "exalted"

    def test_mars_debilitated_in_cancer(self):
        """Mars debilitated in Cancer."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("mars", "cancer") == "debilitated"

    def test_jupiter_exalted_in_cancer(self):
        """Jupiter exalted in Cancer."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("jupiter", "cancer") == "exalted"

    def test_saturn_exalted_in_libra(self):
        """Saturn exalted in Libra."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("saturn", "libra") == "exalted"

    def test_venus_exalted_in_pisces(self):
        """Venus exalted in Pisces."""
        from packages.cosmos.src.divisional import get_planet_dignity_in_sign

        assert get_planet_dignity_in_sign("venus", "pisces") == "exalted"

    def test_vimshopaka_bala_uses_correct_exaltation(self):
        """Vimshopaka Bala should use corrected exaltation data."""
        from packages.cosmos.src.divisional import calculate_vimshopaka_bala

        # Sun at 10 degrees Aries = exalted
        result = calculate_vimshopaka_bala("sun", 10.0, "shad_varga")
        # D1 should show exalted dignity for Sun in Aries
        d1_entry = next(v for v in result["varga_details"] if v["division"] == 1)
        assert d1_entry["dignity"] == "exalted"
        assert d1_entry["score"] == 20  # DIGNITY_SCORES["exalted"] = 20
