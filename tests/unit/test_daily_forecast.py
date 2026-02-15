"""Tests for the Daily Forecast Engine.

Tests cover:
- Panchanga quality scoring
- Aspect quality scoring
- Moon BAV quality mapping
- Day rating computation
- Recommendation generation
- Daily summary generation
- Dasha theme generation
- Full daily forecast integration (mocked ephemeris)
"""

from datetime import datetime
from unittest.mock import patch

from packages.context.src.daily_forecast import (
    AREA_HOUSES,
    AREA_PLANETS,
    RASHI_NAMES,
    WEEKDAY_NAMES,
    _aspect_quality_score,
    _compute_day_rating,
    _dasha_theme,
    _generate_daily_summary,
    _generate_recommendations,
    _get_rashi_index,
    _house_from_lagna,
    _moon_bav_to_quality,
    _panchanga_quality_score,
    get_daily_forecast,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NATAL_PLANETS = {
    "sun": {"longitude": 227.5, "rashi": 7},
    "moon": {"longitude": 326.85, "rashi": 10},
    "mars": {"longitude": 100.2, "rashi": 3},
    "mercury": {"longitude": 243.1, "rashi": 8},
    "jupiter": {"longitude": 120.0, "rashi": 4},
    "venus": {"longitude": 210.5, "rashi": 7},
    "saturn": {"longitude": 310.0, "rashi": 10},
    "rahu": {"longitude": 170.0, "rashi": 5},
    "ketu": {"longitude": 350.0, "rashi": 11},
}


# ---------------------------------------------------------------------------
# _get_rashi_index tests
# ---------------------------------------------------------------------------


class TestGetRashiIndex:
    def test_known_rashi(self):
        assert _get_rashi_index("aries") == 0
        assert _get_rashi_index("libra") == 6
        assert _get_rashi_index("pisces") == 11

    def test_case_insensitive(self):
        assert _get_rashi_index("Aries") == 0
        assert _get_rashi_index("LIBRA") == 6

    def test_unknown_returns_zero(self):
        assert _get_rashi_index("invalid") == 0


# ---------------------------------------------------------------------------
# _house_from_lagna tests
# ---------------------------------------------------------------------------


class TestHouseFromLagna:
    def test_same_sign(self):
        assert _house_from_lagna(6, 6) == 1

    def test_adjacent_sign(self):
        assert _house_from_lagna(7, 6) == 2

    def test_wrap_around(self):
        assert _house_from_lagna(0, 11) == 2

    def test_opposite(self):
        assert _house_from_lagna(0, 6) == 7


# ---------------------------------------------------------------------------
# _panchanga_quality_score tests
# ---------------------------------------------------------------------------


class TestPanchangaQualityScore:
    def test_empty_returns_baseline(self):
        score = _panchanga_quality_score({})
        assert 4.0 <= score <= 6.0

    def test_shukla_paksha_boost(self):
        p = {"tithi": {"paksha": "Shukla", "number": 5, "name": "Panchami"}}
        score = _panchanga_quality_score(p)
        assert score > 5.0

    def test_krishna_paksha_penalty(self):
        p = {"tithi": {"paksha": "Krishna", "number": 8, "name": "Ashtami"}}
        score = _panchanga_quality_score(p)
        assert score < 5.0

    def test_good_yoga_boost(self):
        p = {"yoga": {"name": "Siddha"}}
        score = _panchanga_quality_score(p)
        assert score > 5.0

    def test_bad_yoga_penalty(self):
        p = {"yoga": {"name": "Vishkumbha"}}
        score = _panchanga_quality_score(p)
        assert score < 5.0

    def test_good_vara_boost(self):
        p = {"vara": {"name": "Thursday"}}
        score = _panchanga_quality_score(p)
        assert score > 5.0

    def test_bad_vara_penalty(self):
        p = {"vara": {"name": "Saturday"}}
        score = _panchanga_quality_score(p)
        assert score < 5.0

    def test_good_karana_boost(self):
        p = {"karana": {"name": "Bava"}}
        score = _panchanga_quality_score(p)
        assert score >= 5.0

    def test_combined_positive(self):
        p = {
            "tithi": {"paksha": "Shukla", "number": 5, "name": "Panchami"},
            "yoga": {"name": "Siddhi"},
            "vara": {"name": "Thursday"},
            "karana": {"name": "Balava"},
        }
        score = _panchanga_quality_score(p)
        assert score >= 7.0

    def test_combined_negative(self):
        p = {
            "tithi": {"paksha": "Krishna", "number": 8, "name": "Ashtami"},
            "yoga": {"name": "Vyatipata"},
            "vara": {"name": "Saturday"},
        }
        score = _panchanga_quality_score(p)
        assert score <= 3.5

    def test_score_clamped_to_range(self):
        # Even extreme values should stay in 0-10
        p = {
            "tithi": {"paksha": "Shukla", "number": 5, "name": "Panchami"},
            "yoga": {"name": "Siddhi"},
            "vara": {"name": "Thursday"},
            "karana": {"name": "Bava"},
        }
        score = _panchanga_quality_score(p)
        assert 0.0 <= score <= 10.0


# ---------------------------------------------------------------------------
# _aspect_quality_score tests
# ---------------------------------------------------------------------------


class TestAspectQualityScore:
    def test_no_aspects_returns_baseline(self):
        assert _aspect_quality_score([]) == 5.0

    def test_benefic_trine_boosts(self):
        aspects = [
            {"aspect_type": "trine", "transit_planet": "jupiter", "orb": 1.0},
        ]
        score = _aspect_quality_score(aspects)
        assert score > 5.0

    def test_malefic_square_penalizes(self):
        aspects = [
            {"aspect_type": "square", "transit_planet": "saturn", "orb": 1.0},
        ]
        score = _aspect_quality_score(aspects)
        assert score < 5.0

    def test_tight_orb_stronger(self):
        tight = [{"aspect_type": "trine", "transit_planet": "jupiter", "orb": 0.5}]
        loose = [{"aspect_type": "trine", "transit_planet": "jupiter", "orb": 7.0}]
        assert _aspect_quality_score(tight) > _aspect_quality_score(loose)

    def test_score_clamped(self):
        aspects = [
            {"aspect_type": "square", "transit_planet": "saturn", "orb": 0.1},
            {"aspect_type": "square", "transit_planet": "mars", "orb": 0.1},
            {"aspect_type": "opposition", "transit_planet": "rahu", "orb": 0.1},
            {"aspect_type": "opposition", "transit_planet": "ketu", "orb": 0.1},
        ]
        score = _aspect_quality_score(aspects)
        assert 0.0 <= score <= 10.0


# ---------------------------------------------------------------------------
# _moon_bav_to_quality tests
# ---------------------------------------------------------------------------


class TestMoonBavToQuality:
    def test_high_score(self):
        assert _moon_bav_to_quality(6) == "favorable"
        assert _moon_bav_to_quality(8) == "favorable"

    def test_neutral_score(self):
        assert _moon_bav_to_quality(4) == "neutral"

    def test_low_score(self):
        assert _moon_bav_to_quality(3) == "unfavorable"

    def test_very_low_score(self):
        assert _moon_bav_to_quality(1) == "very_unfavorable"
        assert _moon_bav_to_quality(0) == "very_unfavorable"


# ---------------------------------------------------------------------------
# _compute_day_rating tests
# ---------------------------------------------------------------------------


class TestComputeDayRating:
    def test_all_neutral_gives_middling(self):
        rating = _compute_day_rating(5.0, 4, 5.0, 0.0)
        assert 4 <= rating <= 6

    def test_all_excellent_gives_high(self):
        rating = _compute_day_rating(9.0, 7, 9.0, 1.5)
        assert rating >= 7

    def test_all_poor_gives_low(self):
        rating = _compute_day_rating(1.0, 1, 1.0, -1.0)
        assert rating <= 3

    def test_clamped_to_1_10(self):
        r1 = _compute_day_rating(0.0, 0, 0.0, -5.0)
        r2 = _compute_day_rating(10.0, 8, 10.0, 5.0)
        assert r1 >= 1
        assert r2 <= 10


# ---------------------------------------------------------------------------
# _generate_recommendations tests
# ---------------------------------------------------------------------------


class TestGenerateRecommendations:
    def test_returns_required_keys(self):
        rec = _generate_recommendations({}, 5, "thursday", 7.0, 1.0)
        assert "best_for" in rec
        assert "avoid" in rec
        assert "tip" in rec

    def test_thursday_includes_education(self):
        rec = _generate_recommendations({}, 1, "thursday", 5.0, 0.0)
        assert "education" in rec["best_for"]

    def test_saturday_includes_avoid_new_ventures(self):
        rec = _generate_recommendations({}, 1, "saturday", 5.0, 0.0)
        assert "new_ventures" in rec["avoid"]

    def test_high_aspect_quality_recommends_major_decisions(self):
        rec = _generate_recommendations({}, 1, "wednesday", 8.0, 0.0)
        assert "major_decisions" in rec["best_for"]

    def test_moon_in_trikona_recommends_spiritual(self):
        rec = _generate_recommendations({}, 9, "monday", 5.0, 0.0)
        assert "spiritual" in rec["best_for"]


# ---------------------------------------------------------------------------
# _generate_daily_summary tests
# ---------------------------------------------------------------------------


class TestGenerateDailySummary:
    def test_high_rating_positive_tone(self):
        s = _generate_daily_summary(9, "gemini", 9, "mercury", "venus")
        assert "highly positive" in s.lower()

    def test_low_rating_challenging_tone(self):
        s = _generate_daily_summary(2, "capricorn", 4, "saturn", "rahu")
        assert "challenging" in s.lower()

    def test_contains_moon_sign(self):
        s = _generate_daily_summary(6, "cancer", 10, "jupiter", "moon")
        assert "Cancer" in s

    def test_contains_dasha_lords(self):
        s = _generate_daily_summary(6, "aries", 1, "mercury", "ketu")
        assert "Mercury" in s
        assert "Ketu" in s


# ---------------------------------------------------------------------------
# _dasha_theme tests
# ---------------------------------------------------------------------------


class TestDashaTheme:
    def test_with_pd(self):
        theme = _dasha_theme("mercury", "ketu", "venus")
        assert "intellect" in theme.lower()
        assert "comfort" in theme.lower()

    def test_without_pd(self):
        theme = _dasha_theme("jupiter", "saturn", "unknown")
        assert "wisdom" in theme.lower()

    def test_unknown_planet(self):
        theme = _dasha_theme("xyz", "abc", "unknown")
        assert isinstance(theme, str)


# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------


class TestConstants:
    def test_rashi_names_count(self):
        assert len(RASHI_NAMES) == 12

    def test_weekday_names_count(self):
        assert len(WEEKDAY_NAMES) == 7

    def test_area_houses_eight_areas(self):
        assert len(AREA_HOUSES) == 8
        for key in (
            "career",
            "finance",
            "relationships",
            "health",
            "spiritual",
            "family",
            "education",
            "travel",
        ):
            assert key in AREA_HOUSES

    def test_area_planets_eight_areas(self):
        assert len(AREA_PLANETS) == 8
        for key in (
            "career",
            "finance",
            "relationships",
            "health",
            "spiritual",
            "family",
            "education",
            "travel",
        ):
            assert key in AREA_PLANETS

    def test_area_houses_valid_house_numbers(self):
        for houses in AREA_HOUSES.values():
            for h in houses:
                assert 1 <= h <= 12


# ---------------------------------------------------------------------------
# Full get_daily_forecast (mocked) tests
# ---------------------------------------------------------------------------


class TestGetDailyForecast:
    """Test the full get_daily_forecast function with mocked dependencies."""

    def _make_mock_planets(self) -> dict:
        return {
            "sun": {"longitude": 300.0, "speed": 1.0},
            "moon": {"longitude": 60.0, "speed": 13.0},
            "mars": {"longitude": 150.0, "speed": 0.5},
            "mercury": {"longitude": 310.0, "speed": 1.3},
            "jupiter": {"longitude": 40.0, "speed": 0.08},
            "venus": {"longitude": 280.0, "speed": 1.1},
            "saturn": {"longitude": 340.0, "speed": 0.03},
            "rahu": {"longitude": 5.0, "speed": -0.05},
            "ketu": {"longitude": 185.0, "speed": -0.05},
        }

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_returns_required_keys(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {
            "tithi": {"name": "Shukla Panchami", "number": 5, "paksha": "Shukla"},
            "vara": {"name": "Thursday", "number": 5},
            "yoga": {"name": "Siddha", "number": 16},
            "karana": {"name": "Bava", "number": 1},
            "nakshatra": {"name": "Mrigashira", "number": 5},
        }
        mock_dasha.return_value = {
            "mahadasha": {
                "lord": "mercury",
                "start_date": datetime(2019, 1, 1),
                "end_date": datetime(2036, 1, 1),
                "years": 17,
                "days_remaining": 3000,
            },
            "antardasha": {
                "lord": "ketu",
                "start_date": datetime(2025, 1, 1),
                "end_date": datetime(2026, 1, 1),
                "years": 1,
                "days_remaining": 300,
            },
            "pratyantardasha": {
                "lord": "venus",
                "start_date": datetime(2026, 1, 1),
                "end_date": datetime(2026, 3, 1),
                "years": 0.16,
                "days_remaining": 30,
            },
        }
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        assert "date" in result
        assert "day_rating" in result
        assert "summary" in result
        assert "panchanga" in result
        assert "moon_transit" in result
        assert "active_dasha" in result
        assert "transit_aspects_today" in result
        assert "inauspicious_periods" in result
        assert "choghadiya_highlights" in result
        assert "recommendations" in result
        assert "area_scores" in result
        assert len(result["area_scores"]) == 8
        for key in (
            "career",
            "finance",
            "relationships",
            "health",
            "spiritual",
            "family",
            "education",
            "travel",
        ):
            assert key in result["area_scores"]

        # New enriched fields
        assert "mental_state" in result
        assert "hora_lord" in result
        assert "gochara_summary" in result
        assert "is_chandrashtama" in result
        assert "active_yogas" in result
        assert "active_doshas" in result
        assert "sade_sati" in result
        assert "factor_scores" in result
        assert "upcoming_triggers" in result
        assert "composite_score" in result
        assert isinstance(result["gochara_summary"], list)
        assert isinstance(result["active_yogas"], list)
        assert isinstance(result["active_doshas"], list)
        assert isinstance(result["is_chandrashtama"], bool)

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_day_rating_in_range(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {}
        mock_dasha.return_value = None
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        assert 1 <= result["day_rating"] <= 10

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_panchanga_output_format(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {
            "tithi": {"name": "Shukla Dashami", "number": 10, "paksha": "Shukla"},
            "vara": {"name": "Saturday", "number": 7},
            "yoga": {"name": "Siddhi", "number": 16},
            "karana": {"name": "Taitila", "number": 4},
            "nakshatra": {"name": "Punarvasu", "number": 7},
        }
        mock_dasha.return_value = None
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        panchanga = result["panchanga"]
        assert "tithi" in panchanga
        assert "vara" in panchanga
        assert "yoga" in panchanga
        assert "karana" in panchanga
        assert "nakshatra" in panchanga

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_moon_transit_output(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {"nakshatra": {"name": "Mrigashira"}}
        mock_dasha.return_value = None
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        mt = result["moon_transit"]
        assert "sign" in mt
        assert "house_from_lagna" in mt
        assert "house_from_moon" in mt
        assert "ashtakavarga_score" in mt
        assert "quality" in mt

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_inauspicious_periods_format(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {}
        mock_dasha.return_value = None
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        ip = result["inauspicious_periods"]
        assert "rahu_kaal" in ip
        assert "start" in ip["rahu_kaal"]
        assert "end" in ip["rahu_kaal"]

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_choghadiya_highlights_format(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {}
        mock_dasha.return_value = None
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        ch = result["choghadiya_highlights"]
        assert "best_periods" in ch
        assert "avoid_periods" in ch
        assert isinstance(ch["best_periods"], list)
        assert isinstance(ch["avoid_periods"], list)

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_date_format(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {}
        mock_dasha.return_value = None
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        assert result["date"] == "2026-02-07"

    @patch("packages.cosmos.src.sunrise_sunset.get_sunrise_sunset")
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    @patch("packages.cosmos.src.panchanga.get_panchanga")
    @patch("packages.context.src.dasha.get_current_dasha")
    @patch("packages.context.src.transit_aspects.get_transit_natal_aspects")
    def test_active_dasha_output(
        self, mock_aspects, mock_dasha, mock_panchanga, mock_jd, mock_planets, mock_sun
    ):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = self._make_mock_planets()
        mock_panchanga.return_value = {}
        mock_dasha.return_value = {
            "mahadasha": {
                "lord": "mercury",
                "start_date": datetime(2019, 1, 1),
                "end_date": datetime(2036, 1, 1),
                "years": 17,
                "days_remaining": 3000,
            },
            "antardasha": {
                "lord": "ketu",
                "start_date": datetime(2025, 1, 1),
                "end_date": datetime(2026, 1, 1),
                "years": 1,
                "days_remaining": 300,
            },
            "pratyantardasha": {
                "lord": "venus",
                "start_date": datetime(2026, 1, 1),
                "end_date": datetime(2026, 3, 1),
                "years": 0.16,
                "days_remaining": 30,
            },
        }
        mock_aspects.return_value = []
        mock_sun.return_value = {
            "sunrise": datetime(2026, 2, 7, 6, 30),
            "sunset": datetime(2026, 2, 7, 18, 0),
        }

        result = get_daily_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            query_date="2026-02-07",
        )

        ad = result["active_dasha"]
        assert ad["mahadasha"] == "mercury"
        assert ad["antardasha"] == "ketu"
        assert ad["pratyantardasha"] == "venus"
        assert "theme" in ad
