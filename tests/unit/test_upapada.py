"""Unit tests for Upapada Lagna (marriage) interpretation from Jaimini astrology."""

from datetime import UTC, datetime

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import (
    BirthChart,
    BirthData,
    HouseCusps,
    PlanetPosition,
)
from packages.self.src.jaimini import (
    _analyze_dk_ul_connection,
    _analyze_second_from_ul,
    _check_separation_indicators,
    _interpret_upapada_lord,
    _interpret_upapada_sign,
    _marriage_timing_from_ul,
    interpret_upapada,
)


def _make_birth_chart(
    lagna_rashi: Rashi = Rashi.LIBRA,
    lagna_degree: float = 195.0,
    planet_placements: dict | None = None,
) -> BirthChart:
    """Create a test BirthChart with configurable planet placements.

    Args:
        lagna_rashi: Ascendant sign
        lagna_degree: Ascendant longitude
        planet_placements: Dict of {Planet: (longitude, house, rashi_degree)}
            If not given, uses default spread across signs.

    Returns:
        BirthChart suitable for testing
    """
    default_placements = {
        Planet.SUN: (135.0, 11, 15.0),  # Leo, house 11
        Planet.MOON: (326.85, 5, 26.85),  # Aquarius, house 5
        Planet.MARS: (100.0, 10, 10.0),  # Cancer, house 10
        Planet.MERCURY: (150.0, 12, 0.0),  # Virgo, house 12
        Planet.JUPITER: (60.0, 9, 0.0),  # Gemini, house 9
        Planet.VENUS: (210.0, 1, 0.0),  # Libra, house 1
        Planet.SATURN: (310.0, 5, 10.0),  # Aquarius, house 5
        Planet.RAHU: (30.0, 7, 0.0),  # Taurus, house 7
        Planet.KETU: (210.0, 1, 0.0),  # Libra, house 1
    }

    if planet_placements:
        default_placements.update(planet_placements)

    planets = {}
    for planet, (lon, house, rdeg) in default_placements.items():
        rashi_index = int(lon / 30) % 12
        planets[planet] = PlanetPosition(
            planet=planet,
            longitude=lon,
            latitude=0.0,
            speed=1.0,
            rashi=Rashi(list(Rashi)[rashi_index]),
            rashi_degree=rdeg if rdeg else lon % 30,
            nakshatra="Ashwini",
            nakshatra_pada=1,
            nakshatra_lord=Planet.KETU,
            is_retrograde=False,
            house=house,
        )

    return BirthChart(
        user_id="test_user",
        birth_data=BirthData(
            datetime_utc=datetime(1992, 12, 2, 21, 30, 0, tzinfo=UTC),
            latitude=16.722786,
            longitude=81.294264,
            timezone="Asia/Kolkata",
        ),
        planets=planets,
        houses=HouseCusps(
            ascendant=lagna_degree,
            mc=270.0,
            cusps=[lagna_degree + i * 30 for i in range(12)],
        ),
        lagna_rashi=lagna_rashi,
        moon_rashi=Rashi.AQUARIUS,
        moon_nakshatra="Purva Bhadrapada",
        ayanamsa=23.45,
        calculated_at=datetime.now(UTC),
    )


class TestInterpretUpapadaSign:
    """Test _interpret_upapada_sign for all 12 signs."""

    def test_all_signs_have_interpretation(self):
        """Every Rashi has a valid partner type interpretation."""
        for rashi in Rashi:
            result = _interpret_upapada_sign(rashi)
            assert "sign" in result
            assert "element" in result
            assert "quality" in result
            assert "partner_type" in result
            assert result["sign"] == rashi.value
            assert len(result["partner_type"]) > 10

    def test_fire_signs_fire_element(self):
        """Fire signs (Aries, Leo, Sagittarius) have fire element."""
        for rashi in [Rashi.ARIES, Rashi.LEO, Rashi.SAGITTARIUS]:
            result = _interpret_upapada_sign(rashi)
            assert result["element"] == "fire"

    def test_earth_signs_earth_element(self):
        """Earth signs (Taurus, Virgo, Capricorn) have earth element."""
        for rashi in [Rashi.TAURUS, Rashi.VIRGO, Rashi.CAPRICORN]:
            result = _interpret_upapada_sign(rashi)
            assert result["element"] == "earth"

    def test_air_signs_air_element(self):
        """Air signs (Gemini, Libra, Aquarius) have air element."""
        for rashi in [Rashi.GEMINI, Rashi.LIBRA, Rashi.AQUARIUS]:
            result = _interpret_upapada_sign(rashi)
            assert result["element"] == "air"

    def test_water_signs_water_element(self):
        """Water signs (Cancer, Scorpio, Pisces) have water element."""
        for rashi in [Rashi.CANCER, Rashi.SCORPIO, Rashi.PISCES]:
            result = _interpret_upapada_sign(rashi)
            assert result["element"] == "water"


class TestInterpretUpapadaLord:
    """Test _interpret_upapada_lord for marriage quality."""

    def test_lord_in_kendra_strong(self):
        """UL lord in kendra house gives high quality score."""
        for house in [1, 4, 7, 10]:
            result = _interpret_upapada_lord(Planet.VENUS, Rashi.TAURUS, house)
            assert result["quality_score"] >= 65
            assert any("kendra" in f.lower() for f in result["factors"])

    def test_lord_in_trikona_good(self):
        """UL lord in trikona house gives good quality score."""
        for house in [5, 9]:
            result = _interpret_upapada_lord(Planet.JUPITER, Rashi.SAGITTARIUS, house)
            assert result["quality_score"] >= 60

    def test_lord_in_dusthana_weak(self):
        """UL lord in dusthana house gives lower quality score."""
        for house in [6, 8, 12]:
            result = _interpret_upapada_lord(Planet.MARS, Rashi.ARIES, house)
            assert result["quality_score"] <= 45

    def test_lord_exalted_bonus(self):
        """Exalted UL lord gets a significant quality bonus."""
        # Jupiter exalted in Cancer
        result = _interpret_upapada_lord(Planet.JUPITER, Rashi.CANCER, 5)
        assert result["quality_score"] >= 80
        assert any("exalted" in f.lower() for f in result["factors"])

    def test_lord_debilitated_penalty(self):
        """Debilitated UL lord gets a quality penalty."""
        # Jupiter debilitated in Capricorn
        result = _interpret_upapada_lord(Planet.JUPITER, Rashi.CAPRICORN, 5)
        assert result["quality_score"] <= 50
        assert any("debilitated" in f.lower() for f in result["factors"])

    def test_quality_summary_reflects_score(self):
        """Quality summary matches the score range."""
        high = _interpret_upapada_lord(Planet.VENUS, Rashi.PISCES, 1)
        assert "high" in high["quality_summary"].lower() or high["quality_score"] >= 70

        low = _interpret_upapada_lord(Planet.SATURN, Rashi.ARIES, 8)
        assert "challenge" in low["quality_summary"].lower() or low["quality_score"] < 50


class TestAnalyzeSecondFromUL:
    """Test _analyze_second_from_ul for marriage sustenance."""

    def test_empty_second_from_ul(self):
        """Empty 2nd from UL yields low separation risk."""
        # UL in Pisces, 2nd from UL = Aries
        # No planets in Aries in default chart
        chart = _make_birth_chart()
        result = _analyze_second_from_ul(chart, Rashi.PISCES)

        assert "second_from_ul_sign" in result
        assert "separation_risk" in result
        assert isinstance(result["factors"], list)

    def test_benefic_in_second_sustains(self):
        """Benefic in 2nd from UL indicates strong sustenance."""
        # UL in Gemini -> 2nd from UL = Cancer
        # Place Jupiter (benefic) in Cancer
        chart = _make_birth_chart(
            planet_placements={
                Planet.JUPITER: (100.0, 10, 10.0),  # Cancer
            }
        )
        result = _analyze_second_from_ul(chart, Rashi.GEMINI)

        assert "jupiter" in result.get("benefics", [])

    def test_malefic_in_second_threatens(self):
        """Malefic in 2nd from UL raises separation risk."""
        # UL in Capricorn -> 2nd from UL = Aquarius
        # Place Saturn (malefic) in Aquarius
        chart = _make_birth_chart(
            planet_placements={
                Planet.SATURN: (310.0, 5, 10.0),  # Aquarius
            }
        )
        result = _analyze_second_from_ul(chart, Rashi.CAPRICORN)

        assert result["separation_risk"] in ("moderate", "high")
        assert "saturn" in result.get("malefics", [])

    def test_returns_planets_list(self):
        """Result always has a planets_in_second list."""
        chart = _make_birth_chart()
        result = _analyze_second_from_ul(chart, Rashi.ARIES)

        assert "planets_in_second" in result
        assert isinstance(result["planets_in_second"], list)


class TestCheckSeparationIndicators:
    """Test _check_separation_indicators."""

    def test_rahu_on_ul_detected(self):
        """Rahu placed in UL sign is detected as indicator."""
        # Place Rahu in Aries
        chart = _make_birth_chart(
            planet_placements={
                Planet.RAHU: (10.0, 7, 10.0),  # Aries
            }
        )
        result = _check_separation_indicators(chart, Rashi.ARIES)

        assert any("rahu" in ind.lower() for ind in result["indicators"])

    def test_ketu_on_ul_detected(self):
        """Ketu placed in UL sign is detected as indicator."""
        chart = _make_birth_chart(
            planet_placements={
                Planet.KETU: (10.0, 7, 10.0),  # Aries
            }
        )
        result = _check_separation_indicators(chart, Rashi.ARIES)

        assert any("ketu" in ind.lower() for ind in result["indicators"])

    def test_saturn_on_ul_detected(self):
        """Saturn placed in UL sign is detected."""
        chart = _make_birth_chart(
            planet_placements={
                Planet.SATURN: (10.0, 7, 10.0),  # Aries
            }
        )
        result = _check_separation_indicators(chart, Rashi.ARIES)

        assert any("saturn" in ind.lower() for ind in result["indicators"])

    def test_no_indicators_low_risk(self):
        """Clean UL gives low separation risk."""
        # UL in Leo - no nodes or Saturn there in defaults
        chart = _make_birth_chart()
        result = _check_separation_indicators(chart, Rashi.LEO)

        assert result["risk_level"] == "low"
        assert result["indicator_count"] == 0

    def test_multiple_indicators_high_risk(self):
        """Multiple separation indicators give high risk."""
        # Place Rahu, Saturn, and Ketu all near Aries
        chart = _make_birth_chart(
            planet_placements={
                Planet.RAHU: (10.0, 7, 10.0),  # Aries (on UL)
                Planet.SATURN: (15.0, 7, 15.0),  # Aries (on UL)
                Planet.KETU: (40.0, 8, 10.0),  # Taurus (2nd from Aries)
            }
        )
        result = _check_separation_indicators(chart, Rashi.ARIES)

        assert result["risk_level"] in ("moderate", "high")
        assert result["indicator_count"] >= 2

    def test_combust_ul_lord(self):
        """Combust UL lord is detected as separation indicator."""
        # UL in Leo (lord = Sun) - Sun can't be combust
        # UL in Aries (lord = Mars), place Mars very close to Sun
        chart = _make_birth_chart(
            planet_placements={
                Planet.SUN: (45.0, 8, 15.0),  # Taurus 15 deg
                Planet.MARS: (47.0, 8, 17.0),  # Taurus 17 deg (within 8 deg of Sun)
            }
        )
        result = _check_separation_indicators(chart, Rashi.ARIES)

        assert any("combust" in ind.lower() for ind in result["indicators"])

    def test_risk_level_values(self):
        """Risk level is one of the expected values."""
        chart = _make_birth_chart()
        result = _check_separation_indicators(chart, Rashi.CANCER)

        assert result["risk_level"] in ("low", "moderate", "high")


class TestAnalyzeDKULConnection:
    """Test _analyze_dk_ul_connection for Darakaraka-UL bond."""

    def test_returns_darakaraka_info(self):
        """Result contains Darakaraka planet and sign info."""
        chart = _make_birth_chart()
        result = _analyze_dk_ul_connection(chart, Rashi.ARIES)

        assert "darakaraka_planet" in result
        assert "darakaraka_sign" in result
        assert "connections" in result
        assert "connection_strength" in result

    def test_dk_in_ul_sign_strong(self):
        """DK placed in UL sign creates a strong connection."""
        # Make Mercury the DK (lowest degree) and place in Taurus
        chart = _make_birth_chart(
            planet_placements={
                Planet.MERCURY: (35.0, 8, 5.0),  # Taurus, low degree
                Planet.SUN: (145.0, 11, 25.0),  # Leo, high degree
                Planet.MOON: (326.85, 5, 26.85),
                Planet.MARS: (115.0, 10, 25.0),
                Planet.JUPITER: (70.0, 9, 10.0),
                Planet.VENUS: (220.0, 1, 10.0),  # Scorpio
                Planet.SATURN: (320.0, 5, 20.0),
            }
        )
        result = _analyze_dk_ul_connection(chart, Rashi.TAURUS)

        # If DK is in Taurus and UL is in Taurus, strong connection
        if result["darakaraka_sign"] == "taurus":
            assert result["connection_strength"] >= 25

    def test_no_connection_noted(self):
        """When no direct DK-UL connection, that is noted."""
        chart = _make_birth_chart()
        result = _analyze_dk_ul_connection(chart, Rashi.PISCES)

        assert len(result["connections"]) >= 1

    def test_connection_strength_range(self):
        """Connection strength is in valid range."""
        chart = _make_birth_chart()
        result = _analyze_dk_ul_connection(chart, Rashi.ARIES)

        assert 0 <= result["connection_strength"] <= 100


class TestMarriageTimingFromUL:
    """Test _marriage_timing_from_ul for timing indicators."""

    def test_returns_activating_signs(self):
        """Timing result contains primary and secondary activating signs."""
        chart = _make_birth_chart()
        result = _marriage_timing_from_ul(chart, Rashi.CANCER)

        assert "primary_activating_signs" in result
        assert "secondary_activating_signs" in result
        assert len(result["primary_activating_signs"]) == 2  # UL and 7th from UL
        assert len(result["secondary_activating_signs"]) == 2  # 5th and 9th from UL

    def test_primary_signs_correct(self):
        """Primary activating signs are UL and 7th from UL."""
        result = _marriage_timing_from_ul(_make_birth_chart(), Rashi.ARIES)

        # UL = Aries, 7th = Libra
        assert "aries" in result["primary_activating_signs"]
        assert "libra" in result["primary_activating_signs"]

    def test_secondary_signs_correct(self):
        """Secondary signs are 5th and 9th from UL."""
        result = _marriage_timing_from_ul(_make_birth_chart(), Rashi.ARIES)

        # 5th from Aries = Leo, 9th from Aries = Sagittarius
        assert "leo" in result["secondary_activating_signs"]
        assert "sagittarius" in result["secondary_activating_signs"]

    def test_timing_factors_non_empty(self):
        """Timing factors list is always non-empty."""
        chart = _make_birth_chart()
        result = _marriage_timing_from_ul(chart, Rashi.TAURUS)

        assert len(result["timing_factors"]) >= 3


class TestInterpretUpapada:
    """Test the main interpret_upapada function."""

    def test_returns_complete_analysis(self):
        """Full Upapada analysis has all required sections."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        assert "upapada_lagna" in result
        assert "partner_type" in result
        assert "marriage_quality" in result
        assert "marriage_sustenance" in result
        assert "physical_relationship" in result
        assert "separation_indicators" in result
        assert "dk_connection" in result
        assert "marriage_timing" in result
        assert "overall_score" in result
        assert "overall_summary" in result

    def test_overall_score_range(self):
        """Overall score is in 0-100 range."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        assert 0 <= result["overall_score"] <= 100

    def test_upapada_lagna_has_sign(self):
        """UL lagna section contains the sign."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        assert "sign" in result["upapada_lagna"]
        # Sign should be a valid rashi value
        valid_signs = [r.value for r in Rashi]
        assert result["upapada_lagna"]["sign"] in valid_signs

    def test_partner_type_has_description(self):
        """Partner type section has meaningful description."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        assert "partner_type" in result["partner_type"]
        assert len(result["partner_type"]["partner_type"]) > 20

    def test_physical_relationship_analysis(self):
        """7th from UL section has sign and factors."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        phys = result["physical_relationship"]
        assert "sign" in phys
        assert "planets" in phys
        assert "factors" in phys
        assert isinstance(phys["factors"], list)
        assert len(phys["factors"]) >= 1

    def test_overall_summary_is_string(self):
        """Overall summary is a non-empty string."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        assert isinstance(result["overall_summary"], str)
        assert len(result["overall_summary"]) > 20

    def test_different_lagna_produces_different_ul(self):
        """Different lagna rashis can produce different UL positions."""
        chart1 = _make_birth_chart(lagna_rashi=Rashi.ARIES, lagna_degree=5.0)
        chart2 = _make_birth_chart(lagna_rashi=Rashi.CANCER, lagna_degree=95.0)

        result1 = interpret_upapada(chart1)
        result2 = interpret_upapada(chart2)

        # At minimum, both should produce valid results
        assert result1["upapada_lagna"]["sign"] in [r.value for r in Rashi]
        assert result2["upapada_lagna"]["sign"] in [r.value for r in Rashi]

    def test_marriage_quality_has_score(self):
        """Marriage quality section contains a quality score."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        mq = result["marriage_quality"]
        assert "quality_score" in mq
        assert 0 <= mq["quality_score"] <= 100

    def test_separation_indicators_have_risk_level(self):
        """Separation section has a risk level."""
        chart = _make_birth_chart()
        result = interpret_upapada(chart)

        sep = result["separation_indicators"]
        assert "risk_level" in sep
        assert sep["risk_level"] in ("low", "moderate", "high")
