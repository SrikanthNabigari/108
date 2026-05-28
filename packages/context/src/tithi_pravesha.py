"""Tithi Pravesha annual chart for 108 Vedic Astrology.

Tithi Pravesha Chakra (TPC) is a yearly horoscope cast for the moment when
the Sun-Moon angular distance returns to the natal tithi value. It is the
lunar-month analogue of Varshaphal (solar return). Each year on the native's
"tithi-anniversary," the chart frozen at that moment indicates the themes
of the upcoming lunar year.

Source: Tithi-Pravesha-Tantra, classical Phaladeepika supplements.

Algorithm:
    1. Natal: compute (moon_lon - sun_lon) % 360 = natal_tithi_arc.
    2. For target year N: scan the native's tithi-anniversary window
       (approx 354.367 lunar days * N from birth, +/-15 days).
    3. Bisect for the moment when (transit_moon - transit_sun) % 360
       == natal_tithi_arc (within 0.001 degrees).
    4. Cast a chart at that exact moment.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day
from packages.cosmos.src.panchanga import get_tithi


def _moon_minus_sun(dt: datetime) -> float:
    """Return (Moon_lon - Sun_lon) % 360 at given moment (sidereal)."""
    jd = get_julian_day(dt)
    planets = get_all_planets(jd)
    sun_lon = float(planets["sun"]["longitude"])
    moon_lon = float(planets["moon"]["longitude"])
    return (moon_lon - sun_lon) % 360


def get_natal_tithi_arc(natal_sun_lon: float, natal_moon_lon: float) -> float:
    """Return the natal tithi arc (Moon-Sun in degrees, 0-360)."""
    return (natal_moon_lon - natal_sun_lon) % 360


def find_tithi_pravesha_datetime(
    birth_datetime: datetime,
    natal_sun_lon: float,
    natal_moon_lon: float,
    target_year_offset: int = 1,
    max_search_days: int = 30,
) -> datetime:
    """Find the next Tithi Pravesha datetime for a given lunar-year offset.

    Args:
        birth_datetime: Birth datetime (tz-aware preferred).
        natal_sun_lon: Sun's sidereal longitude at birth.
        natal_moon_lon: Moon's sidereal longitude at birth.
        target_year_offset: Which year's TP to find. 1 = first anniversary.
        max_search_days: Half-window (days) around the estimated date.

    Returns:
        Datetime when (Moon - Sun) sidereal angular distance equals the
        natal tithi arc within 0.0005°. Bisection-precise (~minutes).
    """
    target_arc = get_natal_tithi_arc(natal_sun_lon, natal_moon_lon)
    # Lunar year ≈ 354.36707 days (12 synodic months)
    estimated = birth_datetime + timedelta(days=354.36707 * target_year_offset)

    # Coarse scan: hourly steps in ±max_search_days window for the closest crossing
    start = estimated - timedelta(days=max_search_days)
    step = timedelta(hours=1)
    best_dt = start
    best_delta = 360.0
    cur = start
    end = estimated + timedelta(days=max_search_days)
    while cur <= end:
        arc = _moon_minus_sun(cur)
        delta = (arc - target_arc + 540) % 360 - 180  # signed shortest distance
        if abs(delta) < best_delta:
            best_delta = abs(delta)
            best_dt = cur
        cur += step

    # Fine bisection: ±2 hours around best_dt
    lo = best_dt - timedelta(hours=2)
    hi = best_dt + timedelta(hours=2)
    for _ in range(40):  # ~minute precision after 40 iters
        mid = lo + (hi - lo) / 2
        arc_mid = _moon_minus_sun(mid)
        d_mid = (arc_mid - target_arc + 540) % 360 - 180
        arc_lo = _moon_minus_sun(lo)
        d_lo = (arc_lo - target_arc + 540) % 360 - 180
        if d_lo * d_mid < 0:
            hi = mid
        else:
            lo = mid
        if abs(d_mid) < 0.0005:
            break
    return mid


def cast_tithi_pravesha_chart(
    birth_datetime: datetime,
    natal_sun_lon: float,
    natal_moon_lon: float,
    target_year_offset: int = 1,
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """Cast a Tithi Pravesha chart for the given lunar-year offset.

    Args:
        birth_datetime: Birth datetime.
        natal_sun_lon: Sun's sidereal longitude at birth.
        natal_moon_lon: Moon's sidereal longitude at birth.
        target_year_offset: Which year's TP chart (1 = first anniversary).
        location_lat: Latitude for the TP chart (default: native's, but TP
            is typically cast for the native's current residence).
        location_lon: Longitude for the TP chart.

    Returns:
        {
          "tithi_pravesha_datetime": ISO,
          "lunar_year_offset": int,
          "natal_tithi": {number, name, paksha, ...},
          "tp_chart": {
             "datetime": ISO,
             "location": {lat, lon},
             "planets": {planet: {longitude, sign_index, ...}},
             "tithi_at_moment": {...},
          },
        }
    """
    tp_dt = find_tithi_pravesha_datetime(
        birth_datetime, natal_sun_lon, natal_moon_lon, target_year_offset
    )

    jd = get_julian_day(tp_dt)
    planets = get_all_planets(jd)

    natal_tithi = get_tithi(natal_sun_lon, natal_moon_lon)
    tp_tithi = get_tithi(float(planets["sun"]["longitude"]), float(planets["moon"]["longitude"]))

    # Coarse house assignment from Moon ascendant approximation:
    # TP chart traditionally uses the rising sign at the TP moment + location.
    # Here we expose the planet positions and let downstream consumers
    # call house_cusps() with location for full Lagna calculation.
    chart_planets: dict[str, Any] = {}
    for name, pdata in planets.items():
        lon = float(pdata.get("longitude", 0.0))
        chart_planets[name] = {
            "longitude": round(lon, 4),
            "sign_index": int(lon // 30) % 12,
            "sign_degree": round(lon % 30, 4),
            "is_retrograde": bool(pdata.get("is_retrograde", False)),
            "speed": float(pdata.get("speed", 0.0)),
        }

    return {
        "tithi_pravesha_datetime": tp_dt.isoformat(),
        "lunar_year_offset": target_year_offset,
        "natal_tithi": natal_tithi,
        "tp_chart": {
            "datetime": tp_dt.isoformat(),
            "location": {
                "lat": location_lat,
                "lon": location_lon,
            },
            "planets": chart_planets,
            "tithi_at_moment": tp_tithi,
        },
    }


def interpret_tithi_pravesha(
    tp_result: dict[str, Any],
    natal_planets: dict[str, dict[str, Any]],
    lagna_index: int,
) -> dict[str, Any]:
    """Lightweight interpretation of TP chart vs natal positions.

    Returns key signals: planets that have shifted into kendra/trikona/dusthana
    relative to the natal lagna, lord of TP-Moon's nakshatra (year ruler), and
    a list of TP planets whose sign matches their natal sign (yoga continuation).
    """
    tp_planets = tp_result.get("tp_chart", {}).get("planets", {})
    kendra = {1, 4, 7, 10}
    trikona = {1, 5, 9}
    dusthana = {6, 8, 12}

    shifts: list[dict[str, Any]] = []
    for name, pdata in tp_planets.items():
        natal = natal_planets.get(name, {})
        if not isinstance(natal, dict):
            continue
        natal_lon = float(natal.get("longitude", 0.0))
        natal_sign = int(natal_lon // 30) % 12
        tp_sign = int(pdata.get("sign_index", 0))
        natal_house = ((natal_sign - lagna_index) % 12) + 1
        tp_house = ((tp_sign - lagna_index) % 12) + 1

        category_natal = (
            "kendra"
            if natal_house in kendra
            else "trikona"
            if natal_house in trikona
            else "dusthana"
            if natal_house in dusthana
            else "neutral"
        )
        category_tp = (
            "kendra"
            if tp_house in kendra
            else "trikona"
            if tp_house in trikona
            else "dusthana"
            if tp_house in dusthana
            else "neutral"
        )
        if category_natal != category_tp or natal_house != tp_house:
            shifts.append(
                {
                    "planet": name,
                    "natal_house": natal_house,
                    "tp_house": tp_house,
                    "natal_category": category_natal,
                    "tp_category": category_tp,
                    "improvement": (category_natal == "dusthana" and category_tp != "dusthana")
                    or (category_tp in ("kendra", "trikona") and category_natal == "neutral"),
                }
            )

    # Year ruler: lord of TP-Moon's nakshatra
    nakshatra_lords = [
        "ketu",
        "venus",
        "sun",
        "moon",
        "mars",
        "rahu",
        "jupiter",
        "saturn",
        "mercury",
    ]
    tp_moon = tp_planets.get("moon", {})
    tp_moon_lon = float(tp_moon.get("longitude", 0.0))
    nak_idx = int(tp_moon_lon // 13.333333333) % 27
    year_ruler = nakshatra_lords[nak_idx % 9]

    return {
        "year_ruler": year_ruler,
        "year_ruler_basis": f"TP-Moon in nakshatra #{nak_idx + 1}",
        "planet_shifts": shifts,
        "favorable_shift_count": sum(1 for s in shifts if s.get("improvement")),
    }
