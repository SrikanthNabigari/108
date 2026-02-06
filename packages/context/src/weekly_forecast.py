"""Weekly Forecast Engine for 108 Vedic Astrology.

Generates a 7-day forecast by composing daily forecasts, identifying
peak/challenging days, aggregating transit events, and computing
area-wise ratings for career, finance, relationships, health, and spiritual.
"""

from datetime import datetime, timedelta
from typing import Any

from packages.context.src.daily_forecast import (
    AREA_HOUSES,
    AREA_PLANETS,
    get_daily_forecast,
)


def _compute_area_ratings(
    daily_forecasts: list[dict[str, Any]],
    natal_planets: dict[str, dict[str, Any]],  # noqa: ARG001
    lagna_rashi: str,  # noqa: ARG001
    dasha_md: str,
    dasha_ad: str,
) -> dict[str, dict[str, Any]]:
    """Compute area ratings from daily forecast data.

    Areas: career, finance, relationships, health, spiritual.
    Each gets a 1-10 rating and a short summary.
    """
    areas: dict[str, dict[str, Any]] = {}

    for area, houses in AREA_HOUSES.items():
        planets = AREA_PLANETS.get(area, [])
        score = 5.0  # baseline

        # Count transit aspects involving area-relevant planets
        total_aspect_boost = 0.0
        for df in daily_forecasts:
            for asp in df.get("transit_aspects_today", []):
                t_planet = asp.get("transit", "").lower()
                n_planet = asp.get("natal", "").lower()
                aspect_type = asp.get("aspect", "")

                if t_planet in planets or n_planet in planets:
                    if aspect_type in ("trine", "sextile", "conjunction"):
                        total_aspect_boost += 0.3
                    elif aspect_type in ("square", "opposition"):
                        total_aspect_boost -= 0.2

        score += total_aspect_boost / max(len(daily_forecasts), 1)

        # Dasha lord affinity with area planets
        if dasha_md in planets:
            score += 1.0
        if dasha_ad in planets:
            score += 0.5

        # Moon house transits through area houses during the week
        moon_in_area_count = 0
        for df in daily_forecasts:
            moon_house = df.get("moon_transit", {}).get("house_from_lagna", 0)
            if moon_house in houses:
                moon_in_area_count += 1
        score += moon_in_area_count * 0.3

        rating = max(1, min(10, round(score)))
        summary = _area_summary(area, rating)
        areas[area] = {"rating": rating, "summary": summary}

    return areas


def _area_summary(area: str, rating: int) -> str:
    """Generate a brief summary for an area rating."""
    if rating >= 8:
        tone = "Excellent"
    elif rating >= 6:
        tone = "Good"
    elif rating >= 4:
        tone = "Moderate"
    else:
        tone = "Challenging"

    area_actions = {
        "career": "professional initiatives",
        "finance": "financial decisions",
        "relationships": "social connections",
        "health": "physical wellbeing",
        "spiritual": "inner growth practices",
    }
    action = area_actions.get(area, area)
    return f"{tone} week for {action}"


def _extract_key_transits(
    daily_forecasts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extract significant transit events from the week's daily forecasts."""
    key_transits: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    for df in daily_forecasts:
        date_str = df.get("date", "")
        for asp in df.get("transit_aspects_today", []):
            # Only report tight aspects (orb < 3) and slow planet aspects
            orb = asp.get("orb", 99)
            t_planet = asp.get("transit", "").lower()
            slow_planets = {"saturn", "jupiter", "rahu", "ketu", "mars"}

            if orb <= 3.0 and t_planet in slow_planets:
                key = f"{t_planet}-{asp.get('natal', '')}-{asp.get('aspect', '')}"
                if key not in seen_keys:
                    seen_keys.add(key)

                    # Determine impact
                    aspect_type = asp.get("aspect", "")
                    if aspect_type in ("trine", "sextile"):
                        impact = "positive"
                    elif aspect_type in ("square", "opposition"):
                        impact = "challenging"
                    elif aspect_type == "conjunction":
                        impact = "very_positive" if t_planet in ("jupiter", "venus") else "intense"
                    else:
                        impact = "neutral"

                    key_transits.append(
                        {
                            "date": date_str,
                            "event": f"{t_planet.title()} {aspect_type} natal {asp.get('natal', '').title()}",
                            "impact": impact,
                        }
                    )

    return key_transits


def _generate_weekly_theme(
    overall_rating: float,
    dasha_md: str,
    dasha_ad: str,
    area_ratings: dict[str, dict[str, Any]],
) -> str:
    """Generate a concise weekly theme string."""
    # Find top and bottom areas
    sorted_areas = sorted(area_ratings.items(), key=lambda x: x[1]["rating"], reverse=True)
    top_area = sorted_areas[0][0] if sorted_areas else "general"
    bottom_area = sorted_areas[-1][0] if sorted_areas else "general"

    area_labels = {
        "career": "career activity",
        "finance": "financial focus",
        "relationships": "relationship dynamics",
        "health": "health awareness",
        "spiritual": "spiritual depth",
    }

    top_label = area_labels.get(top_area, top_area)
    bottom_label = area_labels.get(bottom_area, bottom_area)

    if overall_rating >= 7:
        return f"Strong {top_label} with {dasha_md.title()}-{dasha_ad.title()} support"
    elif overall_rating >= 5:
        return f"{top_label.title()} leads, mindful approach to {bottom_label}"
    else:
        return f"Patience week — focus on {top_label}, navigate {bottom_label} carefully"


def get_weekly_forecast(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, dict[str, Any]],
    moon_longitude: float,
    lagna_rashi: str,
    start_date: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """Generate a comprehensive 7-day forecast.

    Calls get_daily_forecast for each of 7 days, aggregates results,
    identifies peak/challenging days, key transits, and area ratings.

    Args:
        birth_datetime: ISO-format birth datetime string
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        natal_planets: Birth chart planet positions
        moon_longitude: Natal Moon longitude (degrees)
        lagna_rashi: Ascendant sign name (e.g. "libra")
        start_date: First day of the week (ISO date string, defaults to today)
        location_lat: Current location latitude
        location_lon: Current location longitude

    Returns:
        Weekly forecast dictionary with daily_forecasts, key_transits,
        area ratings, peak/challenging days, and weekly theme.
    """
    s_dt = datetime.fromisoformat(start_date) if start_date else datetime.now()

    week_start = datetime(s_dt.year, s_dt.month, s_dt.day)
    week_end = week_start + timedelta(days=6)

    # Generate daily forecasts for 7 days
    daily_forecasts: list[dict[str, Any]] = []
    for day_offset in range(7):
        day_dt = week_start + timedelta(days=day_offset)
        day_str = day_dt.strftime("%Y-%m-%d")
        try:
            df = get_daily_forecast(
                birth_datetime=birth_datetime,
                birth_lat=birth_lat,
                birth_lon=birth_lon,
                natal_planets=natal_planets,
                moon_longitude=moon_longitude,
                lagna_rashi=lagna_rashi,
                query_date=day_str,
                location_lat=location_lat,
                location_lon=location_lon,
            )
            daily_forecasts.append(df)
        except Exception:
            # Provide a minimal fallback
            daily_forecasts.append(
                {
                    "date": day_str,
                    "day_rating": 5,
                    "summary": "Forecast unavailable",
                    "panchanga": {},
                    "moon_transit": {},
                    "active_dasha": {},
                    "transit_aspects_today": [],
                    "inauspicious_periods": {},
                    "choghadiya_highlights": {},
                    "recommendations": {},
                }
            )

    # Overall rating = average of daily ratings
    ratings = [df.get("day_rating", 5) for df in daily_forecasts]
    overall_rating = round(sum(ratings) / len(ratings), 1) if ratings else 5.0

    # Peak and challenging days
    peak_days: list[str] = []
    challenging_days: list[str] = []
    for df in daily_forecasts:
        r = df.get("day_rating", 5)
        d = df.get("date", "")
        if r >= 7:
            peak_days.append(d)
        elif r <= 3:
            challenging_days.append(d)

    # Key transits
    key_transits = _extract_key_transits(daily_forecasts)

    # Dasha context
    dasha_md = "unknown"
    dasha_ad = "unknown"
    dasha_pd = "unknown"
    for df in daily_forecasts:
        ad = df.get("active_dasha", {})
        if ad.get("mahadasha") and ad["mahadasha"] != "unknown":
            dasha_md = ad["mahadasha"]
            dasha_ad = ad.get("antardasha", "unknown")
            dasha_pd = ad.get("pratyantardasha", "unknown")
            break

    dasha_context = {
        "period": f"{dasha_md.title()}-{dasha_ad.title()}-{dasha_pd.title()}",
        "week_theme": _dasha_week_theme(dasha_md, dasha_ad),
    }

    # Area ratings
    area_ratings = _compute_area_ratings(
        daily_forecasts,
        natal_planets,
        lagna_rashi,
        dasha_md,
        dasha_ad,
    )

    # Weekly theme
    weekly_theme = _generate_weekly_theme(overall_rating, dasha_md, dasha_ad, area_ratings)

    return {
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
        "overall_rating": overall_rating,
        "weekly_theme": weekly_theme,
        "peak_days": peak_days,
        "challenging_days": challenging_days,
        "daily_forecasts": daily_forecasts,
        "key_transits_this_week": key_transits,
        "dasha_context": dasha_context,
        "areas": area_ratings,
    }


def _dasha_week_theme(md: str, ad: str) -> str:
    """Generate dasha week theme sentence."""
    benefic = {"jupiter", "venus", "mercury", "moon"}
    md_quality = "favor" if md in benefic else "call for patience in"
    ad_quality = "creative" if ad in benefic else "disciplined"
    return f"Dasha lords {md_quality} {ad_quality} pursuits this week"
