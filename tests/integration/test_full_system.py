"""Comprehensive integration test exercising ALL 5 layers with real birth data.

Birth Data:
- DateTime: 1992-12-03T03:00:00+05:30 (UTC: 1992-12-02T21:30:00)
- Location: lat 16.726239, lon 81.288428
- Known facts: Lagna=Libra, Moon=Aquarius (~324.11°), Purva Bhadrapada Pada 2,
  Mercury Mahadasha (2022-2039)

Tests flow through all 5 layers:
  COSMOS → SELF → CONTEXT → (GUIDE + MEMORY tested separately)
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from packages.context.src import (  # noqa: E402
    calculate_narayana_sequence,
    calculate_yogini_sequence,
    get_current_dasha,
    get_current_narayana_dasha,
    get_current_yogini_dasha,
    get_mahadasha_sequence,
)
from packages.core.src.constants import Planet, PrashnaCategory, Rashi  # noqa: E402
from packages.core.src.models import (  # noqa: E402
    BirthChart,
    BirthData,
    HouseCusps,
    PlanetPosition,
)
from packages.cosmos.src import (  # noqa: E402
    get_all_planets,
    get_all_vimshopaka,
    get_ayanamsa,
    get_house_cusps,
    get_julian_day,
    get_sunrise_sunset,
    longitude_to_nakshatra,
)
from packages.cosmos.src.upagrahas import calculate_all_upagrahas  # noqa: E402
from packages.self.src import (  # noqa: E402
    DoshaDetector,
    YogaDetector,
    analyze_prashna,
    calculate_all_arudha_padas,
    calculate_chara_karakas,
    get_karakamsha,
)

# ===========================================================================
# Constants for the test subject
# ===========================================================================
BIRTH_DT_UTC = datetime(1992, 12, 2, 21, 30, 0)  # IST 03:00 → UTC 21:30
LATITUDE = 16.726239
LONGITUDE = 81.288428
TIMEZONE = "Asia/Kolkata"

# Rashi list for index-based lookups
RASHI_LIST = list(Rashi)


def _build_birth_chart(
    planets_raw: dict,
    houses_raw: dict,
    jd: float,
) -> BirthChart:
    """Convert raw ephemeris dicts into a full BirthChart pydantic model.

    This mirrors the pattern used in packages/guide/src/agent.py lines 620-696.
    """
    ayanamsa = get_ayanamsa(jd)
    ascendant_lon = houses_raw["ascendant"]
    lagna_rashi_idx = int(ascendant_lon // 30)
    lagna_rashi = RASHI_LIST[lagna_rashi_idx]

    planet_positions: dict[Planet, PlanetPosition] = {}

    for name, data in planets_raw.items():
        planet_enum = Planet(name.lower())
        lon = data["longitude"]
        rashi_idx = int(lon // 30)
        rashi_enum = RASHI_LIST[rashi_idx]

        nak = longitude_to_nakshatra(lon)
        nak_name = nak["name"]
        nak_pada = nak["pada"]
        nak_lord_str = nak["lord"]

        try:
            nak_lord = Planet(nak_lord_str.lower())
        except ValueError:
            nak_lord = planet_enum

        house = ((rashi_idx - lagna_rashi_idx) % 12) + 1

        planet_positions[planet_enum] = PlanetPosition(
            planet=planet_enum,
            longitude=lon,
            latitude=data.get("latitude", 0.0),
            speed=data.get("speed", 0.0),
            rashi=rashi_enum,
            rashi_degree=lon % 30,
            nakshatra=nak_name,
            nakshatra_pada=max(1, min(4, nak_pada)),
            nakshatra_lord=nak_lord,
            is_retrograde=data.get("speed", 0.0) < 0,
            house=house,
        )

    moon_pos = planet_positions[Planet.MOON]

    return BirthChart(
        user_id="integration-test-user",
        birth_data=BirthData(
            datetime_utc=BIRTH_DT_UTC,
            latitude=LATITUDE,
            longitude=LONGITUDE,
            timezone=TIMEZONE,
        ),
        planets=planet_positions,
        houses=HouseCusps(
            ascendant=houses_raw["ascendant"],
            mc=houses_raw["mc"],
            cusps=houses_raw["cusps"],
        ),
        lagna_rashi=lagna_rashi,
        moon_rashi=moon_pos.rashi,
        moon_nakshatra=moon_pos.nakshatra,
        ayanamsa=ayanamsa,
        calculated_at=datetime.now(),
    )


class TestFullSystemWithBirthData:
    """End-to-end system test with real birth data: 1992-12-03T03:00+05:30."""

    # -----------------------------------------------------------------------
    # Shared fixtures — compute expensive ephemeris data ONCE
    # -----------------------------------------------------------------------
    @pytest.fixture(scope="class")
    def jd(self) -> float:
        return get_julian_day(BIRTH_DT_UTC)

    @pytest.fixture(scope="class")
    def planets_raw(self, jd: float) -> dict:
        return get_all_planets(jd)

    @pytest.fixture(scope="class")
    def houses_raw(self, jd: float) -> dict:
        return get_house_cusps(jd, LATITUDE, LONGITUDE)

    @pytest.fixture(scope="class")
    def birth_chart(self, planets_raw: dict, houses_raw: dict, jd: float) -> BirthChart:
        return _build_birth_chart(planets_raw, houses_raw, jd)

    # ===================================================================
    # COSMOS LAYER
    # ===================================================================

    def test_ephemeris_positions(self, planets_raw: dict):
        """Verify planet positions — Moon must be in Aquarius ~324.11°."""
        assert len(planets_raw) == 9, "Should have 9 Vedic planets"

        moon = planets_raw["moon"]
        moon_lon = moon["longitude"]

        # Moon at ~324.11° → Aquarius (300-330°)
        assert 300 <= moon_lon < 330, f"Moon should be in Aquarius (300-330°), got {moon_lon:.2f}°"
        # Allow ±1° tolerance for ayanamsa variations
        assert abs(moon_lon - 324.11) < 1.0, f"Moon should be near 324.11°, got {moon_lon:.2f}°"

        # All 9 planets present
        expected_planets = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        }
        assert set(planets_raw.keys()) == expected_planets

    def test_house_cusps(self, houses_raw: dict):
        """Verify Libra lagna (ascendant in 180-210° range)."""
        asc = houses_raw["ascendant"]
        # Libra = 180° to 210°
        assert 180 <= asc < 210, f"Ascendant should be in Libra (180-210°), got {asc:.2f}°"
        assert len(houses_raw["cusps"]) == 12, "Should have 12 house cusps"
        assert "mc" in houses_raw, "Should have MC (Midheaven)"

    def test_sunrise_sunset(self):
        """Sunrise/sunset for birth location and date are reasonable."""
        result = get_sunrise_sunset(BIRTH_DT_UTC, LATITUDE, LONGITUDE)

        sunrise = result["sunrise"]
        sunset = result["sunset"]
        day_hours = result["day_duration_hours"]

        # Sunrise should be between 0:00-6:00 UTC (≈5:30-11:30 IST) for this location
        assert 0 <= sunrise.hour <= 6, f"Sunrise hour UTC should be 0-6, got {sunrise.hour}"
        # Sunset should be between 11:00-13:00 UTC (≈16:30-18:30 IST)
        assert 11 <= sunset.hour <= 14, f"Sunset hour UTC should be 11-14, got {sunset.hour}"
        # Day duration around 11-12 hours for December in south India
        assert 10.5 <= day_hours <= 12.5, f"Day duration should be ~11h, got {day_hours}"

    def test_upagrahas(self, planets_raw: dict, houses_raw: dict):
        """All 11 upagrahas should have valid positions."""
        sun_lon = planets_raw["sun"]["longitude"]
        lagna_lon = houses_raw["ascendant"]

        analysis = calculate_all_upagrahas(
            birth_dt=BIRTH_DT_UTC,
            latitude=LATITUDE,
            longitude=LONGITUDE,
            lagna_longitude=lagna_lon,
            sun_longitude=sun_lon,
        )

        # Should have 11 upagraha positions
        assert (
            len(analysis.positions) == 11
        ), f"Expected 11 upagrahas, got {len(analysis.positions)}"

        # All longitudes should be in valid range
        for name, pos in analysis.positions.items():
            assert (
                0 <= pos.longitude < 360
            ), f"Upagraha {name} longitude {pos.longitude} out of range"
            assert 1 <= pos.house <= 12, f"Upagraha {name} house {pos.house} out of range"

        # Day duration should be reasonable
        assert 10.0 <= analysis.day_duration_hours <= 14.0

    # ===================================================================
    # SELF LAYER
    # ===================================================================

    def test_yoga_detection(self, birth_chart: BirthChart):
        """Detect yogas from real chart — expect at least 1."""
        detector = YogaDetector()
        yogas = detector.detect_all_yogas(birth_chart)

        assert len(yogas) >= 1, "Should detect at least 1 yoga in a real chart"

        # Each yoga should have required fields
        for yoga in yogas:
            assert yoga.name, "Yoga must have a name"
            assert yoga.yoga_id, "Yoga must have an ID"
            assert yoga.is_present is True

    def test_dosha_detection(self, birth_chart: BirthChart):
        """Detect doshas from real chart — should return a list."""
        detector = DoshaDetector()
        doshas = detector.detect_all(birth_chart)

        # May or may not have doshas, but should be a valid list
        assert isinstance(doshas, list)

        for dosha in doshas:
            assert dosha.name, "Dosha must have a name"
            assert dosha.dosha_id, "Dosha must have an ID"

    def test_jaimini_system(self, birth_chart: BirthChart):
        """Chara Karakas, Arudha Padas, and Karakamsha from real chart."""
        # Chara Karakas: 7 planets ranked by degree
        karakas = calculate_chara_karakas(birth_chart)
        assert len(karakas) == 7, f"Expected 7 Chara Karakas, got {len(karakas)}"

        # First karaka should be Atmakaraka (highest degree)
        assert karakas[0].karaka.value == "atmakaraka"
        # Last should be Darakaraka (lowest degree)
        assert karakas[6].karaka.value == "darakaraka"

        # Arudha Padas: 12 (one per house)
        arudhas = calculate_all_arudha_padas(birth_chart)
        assert len(arudhas) == 12, f"Expected 12 Arudha Padas, got {len(arudhas)}"
        for ap in arudhas:
            assert 1 <= ap.house_number <= 12

        # Karakamsha
        karakamsha = get_karakamsha(birth_chart)
        assert karakamsha.atmakaraka in list(Planet)
        assert karakamsha.navamsha_rashi in list(Rashi)

    def test_prashna_chart(self):
        """Create and analyze a Prashna chart at birth location."""
        # Use a fixed time for reproducibility
        question_dt = datetime(2026, 1, 15, 10, 0, 0)  # UTC

        result = analyze_prashna(
            question="Will I succeed in my career change?",
            question_dt=question_dt,
            latitude=LATITUDE,
            longitude=LONGITUDE,
            category=PrashnaCategory.CAREER,
        )

        assert result.chart.question == "Will I succeed in my career change?"
        assert result.chart.category == PrashnaCategory.CAREER
        assert result.chart.lagna_rashi in list(Rashi)
        assert 0 <= result.strength_score <= 100
        assert result.judgment is not None
        assert len(result.chart.planets) == 9

    # ===================================================================
    # CONTEXT LAYER
    # ===================================================================

    def test_vimshottari_dasha(self, birth_chart: BirthChart):
        """Current MD should be Mercury (2022-2039)."""
        moon_lon = birth_chart.planets[Planet.MOON].longitude

        current = get_current_dasha(BIRTH_DT_UTC, moon_lon)
        assert current is not None, "Should return current dasha"

        md_lord = current["mahadasha"]["lord"]
        assert md_lord == "mercury", f"Current Mahadasha should be Mercury, got {md_lord}"

        # Verify the sequence includes Mercury
        sequence = get_mahadasha_sequence(BIRTH_DT_UTC, moon_lon)
        assert len(sequence) >= 9, "Should have at least 9 mahadasha periods"
        lords = [p["lord"] for p in sequence]
        assert "mercury" in lords, "Mercury should be in the mahadasha sequence"

    def test_yogini_dasha(self, birth_chart: BirthChart):
        """Yogini dasha from Moon nakshatra/pada returns valid current period."""
        moon_pos = birth_chart.planets[Planet.MOON]
        nak = longitude_to_nakshatra(moon_pos.longitude)
        nak_num = nak["number"]
        pada = nak["pada"]
        deg_in_nak = nak["degree_in_nakshatra"]

        # Get current Yogini dasha
        current = get_current_yogini_dasha(
            birth_dt=BIRTH_DT_UTC,
            nakshatra_num=nak_num,
            pada=pada,
            degree_in_nakshatra=deg_in_nak,
        )

        assert "yogini" in current, "Should have 'yogini' key"
        assert "lord" in current, "Should have 'lord' key"
        assert "start_date" in current, "Should have start_date"
        assert "end_date" in current, "Should have end_date"

        # Generate full sequence
        sequence = calculate_yogini_sequence(
            birth_dt=BIRTH_DT_UTC,
            nakshatra_num=nak_num,
            pada=pada,
            degree_in_nakshatra=deg_in_nak,
        )
        assert len(sequence) >= 8, "Should have at least 8 yogini periods per cycle"

    def test_narayana_dasha(self, birth_chart: BirthChart):
        """Narayana dasha starts from lagna (Libra)."""
        sequence = calculate_narayana_sequence(BIRTH_DT_UTC, birth_chart)
        assert len(sequence) >= 12, "Should have at least 12 periods"

        # First period should start from lagna rashi (Libra)
        assert (
            sequence[0].rashi == Rashi.LIBRA
        ), f"First Narayana dasha should be Libra (lagna), got {sequence[0].rashi}"

        # Get current period
        current = get_current_narayana_dasha(BIRTH_DT_UTC, birth_chart)
        assert "rashi" in current, "Should have current rashi"
        assert "start_date" in current, "Should have start_date"
        assert "end_date" in current, "Should have end_date"

    def test_vimshopaka_strength(self, planets_raw: dict):
        """Vimshopaka strength for all planets."""
        # Build planet longitudes dict
        planet_longs = {name: data["longitude"] for name, data in planets_raw.items()}

        result = get_all_vimshopaka(planet_longs)

        assert len(result) == 9, f"Expected 9 planets, got {len(result)}"

        for planet_name, strength_data in result.items():
            assert "total_points" in strength_data, f"Planet {planet_name} missing total_points"
            score = strength_data["total_points"]
            # Vimshopaka total_points depends on scheme (shad_varga max=120)
            assert 0 <= score <= 120, f"Planet {planet_name} score {score} out of range 0-120"
            assert "percentage" in strength_data, f"Planet {planet_name} missing percentage"
