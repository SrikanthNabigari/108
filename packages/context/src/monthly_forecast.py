"""Monthly Forecast Engine for 108 Vedic Astrology.

Generates a month-long forecast with:
- Major transits (ingresses, aspects, stations)
- Dasha transitions within the month
- Retrograde status of planets
- Area-wise analysis (career, finance, relationships, health, spiritual)
- Weekly summaries (4 weeks)
- Best/worst dates for various activities

Does NOT generate 30 daily forecasts (too slow). Instead computes
weekly summaries and aggregates transit events at a coarser granularity.
"""

import calendar
from datetime import datetime, timedelta
from typing import Any

from packages.context.src.daily_forecast import (
    _DASHA_LORD_QUALITY,
    AREA_HOUSES,
    AREA_PLANETS,
    RASHI_NAMES,
    _get_rashi_index,
    _house_from_lagna,
)

# Month names for display
MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def _detect_retrogrades(
    start_date: datetime,
    days: int,
) -> dict[str, Any]:
    """Detect planets that are retrograde during the month.

    Checks planet speeds at weekly intervals to find retrograde planets
    and approximate station dates.
    """
    from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

    retro_planets: list[str] = []
    retro_dates: dict[str, dict[str, str]] = {}
    trackable = ["mercury", "venus", "mars", "jupiter", "saturn"]

    prev_retro: dict[str, bool] = {}

    for day_offset in range(0, days + 1, 3):
        check_dt = start_date + timedelta(days=day_offset)
        try:
            jd = get_julian_day(check_dt)
            positions = get_all_planets(jd)
        except Exception:
            continue

        for planet in trackable:
            if planet not in positions:
                continue
            speed = positions[planet].get("speed", 1.0)
            is_retro = speed < 0

            if planet not in prev_retro:
                # First check — record initial state
                if is_retro and planet not in retro_planets:
                    retro_planets.append(planet)
                    retro_dates[planet] = {"start": "before_month", "end": "unknown"}
                prev_retro[planet] = is_retro
                continue

            was_retro = prev_retro[planet]
            if not was_retro and is_retro:
                # Planet turned retrograde
                if planet not in retro_planets:
                    retro_planets.append(planet)
                retro_dates[planet] = {
                    "start": check_dt.strftime("%Y-%m-%d"),
                    "end": "unknown",
                }
            elif was_retro and not is_retro:
                # Planet turned direct
                if planet in retro_dates:
                    retro_dates[planet]["end"] = check_dt.strftime("%Y-%m-%d")

            prev_retro[planet] = is_retro

    # Summarize impact
    impact_parts = []
    for planet in retro_planets:
        planet_impact = {
            "mercury": "communication delays, review period",
            "venus": "relationship re-evaluation, financial caution",
            "mars": "reduced drive, internal anger, re-strategize",
            "jupiter": "wisdom turns inward, reassess growth plans",
            "saturn": "karmic review, structural reassessment",
        }
        impact_parts.append(f"{planet.title()} retrograde: {planet_impact.get(planet, '')}")

    return {
        "planets_retrograde": retro_planets,
        "dates": retro_dates,
        "impact": "; ".join(impact_parts) if impact_parts else "No retrogrades this month",
    }


def _get_dasha_transitions(
    birth_datetime: datetime,
    moon_longitude: float,
    month_start: datetime,
    month_end: datetime,
) -> list[dict[str, Any]]:
    """Find dasha transitions (MD/AD/PD/SD) within the month."""
    from packages.context.src.dasha import (
        get_antardasha_sequence,
        get_mahadasha_sequence,
        get_pratyantardasha_sequence,
        get_sookshma_dasha_sequence,
    )

    transitions: list[dict[str, Any]] = []

    try:
        mahadashas = get_mahadasha_sequence(birth_datetime, moon_longitude)
    except Exception:
        return transitions

    for maha in mahadashas:
        # MD transition
        if month_start <= maha["start_date"] <= month_end:
            transitions.append(
                {
                    "date": maha["start_date"].strftime("%Y-%m-%d"),
                    "from": "previous MD",
                    "to": f"{maha['lord'].title()} Mahadasha",
                    "level": "mahadasha",
                }
            )

        # Check AD transitions
        if maha["start_date"] <= month_end and maha["end_date"] >= month_start:
            try:
                antardashas = get_antardasha_sequence(
                    maha["lord"],
                    maha["start_date"],
                    maha["end_date"],
                )
            except Exception:
                continue

            for i, antar in enumerate(antardashas):
                if month_start <= antar["start_date"] <= month_end:
                    prev_lord = antardashas[i - 1]["lord"] if i > 0 else "previous"
                    transitions.append(
                        {
                            "date": antar["start_date"].strftime("%Y-%m-%d"),
                            "from": f"{maha['lord'].title()}-{prev_lord.title()}",
                            "to": f"{maha['lord'].title()}-{antar['lord'].title()}",
                            "level": "antardasha",
                        }
                    )

                # Check PD transitions
                if antar["start_date"] <= month_end and antar["end_date"] >= month_start:
                    try:
                        pratyantars = get_pratyantardasha_sequence(
                            antar["lord"],
                            antar["start_date"],
                            antar["end_date"],
                        )
                    except Exception:
                        continue

                    for j, pd in enumerate(pratyantars):
                        if month_start <= pd["start_date"] <= month_end:
                            prev_pd = pratyantars[j - 1]["lord"] if j > 0 else "previous"
                            transitions.append(
                                {
                                    "date": pd["start_date"].strftime("%Y-%m-%d"),
                                    "from": f"{maha['lord'].title()}-{antar['lord'].title()}-{prev_pd.title()}",
                                    "to": f"{maha['lord'].title()}-{antar['lord'].title()}-{pd['lord'].title()}",
                                    "level": "pratyantardasha",
                                }
                            )

                        # Check SD transitions within each PD
                        if pd["start_date"] <= month_end and pd["end_date"] >= month_start:
                            try:
                                sookshmas = get_sookshma_dasha_sequence(
                                    pd["lord"],
                                    pd["start_date"],
                                    pd["end_date"],
                                )
                            except Exception:
                                continue

                            for k, sd in enumerate(sookshmas):
                                if month_start <= sd["start_date"] <= month_end:
                                    prev_sd = sookshmas[k - 1]["lord"] if k > 0 else "previous"
                                    transitions.append(
                                        {
                                            "date": sd["start_date"].strftime("%Y-%m-%d"),
                                            "from": f"SD: {prev_sd.title()}",
                                            "to": f"SD: {sd['lord'].title()}",
                                            "level": "sookshma",
                                        }
                                    )

    transitions.sort(key=lambda x: x["date"])
    return transitions


def _get_major_transits(
    natal_planets: dict[str, dict[str, Any]],  # noqa: ARG001
    lagna_rashi: str,
    start_date: datetime,
    days: int,
) -> list[dict[str, Any]]:
    """Find major transit events during the month.

    Checks sign ingresses, close aspects, and stations.
    """
    from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

    lagna_idx = _get_rashi_index(lagna_rashi)
    major_transits: list[dict[str, Any]] = []
    prev_positions: dict[str, dict[str, Any]] | None = None
    seen: set[str] = set()

    slow_planets = ["saturn", "jupiter", "mars", "rahu", "ketu", "sun", "venus", "mercury"]

    for day_offset in range(0, days + 1):
        check_dt = start_date + timedelta(days=day_offset)
        try:
            jd = get_julian_day(check_dt)
            curr = get_all_planets(jd)
        except Exception:
            continue

        if prev_positions is not None:
            for planet in slow_planets:
                if planet not in curr or planet not in prev_positions:
                    continue

                curr_rashi = int(curr[planet]["longitude"] // 30)
                prev_rashi = int(prev_positions[planet]["longitude"] // 30)

                # Sign ingress
                if curr_rashi != prev_rashi:
                    house = _house_from_lagna(curr_rashi, lagna_idx)
                    sign_name = RASHI_NAMES[curr_rashi] if 0 <= curr_rashi < 12 else "Unknown"
                    key = f"ingress_{planet}_{sign_name}"
                    if key not in seen:
                        seen.add(key)

                        # Determine house lord and effect
                        effect = (
                            f"{planet.title()} enters {sign_name.title()}, "
                            f"activating house {house} themes"
                        )

                        major_transits.append(
                            {
                                "date": check_dt.strftime("%Y-%m-%d"),
                                "event": f"{planet.title()} enters {sign_name.title()}",
                                "house": house,
                                "duration_days": _planet_sign_duration(planet),
                                "effect": effect,
                            }
                        )

        prev_positions = curr

    major_transits.sort(key=lambda x: x["date"])
    return major_transits


def _planet_sign_duration(planet: str) -> int:
    """Approximate days a planet stays in one sign."""
    durations = {
        "sun": 30,
        "moon": 2,
        "mercury": 25,
        "venus": 28,
        "mars": 45,
        "jupiter": 365,
        "saturn": 900,
        "rahu": 540,
        "ketu": 540,
    }
    return durations.get(planet.lower(), 30)


def _compute_weekly_summaries(
    natal_planets: dict[str, dict[str, Any]],  # noqa: ARG001
    lagna_rashi: str,  # noqa: ARG001
    month_start: datetime,
    num_days: int,
    birth_datetime: datetime,
    moon_longitude: float,
) -> list[dict[str, Any]]:
    """Compute 4 weekly summaries for the month.

    Uses a lightweight approach: sample mid-week panchanga + dasha
    quality for each week.
    """
    from packages.context.src.dasha import get_current_dasha

    weeks: list[dict[str, Any]] = []
    week_boundaries = _get_week_boundaries(month_start, num_days)

    for i, (w_start, w_end) in enumerate(week_boundaries, 1):
        mid_week = w_start + timedelta(days=3)
        mid_week_noon = datetime(mid_week.year, mid_week.month, mid_week.day, 12, 0, 0)

        # Sample dasha quality at mid-week
        week_rating = 5
        theme = "Steady progress"
        try:
            dasha = get_current_dasha(birth_datetime, moon_longitude, mid_week_noon)
            if dasha:
                md_q = _DASHA_LORD_QUALITY.get(dasha["mahadasha"]["lord"], 0)
                ad_q = _DASHA_LORD_QUALITY.get(dasha["antardasha"]["lord"], 0)
                dasha_score = (md_q + ad_q) / 2
                week_rating = max(1, min(10, round(5 + dasha_score * 2)))

                md_lord = dasha["mahadasha"]["lord"]
                ad_lord = dasha["antardasha"]["lord"]
                if dasha_score >= 0.5:
                    theme = f"Positive {md_lord.title()}-{ad_lord.title()} energy"
                elif dasha_score <= -0.3:
                    theme = f"Patience with {md_lord.title()}-{ad_lord.title()} period"
                else:
                    theme = f"Balanced {md_lord.title()}-{ad_lord.title()} focus"
        except Exception:
            pass

        date_label = f"{MONTH_NAMES[w_start.month - 1][:3]} {w_start.day}-{w_end.day}"

        weeks.append(
            {
                "week": i,
                "dates": date_label,
                "rating": week_rating,
                "theme": theme,
            }
        )

    return weeks


def _get_week_boundaries(
    month_start: datetime,
    num_days: int,
) -> list[tuple[datetime, datetime]]:
    """Split a month into approximately 4 weeks."""
    boundaries: list[tuple[datetime, datetime]] = []
    week_size = max(7, num_days // 4)
    current = month_start

    for _ in range(4):
        week_end = min(
            current + timedelta(days=week_size - 1), month_start + timedelta(days=num_days - 1)
        )
        boundaries.append((current, week_end))
        current = week_end + timedelta(days=1)
        if current > month_start + timedelta(days=num_days - 1):
            break

    return boundaries


def _compute_area_ratings_monthly(
    major_transits: list[dict[str, Any]],
    retro_info: dict[str, Any],
    dasha_md: str,  # noqa: ARG001
    dasha_ad: str,  # noqa: ARG001
    natal_planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    month_start: datetime,
    num_days: int,
    birth_datetime: str = "",
    birth_lat: float = 0.0,
    birth_lon: float = 0.0,
    moon_longitude: float = 0.0,
) -> dict[str, dict[str, Any]]:
    """Compute area ratings for the month by sampling state engine every 3rd day.

    Uses compute_state_vector() as single source of truth, sampling ~10 days
    and averaging area scores across samples.
    """
    import logging

    logger = logging.getLogger(__name__)
    areas: dict[str, dict[str, Any]] = {}

    # Sample state engine every 3rd day (~10 calls for a 30-day month)
    sampled_areas: dict[str, list[float]] = {area: [] for area in AREA_HOUSES}
    if birth_datetime and natal_planets:
        try:
            from packages.context.src.state_engine import compute_state_vector

            for day_offset in range(0, num_days, 3):
                sample_dt = month_start + timedelta(days=day_offset)
                try:
                    vec = compute_state_vector(
                        birth_datetime=birth_datetime,
                        birth_lat=birth_lat,
                        birth_lon=birth_lon,
                        natal_planets=natal_planets,
                        moon_longitude=moon_longitude,
                        lagna_rashi=lagna_rashi,
                        query_datetime=sample_dt.isoformat(),
                    )
                    for area in vec.get("areas", []):
                        area_id = area["id"]
                        if area_id in sampled_areas:
                            sampled_areas[area_id].append(float(area["score"]))
                except Exception as e:
                    logger.debug(f"State vector sample failed for {sample_dt}: {e}")
        except Exception as e:
            logger.warning(f"State engine import failed for monthly areas: {e}")

    for area_id, houses in AREA_HOUSES.items():
        scores = sampled_areas.get(area_id, [])
        avg_score = sum(scores) / len(scores) if scores else 5.0

        rating = max(1, min(10, round(avg_score)))

        # Best/avoid dates from transit events
        best_dates = []
        avoid_dates = []
        for transit in major_transits:
            house = transit.get("house", 0)
            date_str = transit.get("date", "")
            planet_name = (
                transit.get("event", "").split()[0].lower() if transit.get("event") else ""
            )
            if house in houses and planet_name in ("jupiter", "venus"):
                best_dates.append(date_str)
            elif house in houses and planet_name in ("saturn", "mars", "rahu"):
                avoid_dates.append(date_str)

        summary = _monthly_area_summary(area_id, rating, retro_info.get("planets_retrograde", []))

        areas[area_id] = {
            "rating": rating,
            "score": round(avg_score, 1),
            "best_dates": best_dates[:3],
            "avoid_dates": avoid_dates[:3],
            "summary": summary,
        }

    return areas


def _monthly_area_summary(area: str, rating: int, retro_planets: list[str]) -> str:
    """Generate a monthly area summary."""
    if rating >= 8:
        tone = "Strong"
    elif rating >= 6:
        tone = "Positive"
    elif rating >= 4:
        tone = "Mixed"
    else:
        tone = "Challenging"

    area_labels = {
        "career": "career progress",
        "finance": "financial matters",
        "relationships": "relationship dynamics",
        "health": "health and vitality",
        "spiritual": "spiritual growth",
        "family": "family harmony",
        "education": "learning and studies",
        "travel": "travel and exploration",
    }
    label = area_labels.get(area, area)

    retro_note = ""
    area_planets = AREA_PLANETS.get(area, [])
    affected = [p for p in retro_planets if p in area_planets]
    if affected:
        retro_note = f" ({', '.join(p.title() for p in affected)} retrograde adds complexity)"

    return f"{tone} month for {label}{retro_note}"


def _compute_best_dates(
    major_transits: list[dict[str, Any]],
    weekly_summaries: list[dict[str, Any]],  # noqa: ARG001
    month_start: datetime,  # noqa: ARG001
    num_days: int,  # noqa: ARG001
) -> dict[str, list[str]]:
    """Determine best dates for various activities based on transit data."""
    best_dates: dict[str, list[str]] = {
        "career_moves": [],
        "financial": [],
        "travel": [],
        "spiritual": [],
        "avoid_important": [],
    }

    # Find dates with beneficial planet ingresses
    for transit in major_transits:
        event = transit.get("event", "").lower()
        date_str = transit.get("date", "")
        house = transit.get("house", 0)

        if "jupiter" in event:
            best_dates["career_moves"].append(date_str)
            best_dates["spiritual"].append(date_str)
        if "venus" in event:
            best_dates["financial"].append(date_str)
        if house in (3, 9, 12):
            best_dates["travel"].append(date_str)
        if "saturn" in event or "rahu" in event:
            best_dates["avoid_important"].append(date_str)

    # Limit to 3 per category
    for key in best_dates:
        best_dates[key] = best_dates[key][:3]

    return best_dates


def get_monthly_forecast(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, dict[str, Any]],
    moon_longitude: float,
    lagna_rashi: str,
    month: int | None = None,
    year: int | None = None,
    location_lat: float | None = None,  # noqa: ARG001
    location_lon: float | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """Generate a comprehensive monthly forecast.

    Analyzes major transits, dasha transitions, retrograde status,
    area-wise ratings, weekly summaries, and key dates.

    Args:
        birth_datetime: ISO-format birth datetime string
        birth_lat: Birth latitude (reserved for future use)
        birth_lon: Birth longitude (reserved for future use)
        natal_planets: Birth chart planet positions
        moon_longitude: Natal Moon longitude (degrees)
        lagna_rashi: Ascendant sign name (e.g. "libra")
        month: Month number (1-12), defaults to current
        year: Year, defaults to current
        location_lat: Current location latitude (reserved for future use)
        location_lon: Current location longitude (reserved for future use)

    Returns:
        Monthly forecast dictionary.
    """
    from packages.context.src.dasha import get_current_dasha

    now = datetime.now()
    target_month = month if month is not None else now.month
    target_year = year if year is not None else now.year

    num_days = calendar.monthrange(target_year, target_month)[1]
    month_start = datetime(target_year, target_month, 1)
    month_end = datetime(target_year, target_month, num_days, 23, 59, 59)

    birth_dt = datetime.fromisoformat(birth_datetime)

    # ---- 1. Current dasha context ----
    dasha_md = "unknown"
    dasha_ad = "unknown"
    try:
        mid_month = datetime(target_year, target_month, 15, 12, 0, 0)
        dasha_info = get_current_dasha(birth_dt, moon_longitude, mid_month)
        if dasha_info:
            dasha_md = dasha_info["mahadasha"]["lord"]
            dasha_ad = dasha_info["antardasha"]["lord"]
    except Exception:
        dasha_info = None

    # ---- 2. Dasha transitions ----
    dasha_transitions = _get_dasha_transitions(birth_dt, moon_longitude, month_start, month_end)

    dasha_pd = "unknown"
    dasha_sd = "unknown"
    if dasha_info:
        if dasha_info.get("pratyantardasha"):
            dasha_pd = dasha_info["pratyantardasha"]["lord"]
        if dasha_info.get("sookshma_dasha"):
            dasha_sd = dasha_info["sookshma_dasha"]["lord"]

    dasha_context: dict[str, Any] = {
        "mahadasha": dasha_md,
        "antardasha": dasha_ad,
        "pratyantardasha": dasha_pd,
        "sookshma": dasha_sd,
        "transitions": dasha_transitions,
    }

    # ---- 3. Major transits ----
    major_transits = _get_major_transits(natal_planets, lagna_rashi, month_start, num_days)

    # ---- 4. Retrograde status ----
    retrograde_status = _detect_retrogrades(month_start, num_days)

    # ---- 5. Area ratings ----
    area_ratings = _compute_area_ratings_monthly(
        major_transits,
        retrograde_status,
        dasha_md,
        dasha_ad,
        natal_planets,
        lagna_rashi,
        month_start,
        num_days,
        birth_datetime=birth_datetime,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        moon_longitude=moon_longitude,
    )

    # ---- 6. Weekly summaries ----
    weekly_summaries = _compute_weekly_summaries(
        natal_planets,
        lagna_rashi,
        month_start,
        num_days,
        birth_dt,
        moon_longitude,
    )

    # ---- 7. Best dates ----
    best_dates = _compute_best_dates(major_transits, weekly_summaries, month_start, num_days)

    # ---- 8. Overall rating ----
    area_avg = sum(a["rating"] for a in area_ratings.values()) / max(len(area_ratings), 1)
    dasha_quality = (
        _DASHA_LORD_QUALITY.get(dasha_md, 0) + _DASHA_LORD_QUALITY.get(dasha_ad, 0)
    ) / 2.0
    overall_rating = round(
        max(1.0, min(10.0, area_avg * 0.6 + (5 + dasha_quality * 2) * 0.4)),
        1,
    )

    # ---- 9. Monthly theme + summary + recommendations (knowledge-backed) ----
    # Derive best/weakest areas
    sorted_areas = sorted(area_ratings.items(), key=lambda x: x[1]["rating"], reverse=True)
    best_area = sorted_areas[0][0] if sorted_areas else None
    weakest_area = sorted_areas[-1][0] if sorted_areas else None

    # Derive double-transit houses from area_scores that have double_transit
    double_transit_houses: list[int] = []
    for _area_id, area_data in area_ratings.items():
        if area_data.get("double_transit"):
            for h in AREA_HOUSES.get(_area_id, []):
                if h not in double_transit_houses:
                    double_transit_houses.append(h)

    try:
        from packages.context.src.forecast_knowledge import (
            build_monthly_recommendations,
            build_monthly_summary,
        )

        monthly_theme = build_monthly_summary(
            month_rating=overall_rating,
            dasha_md=dasha_md,
            dasha_ad=dasha_ad,
            double_transit_houses=double_transit_houses,
            best_area=best_area,
            weakest_area=weakest_area,
        )
        monthly_recommendations = build_monthly_recommendations(
            dasha_md=dasha_md,
            dasha_ad=dasha_ad,
            double_transit_houses=double_transit_houses,
        )
    except Exception:
        monthly_theme = _generate_monthly_theme(
            overall_rating,
            dasha_md,
            dasha_ad,
            area_ratings,
            retrograde_status,
        )
        monthly_recommendations = []

    # ---- 10. Gochara monthly summary (sample mid-month) ----
    gochara_summary: list[dict[str, Any]] = []
    sade_sati_info: dict[str, Any] = {"active": False, "phase": None}
    active_yogas: list[str] = []
    active_doshas: list[str] = []
    try:
        from packages.context.src.state_engine import compute_state_vector
        from packages.context.src.transits import get_gochara

        mid_dt = datetime(target_year, target_month, 15, 12, 0, 0)
        mid_vec = compute_state_vector(
            birth_datetime=birth_datetime,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
            query_datetime=mid_dt.isoformat(),
        )
        active_yogas = mid_vec.get("natal_yogas", [])
        active_doshas = mid_vec.get("natal_doshas", [])
        sade_sati_info = mid_vec.get("sade_sati", {"active": False, "phase": None})

        # Get transit positions at mid-month for gochara
        from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

        jd = get_julian_day(mid_dt)
        transit_pos = get_all_planets(jd)
        natal_moon_rashi = int(moon_longitude // 30)
        transit_rashis = {p: int(d.get("longitude", 0) // 30) for p, d in transit_pos.items()}

        for planet_name, pdata in transit_pos.items():
            if planet_name == "moon":
                continue
            t_rashi = int(pdata.get("longitude", 0) // 30)
            gochara = get_gochara(natal_moon_rashi, planet_name, t_rashi, transit_rashis)
            gochara_summary.append(
                {
                    "planet": planet_name,
                    "sign": RASHI_NAMES[t_rashi] if 0 <= t_rashi < 12 else "unknown",
                    "house_from_moon": gochara.get("house_from_moon", 0),
                    "is_favorable": gochara.get("is_favorable", False),
                    "has_vedha": gochara.get("has_vedha", False),
                    "net_effect": gochara.get("net_effect", "neutral"),
                }
            )
    except Exception:
        pass

    # ---- 11. Abhijit muhurta dates (best days for important actions) ----
    muhurta_dates: list[dict[str, str]] = []
    try:
        from packages.context.src.muhurta import get_abhijit_muhurta
        from packages.cosmos.src.sunrise_sunset import get_sunrise_sunset

        # Sample 4 dates (one per week) for Abhijit muhurta times
        for week_offset in (3, 10, 17, 24):
            if week_offset >= num_days:
                break
            sample_dt = month_start + timedelta(days=week_offset)
            sun = get_sunrise_sunset(sample_dt, birth_lat, birth_lon)
            abhijit = get_abhijit_muhurta(sun["sunrise"], sun["sunset"])
            muhurta_dates.append(
                {
                    "date": sample_dt.strftime("%Y-%m-%d"),
                    "abhijit_start": abhijit["start"].strftime("%H:%M"),
                    "abhijit_end": abhijit["end"].strftime("%H:%M"),
                }
            )
    except Exception:
        pass

    return {
        "month": MONTH_NAMES[target_month - 1],
        "year": target_year,
        "overall_rating": overall_rating,
        "monthly_theme": monthly_theme,
        "summary": monthly_theme,  # Flutter reads "summary" from details
        "recommendations": monthly_recommendations,
        "month_rating": round(overall_rating),
        "best_area": best_area,
        "weakest_area": weakest_area,
        "dasha_context": dasha_context,
        "major_transits": major_transits,
        "retrograde_status": retrograde_status,
        "areas": area_ratings,
        "weekly_summaries": weekly_summaries,
        "best_dates": best_dates,
        "gochara_summary": gochara_summary,
        "active_yogas": active_yogas[:10],
        "active_doshas": active_doshas,
        "sade_sati": sade_sati_info,
        "muhurta_dates": muhurta_dates,
    }


def _generate_monthly_theme(
    overall_rating: float,
    dasha_md: str,
    dasha_ad: str,
    areas: dict[str, dict[str, Any]],
    retro: dict[str, Any],
) -> str:
    """Generate the monthly theme string."""
    sorted_areas = sorted(areas.items(), key=lambda x: x[1]["rating"], reverse=True)
    top_area = sorted_areas[0][0] if sorted_areas else "general"

    area_labels = {
        "career": "career advancement",
        "finance": "financial growth",
        "relationships": "relationship focus",
        "health": "health consciousness",
        "spiritual": "spiritual development",
        "family": "family harmony",
        "education": "learning and growth",
        "travel": "travel and exploration",
    }
    top_label = area_labels.get(top_area, top_area)

    retro_note = ""
    retro_planets = retro.get("planets_retrograde", [])
    if retro_planets:
        retro_note = f" (mindful of {', '.join(p.title() for p in retro_planets[:2])} retrograde)"

    if overall_rating >= 7:
        return f"Strong month for {top_label} with {dasha_md.title()}-{dasha_ad.title()} energy{retro_note}"
    elif overall_rating >= 5:
        return f"Balanced month favoring {top_label}{retro_note}"
    else:
        return f"Reflective month — focus on {top_label}, navigate challenges carefully{retro_note}"
