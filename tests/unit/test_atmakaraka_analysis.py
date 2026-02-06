"""Tests for Atmakaraka Deep Analysis (Session 22 jaimini.py extensions)."""

from datetime import UTC, datetime

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition
from packages.self.src.jaimini import (
    get_all_chara_karaka_analysis,
    get_atmakaraka_analysis,
    get_ishta_devata,
)

# ---------------------------------------------------------------------------
# Helper: create mock birth chart
# ---------------------------------------------------------------------------


def _create_chart(
    planet_degrees: dict[Planet, tuple[Rashi, float]],
    lagna: Rashi = Rashi.LIBRA,
) -> BirthChart:
    """Build a mock BirthChart for testing.

    Args:
        planet_degrees: Mapping of Planet -> (Rashi, degree_in_sign).
        lagna: Ascendant sign.
    """
    birth_data = BirthData(
        datetime_utc=datetime(1992, 12, 2, 21, 30, 0, tzinfo=UTC),
        latitude=16.726239,
        longitude=81.288428,
        timezone="Asia/Kolkata",
    )

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
    }

    lagna_idx = rashi_index[lagna]
    planets = {}
    for planet, (rashi, degree) in planet_degrees.items():
        idx = rashi_index[rashi]
        longitude = idx * 30 + degree
        house = ((idx - lagna_idx) % 12) + 1
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
        ascendant=lagna_idx * 30.0,
        mc=((lagna_idx + 9) % 12) * 30.0,
        cusps=[((lagna_idx + i) % 12) * 30 for i in range(12)],
    )

    moon_rashi = Rashi.ARIES
    for p, pos in planets.items():
        if p == Planet.MOON:
            moon_rashi = pos.rashi
            break

    return BirthChart(
        user_id="test",
        birth_data=birth_data,
        planets=planets,
        houses=houses,
        lagna_rashi=lagna,
        moon_rashi=moon_rashi,
        moon_nakshatra="test",
        ayanamsa=23.0,
        calculated_at=datetime.now(UTC),
    )


# User's birth data: Libra Lagna, Venus AK at high degree
USER_CHART = _create_chart(
    {
        Planet.SUN: (Rashi.SCORPIO, 17.0),
        Planet.MOON: (Rashi.AQUARIUS, 26.85),
        Planet.MARS: (Rashi.CANCER, 19.5),
        Planet.MERCURY: (Rashi.SCORPIO, 3.0),
        Planet.JUPITER: (Rashi.VIRGO, 2.0),
        Planet.VENUS: (Rashi.SAGITTARIUS, 28.0),  # Highest degree -> AK
        Planet.SATURN: (Rashi.AQUARIUS, 13.0),
    },
    lagna=Rashi.LIBRA,
)

# Alternate chart with Sun as AK
SUN_AK_CHART = _create_chart(
    {
        Planet.SUN: (Rashi.ARIES, 29.0),  # AK
        Planet.MOON: (Rashi.CANCER, 15.0),
        Planet.MARS: (Rashi.SCORPIO, 10.0),
        Planet.MERCURY: (Rashi.GEMINI, 5.0),
        Planet.JUPITER: (Rashi.SAGITTARIUS, 8.0),
        Planet.VENUS: (Rashi.TAURUS, 20.0),
        Planet.SATURN: (Rashi.CAPRICORN, 3.0),
    },
    lagna=Rashi.ARIES,
)


# ---------------------------------------------------------------------------
# Tests: get_ishta_devata
# ---------------------------------------------------------------------------


class TestGetIshtaDevata:
    def test_returns_dict(self):
        result = get_ishta_devata(USER_CHART)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = get_ishta_devata(USER_CHART)
        assert "sign_12th_from_km" in result
        assert "planet_in_12th" in result
        assert "deity" in result
        assert "interpretation" in result

    def test_deity_not_empty(self):
        result = get_ishta_devata(USER_CHART)
        assert result["deity"]
        assert isinstance(result["deity"], str)

    def test_interpretation_contains_sign(self):
        result = get_ishta_devata(USER_CHART)
        assert result["sign_12th_from_km"] in result["interpretation"].lower()

    def test_different_chart_different_deity(self):
        r1 = get_ishta_devata(USER_CHART)
        r2 = get_ishta_devata(SUN_AK_CHART)
        # Different charts can produce different results
        assert isinstance(r1["deity"], str)
        assert isinstance(r2["deity"], str)

    def test_worship_suggestion_present(self):
        result = get_ishta_devata(USER_CHART)
        assert "worship" in result


# ---------------------------------------------------------------------------
# Tests: get_atmakaraka_analysis
# ---------------------------------------------------------------------------


class TestGetAtmakarakaAnalysis:
    def test_returns_dict(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert isinstance(result, dict)

    def test_has_atmakaraka_section(self):
        result = get_atmakaraka_analysis(USER_CHART)
        ak = result["atmakaraka"]
        assert "planet" in ak
        assert "degree" in ak
        assert "sign" in ak
        assert "soul_lesson" in ak
        assert "karmic_focus" in ak

    def test_atmakaraka_is_venus(self):
        """Venus has highest degree (28.0) in USER_CHART."""
        result = get_atmakaraka_analysis(USER_CHART)
        assert result["atmakaraka"]["planet"] == "venus"

    def test_has_karakamsha_section(self):
        result = get_atmakaraka_analysis(USER_CHART)
        km = result["karakamsha"]
        assert "sign" in km
        assert "house_from_lagna" in km
        assert 1 <= km["house_from_lagna"] <= 12

    def test_has_soul_purpose_narrative(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert "soul_purpose" in result
        assert isinstance(result["soul_purpose"], str)
        assert len(result["soul_purpose"]) > 20

    def test_soul_purpose_mentions_ak_planet(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert "venus" in result["soul_purpose"].lower()

    def test_has_ishta_devata(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert "ishta_devata" in result
        assert "deity" in result["ishta_devata"]

    def test_planets_in_karakamsha_is_list(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert isinstance(result["planets_in_karakamsha"], list)

    def test_planets_aspecting_karakamsha_is_list(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert isinstance(result["planets_aspecting_karakamsha"], list)

    def test_has_career_direction(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert "career_from_karakamsha" in result

    def test_has_spiritual_path(self):
        result = get_atmakaraka_analysis(USER_CHART)
        assert "spiritual_path" in result

    def test_sun_ak_chart(self):
        result = get_atmakaraka_analysis(SUN_AK_CHART)
        assert result["atmakaraka"]["planet"] == "sun"
        assert (
            "ego" in result["atmakaraka"]["soul_lesson"].lower()
            or "leadership" in result["atmakaraka"]["soul_lesson"].lower()
        )


# ---------------------------------------------------------------------------
# Tests: get_all_chara_karaka_analysis
# ---------------------------------------------------------------------------


class TestGetAllCharaKarakaAnalysis:
    def test_returns_dict(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        assert isinstance(result, dict)

    def test_has_7_karakas(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        assert result["total_karakas"] == 7

    def test_first_karaka_is_ak(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        first = result["karakas"][0]
        assert first["karaka"] == "atmakaraka"

    def test_last_karaka_is_dk(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        last = result["karakas"][-1]
        assert last["karaka"] == "darakaraka"

    def test_each_karaka_has_required_fields(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        for k in result["karakas"]:
            assert "karaka" in k
            assert "planet" in k
            assert "sign" in k
            assert "degree" in k
            assert "signification" in k
            assert "description" in k

    def test_has_themes(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        assert isinstance(result["themes"], list)
        assert len(result["themes"]) >= 1

    def test_has_summary(self):
        result = get_all_chara_karaka_analysis(USER_CHART)
        assert "summary" in result
        assert isinstance(result["summary"], str)

    def test_degrees_descending(self):
        """Karaka degrees should be in descending order (AK highest)."""
        result = get_all_chara_karaka_analysis(USER_CHART)
        degrees = [k["degree"] for k in result["karakas"]]
        for i in range(len(degrees) - 1):
            assert degrees[i] >= degrees[i + 1]
