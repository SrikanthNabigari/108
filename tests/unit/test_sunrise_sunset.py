"""Tests for sunrise/sunset calculations."""

from datetime import UTC, datetime

from packages.cosmos.src.sunrise_sunset import (
    get_sunrise,
    get_sunrise_sunset,
    get_sunset,
)


class TestSunriseSunset:
    """Test sunrise/sunset core functionality."""

    def test_basic_sunrise_sunset(self):
        """Test basic sunrise/sunset for a known location."""
        # Delhi, India - 2024-03-20 (equinox)
        date = datetime(2024, 3, 20, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=28.6139, longitude=77.2090)

        assert "sunrise" in result
        assert "sunset" in result
        assert "sunrise_jd" in result
        assert "sunset_jd" in result
        assert "day_duration_hours" in result
        assert "night_duration_hours" in result

        # Sunrise should be before sunset
        assert result["sunrise"] < result["sunset"]

        # Day + night should be ~24 hours
        total = result["day_duration_hours"] + result["night_duration_hours"]
        assert abs(total - 24.0) < 0.01

    def test_equinox_day_length(self):
        """Near equinox, day and night should be roughly equal."""
        date = datetime(2024, 3, 20, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=0.0, longitude=0.0)

        # At equator during equinox, day ~12 hours
        assert 11.5 < result["day_duration_hours"] < 12.5

    def test_user_location(self):
        """Test with user's birth location (16.726, 81.288)."""
        date = datetime(1992, 12, 3, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=16.726239, longitude=81.288428)

        assert result["sunrise"].year == 1992
        assert result["sunrise"].month == 12
        assert result["sunrise"].day == 3

        # December in India, day should be shorter
        assert result["day_duration_hours"] < 12.0

    def test_summer_solstice_northern(self):
        """Summer solstice: longest day in northern hemisphere."""
        date = datetime(2024, 6, 21, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=40.0, longitude=0.0)

        # Day should be longer than 14 hours at 40°N
        assert result["day_duration_hours"] > 14.0

    def test_winter_solstice_northern(self):
        """Winter solstice: shortest day in northern hemisphere."""
        date = datetime(2024, 12, 21, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=40.0, longitude=0.0)

        # Day should be shorter than 10 hours at 40°N
        assert result["day_duration_hours"] < 10.0

    def test_tropical_location(self):
        """Test near tropics - moderate day length variation."""
        # Chennai, India (13°N)
        date = datetime(2024, 6, 15, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=13.08, longitude=80.27)

        # Tropical locations have relatively stable day length
        assert 11.5 < result["day_duration_hours"] < 13.5

    def test_sunrise_jd_before_sunset_jd(self):
        """Sunrise JD should always be less than sunset JD."""
        date = datetime(2024, 6, 15, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=28.6, longitude=77.2)

        assert result["sunrise_jd"] < result["sunset_jd"]

    def test_returns_utc_datetimes(self):
        """Returned datetimes should be in UTC."""
        date = datetime(2024, 3, 20, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=28.6, longitude=77.2)

        assert result["sunrise"].tzinfo == UTC
        assert result["sunset"].tzinfo == UTC

    def test_with_altitude(self):
        """Test with non-zero altitude."""
        date = datetime(2024, 3, 20, tzinfo=UTC)
        result_sea = get_sunrise_sunset(date, latitude=28.6, longitude=77.2, altitude=0.0)
        result_high = get_sunrise_sunset(date, latitude=28.6, longitude=77.2, altitude=2000.0)

        # Both should return valid results
        assert result_sea["sunrise"] < result_sea["sunset"]
        assert result_high["sunrise"] < result_high["sunset"]

    def test_southern_hemisphere(self):
        """Test southern hemisphere location."""
        # Sydney, Australia
        date = datetime(2024, 1, 15, tzinfo=UTC)
        result = get_sunrise_sunset(date, latitude=-33.87, longitude=151.21)

        # January is summer in southern hemisphere, day should be > 13 hours
        assert result["day_duration_hours"] > 13.0

    def test_different_dates_same_location(self):
        """Day length should vary through the year."""
        loc = {"latitude": 40.0, "longitude": 0.0}
        summer = get_sunrise_sunset(datetime(2024, 6, 21, tzinfo=UTC), **loc)
        winter = get_sunrise_sunset(datetime(2024, 12, 21, tzinfo=UTC), **loc)

        assert summer["day_duration_hours"] > winter["day_duration_hours"]


class TestConvenienceFunctions:
    """Test get_sunrise and get_sunset convenience functions."""

    def test_get_sunrise(self):
        """get_sunrise returns datetime."""
        date = datetime(2024, 3, 20, tzinfo=UTC)
        sunrise = get_sunrise(date, latitude=28.6, longitude=77.2)

        assert isinstance(sunrise, datetime)
        assert sunrise.tzinfo == UTC

    def test_get_sunset(self):
        """get_sunset returns datetime."""
        date = datetime(2024, 3, 20, tzinfo=UTC)
        sunset = get_sunset(date, latitude=28.6, longitude=77.2)

        assert isinstance(sunset, datetime)
        assert sunset.tzinfo == UTC

    def test_sunrise_before_sunset(self):
        """Sunrise should always be before sunset for same day."""
        date = datetime(2024, 3, 20, tzinfo=UTC)
        sunrise = get_sunrise(date, latitude=28.6, longitude=77.2)
        sunset = get_sunset(date, latitude=28.6, longitude=77.2)

        assert sunrise < sunset

    def test_naive_datetime_input(self):
        """Should handle naive datetime (no timezone)."""
        date = datetime(2024, 3, 20)
        result = get_sunrise_sunset(date, latitude=28.6, longitude=77.2)

        assert result["sunrise"] < result["sunset"]
