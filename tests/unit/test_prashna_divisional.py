"""Unit tests for Prashna D9 (Navamsha) and D3 (Drekkana) divisional analysis."""

from datetime import UTC, datetime

from packages.core.src.constants import Planet, PrashnaCategory, Rashi
from packages.core.src.models import HouseCusps, PlanetPosition, PrashnaChart
from packages.self.src.prashna import (
    analyze_prashna,
    create_prashna_chart,
    get_prashna_divisional_analysis,
)


def _make_mock_prashna_chart(
    lagna_degree: float = 15.0,
    lagna_rashi: Rashi = Rashi.ARIES,
    planet_overrides: dict | None = None,
) -> PrashnaChart:
    """Create a mock Prashna chart for testing divisional analysis.

    Args:
        lagna_degree: Ascendant longitude (0-360)
        lagna_rashi: Ascendant sign
        planet_overrides: Dict of {Planet: (longitude, house)} overrides

    Returns:
        PrashnaChart for testing
    """
    planets = {}
    base_longitudes = {
        Planet.SUN: 45.0,
        Planet.MOON: 100.0,
        Planet.MARS: 15.0,
        Planet.MERCURY: 130.0,
        Planet.JUPITER: 250.0,
        Planet.VENUS: 200.0,
        Planet.SATURN: 320.0,
        Planet.RAHU: 80.0,
        Planet.KETU: 260.0,
    }

    for planet in Planet:
        lon = base_longitudes.get(planet, 0.0)
        house = (int(lon / 30) % 12) + 1

        if planet_overrides and planet in planet_overrides:
            lon, house = planet_overrides[planet]

        planets[planet] = PlanetPosition(
            planet=planet,
            longitude=lon,
            latitude=0.0,
            speed=1.0 if planet != Planet.MOON else 13.5,
            rashi=Rashi(list(Rashi)[int(lon / 30) % 12]),
            rashi_degree=lon % 30,
            nakshatra="Ashwini",
            nakshatra_pada=1,
            nakshatra_lord=Planet.KETU,
            is_retrograde=False,
            house=house,
        )

    return PrashnaChart(
        question="Test Prashna question",
        question_datetime=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
        category=PrashnaCategory.CAREER,
        latitude=28.6139,
        longitude=77.2090,
        lagna_rashi=lagna_rashi,
        lagna_degree=lagna_degree,
        moon_position=planets[Planet.MOON],
        significator=Planet.SATURN,
        planets=planets,
        houses=HouseCusps(ascendant=lagna_degree, mc=270.0, cusps=[0] * 12),
    )


class TestPrashnaDivisionalAnalysis:
    """Test the get_prashna_divisional_analysis entry point."""

    def test_returns_both_analyses(self):
        """Divisional analysis returns both navamsha and drekkana sub-dicts."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)

        assert "navamsha_analysis" in result
        assert "drekkana_analysis" in result
        assert isinstance(result["navamsha_analysis"], dict)
        assert isinstance(result["drekkana_analysis"], dict)

    def test_navamsha_has_required_fields(self):
        """Navamsha analysis contains all required keys."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)
        nav = result["navamsha_analysis"]

        assert "d9_lagna_sign" in nav
        assert "strength_score" in nav
        assert "benefics_in_d9_lagna" in nav
        assert "malefics_in_d9_lagna" in nav
        assert "factors" in nav
        assert "interpretation" in nav

    def test_drekkana_has_required_fields(self):
        """Drekkana analysis contains all required keys."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert "drekkana_number" in drek
        assert "effort_level" in drek
        assert "effort_description" in drek
        assert "d3_lagna_sign" in drek
        assert "strength_score" in drek
        assert "factors" in drek

    def test_with_real_chart(self):
        """Test divisional analysis with a real ephemeris chart."""
        chart = create_prashna_chart(
            question="Will I get the job?",
            question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.CAREER,
        )
        result = get_prashna_divisional_analysis(chart)

        assert result["navamsha_analysis"]["strength_score"] >= 0
        assert result["navamsha_analysis"]["strength_score"] <= 100
        assert result["drekkana_analysis"]["drekkana_number"] in (1, 2, 3)


class TestPrashnaNavamshaAnalysis:
    """Test _analyze_prashna_navamsha D9 analysis."""

    def test_strength_score_range(self):
        """D9 strength score is in 0-100 range."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)
        nav = result["navamsha_analysis"]

        assert 0 <= nav["strength_score"] <= 100

    def test_d9_lagna_sign_present(self):
        """D9 lagna sign is a valid string."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)

        assert isinstance(result["navamsha_analysis"]["d9_lagna_sign"], str)
        assert len(result["navamsha_analysis"]["d9_lagna_sign"]) > 0

    def test_benefics_malefics_are_lists(self):
        """Benefics and malefics in D9 lagna are proper lists."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)
        nav = result["navamsha_analysis"]

        assert isinstance(nav["benefics_in_d9_lagna"], list)
        assert isinstance(nav["malefics_in_d9_lagna"], list)

    def test_factors_non_empty(self):
        """D9 analysis always produces at least one factor."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)

        assert len(result["navamsha_analysis"]["factors"]) >= 1

    def test_interpretation_present(self):
        """D9 analysis includes an interpretation string."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)
        nav = result["navamsha_analysis"]

        assert isinstance(nav["interpretation"], str)
        assert len(nav["interpretation"]) > 10


class TestPrashnaDrekkanaAnalysis:
    """Test _analyze_prashna_drekkana D3 analysis."""

    def test_first_drekkana_self_effort(self):
        """Lagna at 5 degrees (first drekkana) -> self_effort."""
        chart = _make_mock_prashna_chart(lagna_degree=5.0, lagna_rashi=Rashi.ARIES)
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert drek["drekkana_number"] == 1
        assert drek["effort_level"] == "self_effort"

    def test_second_drekkana_needs_help(self):
        """Lagna at 15 degrees (second drekkana) -> needs_help."""
        chart = _make_mock_prashna_chart(lagna_degree=15.0, lagna_rashi=Rashi.ARIES)
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert drek["drekkana_number"] == 2
        assert drek["effort_level"] == "needs_help"

    def test_third_drekkana_very_difficult(self):
        """Lagna at 25 degrees (third drekkana) -> very_difficult."""
        chart = _make_mock_prashna_chart(lagna_degree=25.0, lagna_rashi=Rashi.ARIES)
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert drek["drekkana_number"] == 3
        assert drek["effort_level"] == "very_difficult"

    def test_drekkana_boundary_at_10_degrees(self):
        """Lagna at exactly 10.0 degrees is second drekkana."""
        chart = _make_mock_prashna_chart(lagna_degree=10.0, lagna_rashi=Rashi.ARIES)
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert drek["drekkana_number"] == 2
        assert drek["effort_level"] == "needs_help"

    def test_drekkana_boundary_at_20_degrees(self):
        """Lagna at exactly 20.0 degrees is third drekkana."""
        chart = _make_mock_prashna_chart(lagna_degree=20.0, lagna_rashi=Rashi.ARIES)
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert drek["drekkana_number"] == 3
        assert drek["effort_level"] == "very_difficult"

    def test_drekkana_edge_zero_degrees(self):
        """Lagna at 0.0 degrees is first drekkana."""
        chart = _make_mock_prashna_chart(lagna_degree=0.0, lagna_rashi=Rashi.ARIES)
        result = get_prashna_divisional_analysis(chart)
        drek = result["drekkana_analysis"]

        assert drek["drekkana_number"] == 1
        assert drek["effort_level"] == "self_effort"

    def test_drekkana_for_different_signs(self):
        """Drekkana analysis works for different lagna signs."""
        for sign_idx, rashi in enumerate(Rashi):
            if sign_idx >= 4:
                break  # Test first 4 signs
            degree = sign_idx * 30 + 5.0  # First drekkana of each sign
            chart = _make_mock_prashna_chart(lagna_degree=degree, lagna_rashi=rashi)
            result = get_prashna_divisional_analysis(chart)
            drek = result["drekkana_analysis"]

            assert drek["drekkana_number"] == 1
            assert drek["effort_level"] == "self_effort"

    def test_drekkana_strength_score_range(self):
        """D3 strength score is in 0-100 range."""
        chart = _make_mock_prashna_chart()
        result = get_prashna_divisional_analysis(chart)

        assert 0 <= result["drekkana_analysis"]["strength_score"] <= 100

    def test_effort_description_is_meaningful(self):
        """Effort description is a non-empty string."""
        chart = _make_mock_prashna_chart(lagna_degree=5.0)
        result = get_prashna_divisional_analysis(chart)

        desc = result["drekkana_analysis"]["effort_description"]
        assert isinstance(desc, str)
        assert len(desc) > 20


class TestAnalyzePrashnaIncludesDivisional:
    """Test that the main analyze_prashna function includes divisional analysis."""

    def test_analyze_prashna_has_navamsha(self):
        """Full analysis result includes navamsha_analysis field."""
        result = analyze_prashna(
            question="Will I succeed?",
            question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.CAREER,
        )

        assert result.navamsha_analysis is not None
        assert "d9_lagna_sign" in result.navamsha_analysis
        assert "strength_score" in result.navamsha_analysis

    def test_analyze_prashna_has_drekkana(self):
        """Full analysis result includes drekkana_analysis field."""
        result = analyze_prashna(
            question="Will I succeed?",
            question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
            latitude=28.6139,
            longitude=77.2090,
            category=PrashnaCategory.CAREER,
        )

        assert result.drekkana_analysis is not None
        assert "drekkana_number" in result.drekkana_analysis
        assert "effort_level" in result.drekkana_analysis

    def test_multiple_categories_include_divisional(self):
        """Divisional analysis is present for all question categories."""
        for category in [
            PrashnaCategory.HEALTH,
            PrashnaCategory.MARRIAGE,
            PrashnaCategory.CAREER,
        ]:
            result = analyze_prashna(
                question=f"Test {category.value}",
                question_dt=datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC),
                latitude=28.6139,
                longitude=77.2090,
                category=category,
            )

            assert result.navamsha_analysis is not None
            assert result.drekkana_analysis is not None
