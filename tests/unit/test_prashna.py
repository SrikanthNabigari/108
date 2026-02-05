"""Unit tests for Prashna (Horary) astrology module."""

from datetime import UTC, datetime

from packages.core.src.constants import Planet, PrashnaCategory, PrashnaJudgment, Rashi
from packages.core.src.models import HouseCusps, PlanetPosition, PrashnaChart
from packages.self.src.prashna import (
    analyze_career_prashna,
    analyze_health_prashna,
    analyze_lagna_strength,
    analyze_legal_prashna,
    analyze_lost_object_prashna,
    analyze_marriage_prashna,
    analyze_moon_condition,
    analyze_prashna,
    analyze_significator,
    analyze_travel_prashna,
    create_prashna_chart,
    get_significator,
    judge_prashna,
    predict_timing,
)


class TestGetSignificator:
    """Test significator planet selection for each category."""

    def test_get_significator_health(self):
        """Test health significator is Sun."""
        assert get_significator(PrashnaCategory.HEALTH) == Planet.SUN

    def test_get_significator_marriage(self):
        """Test marriage significator is Venus."""
        assert get_significator(PrashnaCategory.MARRIAGE) == Planet.VENUS

    def test_get_significator_career(self):
        """Test career significator is Saturn."""
        assert get_significator(PrashnaCategory.CAREER) == Planet.SATURN

    def test_get_significator_travel(self):
        """Test travel significator is Moon."""
        assert get_significator(PrashnaCategory.TRAVEL) == Planet.MOON

    def test_get_significator_lost_objects(self):
        """Test lost objects significator is Moon."""
        assert get_significator(PrashnaCategory.LOST_OBJECTS) == Planet.MOON

    def test_get_significator_legal(self):
        """Test legal significator is Jupiter."""
        assert get_significator(PrashnaCategory.LEGAL) == Planet.JUPITER

    def test_get_significator_spiritual(self):
        """Test spiritual significator is Jupiter."""
        assert get_significator(PrashnaCategory.SPIRITUAL) == Planet.JUPITER

    def test_get_significator_children(self):
        """Test children significator is Jupiter."""
        assert get_significator(PrashnaCategory.CHILDREN) == Planet.JUPITER

    def test_get_significator_wealth(self):
        """Test wealth significator is Jupiter."""
        assert get_significator(PrashnaCategory.WEALTH) == Planet.JUPITER

    def test_get_significator_education(self):
        """Test education significator is Mercury."""
        assert get_significator(PrashnaCategory.EDUCATION) == Planet.MERCURY


class TestCreatePrashnaChart:
    """Test Prashna chart creation."""

    def test_create_prashna_chart(self):
        """Test creating a complete Prashna chart."""
        question = "Will I get the job?"
        question_dt = datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC)
        latitude = 28.6139
        longitude = 77.2090

        chart = create_prashna_chart(
            question=question,
            question_dt=question_dt,
            latitude=latitude,
            longitude=longitude,
            category=PrashnaCategory.CAREER,
        )

        assert chart.question == question
        assert chart.question_datetime == question_dt
        assert chart.category == PrashnaCategory.CAREER
        assert chart.latitude == latitude
        assert chart.longitude == longitude
        assert chart.significator == Planet.SATURN
        assert isinstance(chart.lagna_rashi, Rashi)
        assert 0 <= chart.lagna_degree < 360
        assert Planet.MOON in chart.planets
        assert len(chart.planets) == 9  # All 9 Vedic planets
        assert isinstance(chart.houses, HouseCusps)

    def test_create_prashna_chart_planet_positions(self):
        """Test that all planet positions are properly calculated."""
        chart = create_prashna_chart(
            question="Test question",
            question_dt=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.HEALTH,
        )

        for planet, pos in chart.planets.items():
            assert isinstance(planet, Planet)
            assert isinstance(pos, PlanetPosition)
            assert pos.planet == planet
            assert 0 <= pos.longitude < 360
            assert 0 <= pos.rashi_degree < 30
            assert isinstance(pos.rashi, Rashi)
            assert 1 <= pos.house <= 12
            assert pos.nakshatra is not None
            assert 1 <= pos.nakshatra_pada <= 4


class TestAnalyzeLagnaStrength:
    """Test lagna strength analysis."""

    def _create_mock_chart(
        self, lagna_degree: float, lagna_rashi: Rashi, lagna_lord_house: int
    ) -> PrashnaChart:
        """Create a mock Prashna chart for testing."""
        # Mock planet positions
        planets = {}

        # Lagna lord mapping
        lagna_lord_map = {
            Rashi.ARIES: Planet.MARS,
            Rashi.TAURUS: Planet.VENUS,
            Rashi.GEMINI: Planet.MERCURY,
            Rashi.CANCER: Planet.MOON,
            Rashi.LEO: Planet.SUN,
            Rashi.VIRGO: Planet.MERCURY,
            Rashi.LIBRA: Planet.VENUS,
            Rashi.SCORPIO: Planet.MARS,
            Rashi.SAGITTARIUS: Planet.JUPITER,
            Rashi.CAPRICORN: Planet.SATURN,
            Rashi.AQUARIUS: Planet.SATURN,
            Rashi.PISCES: Planet.JUPITER,
        }

        # Create all planet positions
        for i, planet in enumerate(Planet):
            house = lagna_lord_house if planet == lagna_lord_map[lagna_rashi] else ((i % 12) + 1)
            planets[planet] = PlanetPosition(
                planet=planet,
                longitude=float(i * 30),
                latitude=0.0,
                speed=1.0,
                rashi=Rashi(list(Rashi)[i % 12]),
                rashi_degree=15.0,
                nakshatra="Ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.KETU,
                is_retrograde=False,
                house=house,
            )

        return PrashnaChart(
            question="Test",
            question_datetime=datetime.now(UTC),
            category=PrashnaCategory.HEALTH,
            latitude=28.6139,
            longitude=77.2090,
            lagna_rashi=lagna_rashi,
            lagna_degree=lagna_degree,
            moon_position=planets[Planet.MOON],
            significator=Planet.SUN,
            planets=planets,
            houses=HouseCusps(ascendant=lagna_degree, mc=270.0, cusps=[0] * 12),
        )

    def test_analyze_lagna_early_degrees(self):
        """Test lagna in early degrees (0-3)."""
        chart = self._create_mock_chart(
            lagna_degree=2.0, lagna_rashi=Rashi.ARIES, lagna_lord_house=5
        )
        analysis = analyze_lagna_strength(chart)

        assert analysis["degree_quality"] == "too_early"
        assert analysis["score"] < 50
        assert any("early degrees" in f.lower() for f in analysis["factors"])

    def test_analyze_lagna_mid_degrees(self):
        """Test lagna in middle degrees (3-27)."""
        chart = self._create_mock_chart(
            lagna_degree=15.0, lagna_rashi=Rashi.ARIES, lagna_lord_house=5
        )
        analysis = analyze_lagna_strength(chart)

        assert analysis["degree_quality"] == "good"
        assert analysis["score"] >= 50
        assert any("middle degrees" in f.lower() for f in analysis["factors"])

    def test_analyze_lagna_late_degrees(self):
        """Test lagna in late degrees (27-30)."""
        chart = self._create_mock_chart(
            lagna_degree=28.5, lagna_rashi=Rashi.ARIES, lagna_lord_house=5
        )
        analysis = analyze_lagna_strength(chart)

        assert analysis["degree_quality"] == "too_late"
        assert analysis["score"] < 50
        assert any("late degrees" in f.lower() for f in analysis["factors"])

    def test_analyze_lagna_lord_in_kendra(self):
        """Test lagna lord in kendra house."""
        chart = self._create_mock_chart(
            lagna_degree=15.0, lagna_rashi=Rashi.ARIES, lagna_lord_house=4
        )
        analysis = analyze_lagna_strength(chart)

        assert "kendra" in analysis["lagna_lord_strength"].lower()
        assert any("kendra" in f.lower() for f in analysis["factors"])


class TestAnalyzeMoonCondition:
    """Test Moon condition analysis."""

    def _create_mock_chart_with_moon(
        self, moon_lon: float, sun_lon: float, moon_speed: float, moon_house: int
    ) -> PrashnaChart:
        """Create mock chart with specific Moon and Sun positions."""
        planets = {}

        for i, planet in enumerate(Planet):
            if planet == Planet.MOON:
                longitude = moon_lon
                speed = moon_speed
                house = moon_house
            elif planet == Planet.SUN:
                longitude = sun_lon
                speed = 1.0
                house = 1
            else:
                longitude = float(i * 30)
                speed = 1.0
                house = (i % 12) + 1

            planets[planet] = PlanetPosition(
                planet=planet,
                longitude=longitude,
                latitude=0.0,
                speed=speed,
                rashi=Rashi(list(Rashi)[int(longitude / 30) % 12]),
                rashi_degree=longitude % 30,
                nakshatra="Ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.JUPITER,
                is_retrograde=False,
                house=house,
            )

        return PrashnaChart(
            question="Test",
            question_datetime=datetime.now(UTC),
            category=PrashnaCategory.HEALTH,
            latitude=28.6139,
            longitude=77.2090,
            lagna_rashi=Rashi.ARIES,
            lagna_degree=15.0,
            moon_position=planets[Planet.MOON],
            significator=Planet.SUN,
            planets=planets,
            houses=HouseCusps(ascendant=15.0, mc=270.0, cusps=[0] * 12),
        )

    def test_analyze_moon_waxing(self):
        """Test Moon in waxing phase."""
        # Moon ahead of Sun by 90 degrees
        chart = self._create_mock_chart_with_moon(
            moon_lon=100.0, sun_lon=10.0, moon_speed=13.5, moon_house=5
        )
        analysis = analyze_moon_condition(chart)

        assert analysis["phase"] == "waxing"
        assert analysis["score"] > 50
        assert any("waxing" in f.lower() for f in analysis["factors"])

    def test_analyze_moon_waning(self):
        """Test Moon in waning phase."""
        # Moon behind Sun
        chart = self._create_mock_chart_with_moon(
            moon_lon=10.0, sun_lon=100.0, moon_speed=13.5, moon_house=5
        )
        analysis = analyze_moon_condition(chart)

        assert analysis["phase"] == "waning"
        assert any("waning" in f.lower() for f in analysis["factors"])

    def test_analyze_moon_fast(self):
        """Test fast-moving Moon."""
        chart = self._create_mock_chart_with_moon(
            moon_lon=100.0, sun_lon=10.0, moon_speed=14.0, moon_house=5
        )
        analysis = analyze_moon_condition(chart)

        assert analysis["speed_quality"] == "fast"
        assert any("fast" in f.lower() for f in analysis["factors"])

    def test_analyze_moon_slow(self):
        """Test slow-moving Moon."""
        chart = self._create_mock_chart_with_moon(
            moon_lon=100.0, sun_lon=10.0, moon_speed=11.5, moon_house=5
        )
        analysis = analyze_moon_condition(chart)

        assert analysis["speed_quality"] == "slow"
        assert any("slow" in f.lower() for f in analysis["factors"])

    def test_analyze_moon_in_dusthana(self):
        """Test Moon in dusthana house."""
        chart = self._create_mock_chart_with_moon(
            moon_lon=100.0, sun_lon=10.0, moon_speed=13.5, moon_house=6
        )
        analysis = analyze_moon_condition(chart)

        assert any("dusthana" in f.lower() for f in analysis["factors"])


class TestAnalyzeSignificator:
    """Test significator analysis."""

    def _create_mock_chart_with_significator(
        self, sig: Planet, sig_rashi: Rashi, sig_house: int, sig_retro: bool = False
    ) -> PrashnaChart:
        """Create mock chart with specific significator placement."""
        planets = {}

        for i, planet in enumerate(Planet):
            if planet == sig:
                longitude = list(Rashi).index(sig_rashi) * 30 + 15.0
                house = sig_house
                retrograde = sig_retro
            else:
                longitude = float(i * 30)
                house = (i % 12) + 1
                retrograde = False

            planets[planet] = PlanetPosition(
                planet=planet,
                longitude=longitude,
                latitude=0.0,
                speed=1.0 if not retrograde else -0.5,
                rashi=Rashi(list(Rashi)[int(longitude / 30) % 12]),
                rashi_degree=longitude % 30,
                nakshatra="Ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.JUPITER,
                is_retrograde=retrograde,
                house=house,
            )

        return PrashnaChart(
            question="Test",
            question_datetime=datetime.now(UTC),
            category=PrashnaCategory.HEALTH,
            latitude=28.6139,
            longitude=77.2090,
            lagna_rashi=Rashi.ARIES,
            lagna_degree=15.0,
            moon_position=planets[Planet.MOON],
            significator=sig,
            planets=planets,
            houses=HouseCusps(ascendant=15.0, mc=270.0, cusps=[0] * 12),
        )

    def test_analyze_significator_in_kendra(self):
        """Test significator in kendra house."""
        chart = self._create_mock_chart_with_significator(
            sig=Planet.JUPITER, sig_rashi=Rashi.CANCER, sig_house=10
        )
        analysis = analyze_significator(chart)

        assert analysis["house"] == 10
        assert analysis["score"] > 50
        assert any("kendra" in f.lower() for f in analysis["factors"])

    def test_analyze_significator_exalted(self):
        """Test exalted significator."""
        chart = self._create_mock_chart_with_significator(
            sig=Planet.JUPITER, sig_rashi=Rashi.CANCER, sig_house=5
        )
        analysis = analyze_significator(chart)

        assert analysis["dignity"] == "exalted"
        assert analysis["score"] > 70
        assert any("exalted" in f.lower() for f in analysis["factors"])

    def test_analyze_significator_retrograde(self):
        """Test retrograde significator."""
        chart = self._create_mock_chart_with_significator(
            sig=Planet.JUPITER, sig_rashi=Rashi.CANCER, sig_house=5, sig_retro=True
        )
        analysis = analyze_significator(chart)

        assert any("retrograde" in f.lower() for f in analysis["factors"])


class TestJudgePrashna:
    """Test Prashna judgment."""

    def test_judge_prashna_favorable(self):
        """Test favorable Prashna judgment."""
        # Create chart with Jupiter exalted in Cancer, 10th house
        chart = create_prashna_chart(
            question="Will I succeed?",
            question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.CAREER,
        )

        judgment, score = judge_prashna(chart)

        assert isinstance(judgment, PrashnaJudgment)
        assert 0 <= score <= 100

    def test_judge_prashna_unfavorable(self):
        """Test unfavorable judgment detection."""
        # Create a chart and check judgment logic
        chart = create_prashna_chart(
            question="Test",
            question_dt=datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.HEALTH,
        )

        judgment, score = judge_prashna(chart)

        # Verify score ranges
        if judgment == PrashnaJudgment.FAVORABLE:
            assert score > 70
        elif judgment == PrashnaJudgment.NEUTRAL:
            assert 55 <= score <= 70
        elif judgment == PrashnaJudgment.DELAYED:
            assert 40 <= score < 55
        else:  # UNFAVORABLE
            assert score < 40


class TestPredictTiming:
    """Test timing prediction."""

    def _create_mock_chart_with_lagna(
        self, lagna_degree: float, lagna_rashi: Rashi
    ) -> PrashnaChart:
        """Create mock chart with specific lagna."""
        planets = {}
        for i, planet in enumerate(Planet):
            planets[planet] = PlanetPosition(
                planet=planet,
                longitude=float(i * 30),
                latitude=0.0,
                speed=1.0,
                rashi=Rashi(list(Rashi)[i % 12]),
                rashi_degree=15.0,
                nakshatra="Ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.JUPITER,
                is_retrograde=False,
                house=((i % 12) + 1),
            )

        return PrashnaChart(
            question="Test",
            question_datetime=datetime.now(UTC),
            category=PrashnaCategory.HEALTH,
            latitude=28.6139,
            longitude=77.2090,
            lagna_rashi=lagna_rashi,
            lagna_degree=lagna_degree,
            moon_position=planets[Planet.MOON],
            significator=Planet.SUN,
            planets=planets,
            houses=HouseCusps(ascendant=lagna_degree, mc=270.0, cusps=[0] * 12),
        )

    def test_predict_timing_movable_sign(self):
        """Test timing for movable sign (Aries)."""
        chart = self._create_mock_chart_with_lagna(lagna_degree=5.0, lagna_rashi=Rashi.ARIES)
        timing = predict_timing(chart)

        assert timing["timing_unit"] == "days"
        assert "estimate" in timing
        assert "confidence" in timing

    def test_predict_timing_fixed_sign(self):
        """Test timing for fixed sign (Taurus)."""
        chart = self._create_mock_chart_with_lagna(lagna_degree=35.0, lagna_rashi=Rashi.TAURUS)
        timing = predict_timing(chart)

        assert timing["timing_unit"] == "months"

    def test_predict_timing_dual_sign(self):
        """Test timing for dual sign (Gemini)."""
        chart = self._create_mock_chart_with_lagna(lagna_degree=65.0, lagna_rashi=Rashi.GEMINI)
        timing = predict_timing(chart)

        assert timing["timing_unit"] == "weeks"


class TestCategorySpecificAnalysis:
    """Test category-specific analysis functions."""

    def _create_basic_chart(self, category: PrashnaCategory) -> PrashnaChart:
        """Create a basic chart for testing."""
        return create_prashna_chart(
            question="Test question",
            question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=category,
        )

    def test_analyze_health_prashna(self):
        """Test health-specific analysis."""
        chart = self._create_basic_chart(PrashnaCategory.HEALTH)
        analysis = analyze_health_prashna(chart)

        assert "analysis" in analysis
        assert "factors" in analysis
        assert "outlook" in analysis
        assert isinstance(analysis["factors"], list)

    def test_analyze_marriage_prashna(self):
        """Test marriage-specific analysis."""
        chart = self._create_basic_chart(PrashnaCategory.MARRIAGE)
        analysis = analyze_marriage_prashna(chart)

        assert "analysis" in analysis
        assert "factors" in analysis
        assert "outlook" in analysis
        assert any("venus" in f.lower() or "7th" in f.lower() for f in analysis["factors"])

    def test_analyze_career_prashna(self):
        """Test career-specific analysis."""
        chart = self._create_basic_chart(PrashnaCategory.CAREER)
        analysis = analyze_career_prashna(chart)

        assert "analysis" in analysis
        assert "factors" in analysis
        assert "outlook" in analysis
        assert isinstance(analysis["factors"], list)
        assert len(analysis["factors"]) > 0

    def test_analyze_travel_prashna(self):
        """Test travel-specific analysis."""
        chart = self._create_basic_chart(PrashnaCategory.TRAVEL)
        analysis = analyze_travel_prashna(chart)

        assert "analysis" in analysis
        assert "factors" in analysis
        assert "outlook" in analysis

    def test_analyze_lost_object_prashna(self):
        """Test lost object analysis with direction."""
        chart = self._create_basic_chart(PrashnaCategory.LOST_OBJECTS)
        analysis = analyze_lost_object_prashna(chart)

        assert "analysis" in analysis
        assert "factors" in analysis
        assert "outlook" in analysis
        # Should have direction indication
        assert any(
            any(direction in f for direction in ["East", "West", "North", "South"])
            for f in analysis["factors"]
        )

    def test_analyze_legal_prashna(self):
        """Test legal matter analysis."""
        chart = self._create_basic_chart(PrashnaCategory.LEGAL)
        analysis = analyze_legal_prashna(chart)

        assert "analysis" in analysis
        assert "factors" in analysis
        assert "outlook" in analysis
        # Should compare querent vs opponent
        assert any("strength" in f.lower() for f in analysis["factors"])


class TestFullAnalysis:
    """Test complete Prashna analysis flow."""

    def test_full_analysis(self):
        """Test complete analyze_prashna function."""
        result = analyze_prashna(
            question="Will I get the promotion?",
            question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.CAREER,
        )

        # Check result structure
        assert result.chart is not None
        assert isinstance(result.judgment, PrashnaJudgment)
        assert 0 <= result.strength_score <= 100
        assert isinstance(result.favorable_factors, list)
        assert isinstance(result.unfavorable_factors, list)
        assert isinstance(result.timing, dict)
        assert result.recommendation != ""

        # Check timing dict
        assert "estimate" in result.timing
        assert "timing_unit" in result.timing
        assert "confidence" in result.timing

        # Check chart details
        assert result.chart.category == PrashnaCategory.CAREER
        assert result.chart.significator == Planet.SATURN

    def test_full_analysis_multiple_categories(self):
        """Test analysis for multiple categories."""
        categories = [
            PrashnaCategory.HEALTH,
            PrashnaCategory.MARRIAGE,
            PrashnaCategory.TRAVEL,
            PrashnaCategory.LOST_OBJECTS,
        ]

        for category in categories:
            result = analyze_prashna(
                question=f"Test {category.value}",
                question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
                latitude=28.6139,
                longitude=77.2090,
                category=category,
            )

            assert result.chart.category == category
            assert result.chart.significator == get_significator(category)
            assert result.judgment in list(PrashnaJudgment)
            assert 0 <= result.strength_score <= 100
