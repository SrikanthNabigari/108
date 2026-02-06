"""Tests for the Weekly Forecast Engine.

Tests cover:
- Area ratings computation
- Key transit extraction
- Weekly theme generation
- Dasha week theme
- Full weekly forecast integration (mocked)
"""

from unittest.mock import patch

from packages.context.src.weekly_forecast import (
    _area_summary,
    _compute_area_ratings,
    _dasha_week_theme,
    _extract_key_transits,
    _generate_weekly_theme,
    get_weekly_forecast,
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


def _make_daily_forecast(date: str, rating: int, aspects: list | None = None) -> dict:
    """Helper to create a minimal daily forecast dict."""
    return {
        "date": date,
        "day_rating": rating,
        "summary": f"Day rated {rating}",
        "panchanga": {},
        "moon_transit": {"house_from_lagna": 5, "sign": "gemini"},
        "active_dasha": {"mahadasha": "mercury", "antardasha": "ketu", "pratyantardasha": "venus"},
        "transit_aspects_today": aspects or [],
        "inauspicious_periods": {},
        "choghadiya_highlights": {"best_periods": [], "avoid_periods": []},
        "recommendations": {},
    }


# ---------------------------------------------------------------------------
# _area_summary tests
# ---------------------------------------------------------------------------


class TestAreaSummary:
    def test_excellent_rating(self):
        s = _area_summary("career", 9)
        assert "Excellent" in s

    def test_good_rating(self):
        s = _area_summary("finance", 7)
        assert "Good" in s

    def test_moderate_rating(self):
        s = _area_summary("health", 4)
        assert "Moderate" in s

    def test_challenging_rating(self):
        s = _area_summary("spiritual", 2)
        assert "Challenging" in s


# ---------------------------------------------------------------------------
# _compute_area_ratings tests
# ---------------------------------------------------------------------------


class TestComputeAreaRatings:
    def test_returns_five_areas(self):
        forecasts = [_make_daily_forecast(f"2026-02-0{i+1}", 5) for i in range(7)]
        areas = _compute_area_ratings(forecasts, NATAL_PLANETS, "libra", "mercury", "ketu")
        assert len(areas) == 5
        for key in ("career", "finance", "relationships", "health", "spiritual"):
            assert key in areas

    def test_each_area_has_rating_and_summary(self):
        forecasts = [_make_daily_forecast(f"2026-02-0{i+1}", 5) for i in range(7)]
        areas = _compute_area_ratings(forecasts, NATAL_PLANETS, "libra", "mercury", "ketu")
        for area_data in areas.values():
            assert "rating" in area_data
            assert "summary" in area_data
            assert 1 <= area_data["rating"] <= 10

    def test_dasha_lord_matching_boosts_area(self):
        forecasts = [_make_daily_forecast(f"2026-02-0{i+1}", 5) for i in range(7)]
        # Mercury is in AREA_PLANETS["finance"]
        areas = _compute_area_ratings(forecasts, NATAL_PLANETS, "libra", "mercury", "jupiter")
        # Both mercury and jupiter are finance planets
        assert areas["finance"]["rating"] >= 5

    def test_aspects_boost_areas(self):
        asp = [{"transit": "jupiter", "natal": "venus", "aspect": "trine", "orb": 1.0}]
        forecasts = [_make_daily_forecast(f"2026-02-0{i+1}", 5, asp) for i in range(7)]
        areas = _compute_area_ratings(forecasts, NATAL_PLANETS, "libra", "mercury", "ketu")
        # Jupiter+Venus aspects should help finance and relationships
        assert areas["finance"]["rating"] >= 5


# ---------------------------------------------------------------------------
# _extract_key_transits tests
# ---------------------------------------------------------------------------


class TestExtractKeyTransits:
    def test_empty_forecasts(self):
        assert _extract_key_transits([]) == []

    def test_ignores_wide_orb(self):
        asp = [{"transit": "saturn", "natal": "moon", "aspect": "square", "orb": 5.0}]
        forecasts = [_make_daily_forecast("2026-02-07", 5, asp)]
        result = _extract_key_transits(forecasts)
        assert len(result) == 0  # orb > 3 ignored

    def test_detects_tight_slow_planet(self):
        asp = [{"transit": "saturn", "natal": "moon", "aspect": "square", "orb": 1.5}]
        forecasts = [_make_daily_forecast("2026-02-07", 5, asp)]
        result = _extract_key_transits(forecasts)
        assert len(result) == 1
        assert result[0]["impact"] == "challenging"

    def test_deduplicates_across_days(self):
        asp = [{"transit": "jupiter", "natal": "sun", "aspect": "trine", "orb": 2.0}]
        forecasts = [_make_daily_forecast(f"2026-02-0{i+1}", 5, asp) for i in range(3)]
        result = _extract_key_transits(forecasts)
        assert len(result) == 1

    def test_jupiter_trine_is_positive(self):
        asp = [{"transit": "jupiter", "natal": "sun", "aspect": "trine", "orb": 1.0}]
        forecasts = [_make_daily_forecast("2026-02-07", 5, asp)]
        result = _extract_key_transits(forecasts)
        assert result[0]["impact"] == "positive"

    def test_jupiter_conjunction_very_positive(self):
        asp = [{"transit": "jupiter", "natal": "moon", "aspect": "conjunction", "orb": 0.5}]
        forecasts = [_make_daily_forecast("2026-02-07", 5, asp)]
        result = _extract_key_transits(forecasts)
        assert result[0]["impact"] == "very_positive"


# ---------------------------------------------------------------------------
# _generate_weekly_theme tests
# ---------------------------------------------------------------------------


class TestGenerateWeeklyTheme:
    def test_high_rating_theme(self):
        areas = {
            "career": {"rating": 8},
            "finance": {"rating": 7},
            "relationships": {"rating": 6},
            "health": {"rating": 7},
            "spiritual": {"rating": 5},
        }
        theme = _generate_weekly_theme(7.5, "jupiter", "venus", areas)
        assert "career" in theme.lower() or "Jupiter" in theme

    def test_low_rating_theme(self):
        areas = {
            "career": {"rating": 3},
            "finance": {"rating": 3},
            "relationships": {"rating": 4},
            "health": {"rating": 3},
            "spiritual": {"rating": 5},
        }
        theme = _generate_weekly_theme(3.0, "saturn", "rahu", areas)
        assert "patience" in theme.lower() or "carefully" in theme.lower()

    def test_returns_string(self):
        areas = {
            "career": {"rating": 5},
            "finance": {"rating": 5},
            "relationships": {"rating": 5},
            "health": {"rating": 5},
            "spiritual": {"rating": 5},
        }
        theme = _generate_weekly_theme(5.0, "mercury", "ketu", areas)
        assert isinstance(theme, str)
        assert len(theme) > 0


# ---------------------------------------------------------------------------
# _dasha_week_theme tests
# ---------------------------------------------------------------------------


class TestDashaWeekTheme:
    def test_benefic_pair(self):
        theme = _dasha_week_theme("jupiter", "venus")
        assert "favor" in theme.lower()
        assert "creative" in theme.lower()

    def test_malefic_pair(self):
        theme = _dasha_week_theme("saturn", "rahu")
        assert "patience" in theme.lower()
        assert "disciplined" in theme.lower()


# ---------------------------------------------------------------------------
# Full get_weekly_forecast (mocked) tests
# ---------------------------------------------------------------------------


class TestGetWeeklyForecast:
    """Test the full weekly forecast with get_daily_forecast mocked."""

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_returns_required_keys(self, mock_daily):
        mock_daily.return_value = _make_daily_forecast("2026-02-07", 6)

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        assert "week_start" in result
        assert "week_end" in result
        assert "overall_rating" in result
        assert "weekly_theme" in result
        assert "peak_days" in result
        assert "challenging_days" in result
        assert "daily_forecasts" in result
        assert "key_transits_this_week" in result
        assert "dasha_context" in result
        assert "areas" in result

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_seven_daily_forecasts(self, mock_daily):
        mock_daily.return_value = _make_daily_forecast("2026-02-07", 5)

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        assert len(result["daily_forecasts"]) == 7

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_overall_rating_is_average(self, mock_daily):
        ratings = [5, 6, 7, 4, 8, 3, 9]
        call_count = [0]

        def side_effect(**kwargs):
            idx = call_count[0] % len(ratings)
            call_count[0] += 1
            return _make_daily_forecast(kwargs.get("query_date", "2026-02-07"), ratings[idx])

        mock_daily.side_effect = side_effect

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        expected_avg = round(sum(ratings) / 7, 1)
        assert result["overall_rating"] == expected_avg

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_peak_days_identified(self, mock_daily):
        call_count = [0]
        ratings = [5, 5, 8, 5, 5, 9, 5]

        def side_effect(**kwargs):
            idx = call_count[0] % len(ratings)
            call_count[0] += 1
            return _make_daily_forecast(kwargs.get("query_date", "2026-02-07"), ratings[idx])

        mock_daily.side_effect = side_effect

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        assert len(result["peak_days"]) >= 2

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_challenging_days_identified(self, mock_daily):
        call_count = [0]
        ratings = [5, 2, 5, 1, 5, 5, 5]

        def side_effect(**kwargs):
            idx = call_count[0] % len(ratings)
            call_count[0] += 1
            return _make_daily_forecast(kwargs.get("query_date", "2026-02-07"), ratings[idx])

        mock_daily.side_effect = side_effect

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        assert len(result["challenging_days"]) >= 2

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_areas_have_five_entries(self, mock_daily):
        mock_daily.return_value = _make_daily_forecast("2026-02-07", 6)

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        assert len(result["areas"]) == 5
        for area_data in result["areas"].values():
            assert "rating" in area_data
            assert "summary" in area_data

    @patch("packages.context.src.weekly_forecast.get_daily_forecast")
    def test_dasha_context_format(self, mock_daily):
        mock_daily.return_value = _make_daily_forecast("2026-02-07", 6)

        result = get_weekly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            start_date="2026-02-07",
        )

        dc = result["dasha_context"]
        assert "period" in dc
        assert "week_theme" in dc
