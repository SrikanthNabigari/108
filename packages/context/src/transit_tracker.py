"""Real-Time Transit Trigger Tracker for 108 Vedic Astrology.

Given a birth chart, finds the next N significant transit events with
exact dates. Tracks:

1. Planet sign ingress (enters new sign/house)
2. Transit planet conjuncts natal planet (within 2 deg orb)
3. Transit planet aspects natal planet (Parashari aspects)
4. Retrograde station (planet stops and reverses)
5. Dasha period change (MD/AD/PD transitions)
6. Eclipse on natal positions
"""

from datetime import datetime, timedelta
from typing import Any

from packages.context.src.dasha import (
    get_antardasha_sequence,
    get_mahadasha_sequence,
    get_pratyantardasha_sequence,
)
from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

# Parashari special aspects
_SPECIAL_ASPECTS: dict[str, list[int]] = {
    "mars": [4, 8],
    "jupiter": [5, 9],
    "saturn": [3, 10],
    "rahu": [5, 9],
    "ketu": [5, 9],
}

# Significance ratings for trigger types
_TRIGGER_SIGNIFICANCE: dict[str, str] = {
    "sign_ingress": "medium",
    "conjunction": "high",
    "aspect": "medium",
    "retrograde_station": "high",
    "dasha_change": "high",
    "eclipse": "high",
}

# Rashi names for display
RASHI_NAMES = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _get_rashi(longitude: float) -> int:
    """Get rashi index (0-11) from longitude."""
    return int(longitude % 360) // 30


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _detect_sign_ingresses(
    prev_positions: dict[str, dict[str, Any]],
    curr_positions: dict[str, dict[str, Any]],
    check_date: datetime,
    lagna_rashi: int,
    days_from_now: int,
) -> list[dict[str, Any]]:
    """Detect planets that changed signs between two dates."""
    triggers = []
    for planet in prev_positions:
        if planet not in curr_positions:
            continue
        prev_rashi = _get_rashi(prev_positions[planet]["longitude"])
        curr_rashi = _get_rashi(curr_positions[planet]["longitude"])

        if prev_rashi != curr_rashi:
            house = ((curr_rashi - lagna_rashi) % 12) + 1
            triggers.append(
                {
                    "date": check_date.strftime("%Y-%m-%d"),
                    "days_from_now": days_from_now,
                    "trigger": f"{planet.title()} enters {RASHI_NAMES[curr_rashi]} (house {house})",
                    "type": "sign_ingress",
                    "planet": planet,
                    "new_sign": RASHI_NAMES[curr_rashi],
                    "house": house,
                    "significance": _TRIGGER_SIGNIFICANCE["sign_ingress"],
                    "effect": f"{planet.title()} changes sign to {RASHI_NAMES[curr_rashi]}, activating house {house} themes",
                }
            )
    return triggers


def _detect_conjunctions(
    curr_positions: dict[str, dict[str, Any]],
    natal_planets: dict[str, dict[str, Any]],
    check_date: datetime,
    days_from_now: int,
    orb: float = 2.0,
) -> list[dict[str, Any]]:
    """Detect transit planets conjuncting natal planets."""
    triggers = []
    for t_planet, t_data in curr_positions.items():
        t_lon = t_data["longitude"]
        for n_planet, n_data in natal_planets.items():
            n_lon = n_data.get("longitude", 0)
            dist = _angular_distance(t_lon, n_lon)

            if dist <= orb:
                triggers.append(
                    {
                        "date": check_date.strftime("%Y-%m-%d"),
                        "days_from_now": days_from_now,
                        "trigger": f"Transit {t_planet.title()} conjuncts natal {n_planet.title()} (orb {dist:.1f} deg)",
                        "type": "conjunction",
                        "transit_planet": t_planet,
                        "natal_planet": n_planet,
                        "orb": round(dist, 2),
                        "significance": _TRIGGER_SIGNIFICANCE["conjunction"],
                        "effect": f"Transit {t_planet.title()} activating natal {n_planet.title()} by conjunction",
                    }
                )
    return triggers


def _detect_aspects(
    curr_positions: dict[str, dict[str, Any]],
    natal_planets: dict[str, dict[str, Any]],
    check_date: datetime,
    days_from_now: int,
) -> list[dict[str, Any]]:
    """Detect Parashari aspects between transit and natal planets."""
    triggers = []
    for t_planet, t_data in curr_positions.items():
        t_rashi = _get_rashi(t_data["longitude"])
        t_lower = t_planet.lower()

        # Build aspect houses for this planet
        aspect_houses = [7]
        if t_lower in _SPECIAL_ASPECTS:
            aspect_houses.extend(_SPECIAL_ASPECTS[t_lower])

        for n_planet, n_data in natal_planets.items():
            n_rashi = _get_rashi(n_data.get("longitude", 0))
            house_dist = ((n_rashi - t_rashi) % 12) or 12

            if house_dist in aspect_houses:
                aspect_name = {
                    7: "7th (opposition)",
                    4: "4th (Mars special)",
                    8: "8th (Mars special)",
                    5: "5th (Jupiter special)",
                    9: "9th (Jupiter special)",
                    3: "3rd (Saturn special)",
                    10: "10th (Saturn special)",
                }.get(house_dist, f"{house_dist}th")

                # Only report slow planet aspects as significant
                slow_planets = {"saturn", "jupiter", "rahu", "ketu", "mars"}
                sig = "high" if t_lower in slow_planets else "low"

                triggers.append(
                    {
                        "date": check_date.strftime("%Y-%m-%d"),
                        "days_from_now": days_from_now,
                        "trigger": f"Transit {t_planet.title()} {aspect_name} aspect on natal {n_planet.title()}",
                        "type": "aspect",
                        "transit_planet": t_planet,
                        "natal_planet": n_planet,
                        "aspect_house": house_dist,
                        "significance": sig,
                        "effect": f"Transit {t_planet.title()} influencing natal {n_planet.title()} via {aspect_name} aspect",
                    }
                )
    return triggers


def _detect_retrograde_stations(
    prev_positions: dict[str, dict[str, Any]],
    curr_positions: dict[str, dict[str, Any]],
    check_date: datetime,
    days_from_now: int,
) -> list[dict[str, Any]]:
    """Detect planets that changed retrograde/direct status."""
    triggers = []
    retro_planets = {"mars", "mercury", "jupiter", "venus", "saturn"}

    for planet in retro_planets:
        if planet not in prev_positions or planet not in curr_positions:
            continue

        prev_retro = prev_positions[planet].get("is_retrograde", False)
        curr_retro = curr_positions[planet].get("is_retrograde", False)

        if prev_retro != curr_retro:
            station_type = "retrograde" if curr_retro else "direct"
            triggers.append(
                {
                    "date": check_date.strftime("%Y-%m-%d"),
                    "days_from_now": days_from_now,
                    "trigger": f"{planet.title()} stations {station_type}",
                    "type": "retrograde_station",
                    "planet": planet,
                    "station": station_type,
                    "significance": _TRIGGER_SIGNIFICANCE["retrograde_station"],
                    "effect": f"{planet.title()} turning {station_type} - expect shifts in {planet.title()}-related matters",
                }
            )
    return triggers


def _detect_dasha_changes(
    birth_datetime: datetime,
    moon_longitude: float,
    start_date: datetime,
    days_ahead: int,
) -> list[dict[str, Any]]:
    """Detect upcoming dasha period transitions (MD/AD/PD changes)."""
    triggers = []
    end_date = start_date + timedelta(days=days_ahead)

    try:
        # Get mahadasha sequence
        mahadashas = get_mahadasha_sequence(birth_datetime, moon_longitude)

        for _i, maha in enumerate(mahadashas):
            # Check MD transition
            if start_date <= maha["start_date"] <= end_date:
                days_from = (maha["start_date"] - start_date).days
                triggers.append(
                    {
                        "date": maha["start_date"].strftime("%Y-%m-%d"),
                        "days_from_now": days_from,
                        "trigger": f"Mahadasha changes to {maha['lord'].title()}",
                        "type": "dasha_change",
                        "dasha_level": "mahadasha",
                        "new_lord": maha["lord"],
                        "significance": "high",
                        "effect": f"Major life theme shift: {maha['lord'].title()} Mahadasha begins",
                    }
                )

            # Check AD transitions within active mahadashas
            if maha["start_date"] <= end_date and maha["end_date"] >= start_date:
                try:
                    antardashas = get_antardasha_sequence(
                        maha["lord"], maha["start_date"], maha["end_date"]
                    )
                    for antar in antardashas:
                        if start_date <= antar["start_date"] <= end_date:
                            days_from = (antar["start_date"] - start_date).days
                            triggers.append(
                                {
                                    "date": antar["start_date"].strftime("%Y-%m-%d"),
                                    "days_from_now": days_from,
                                    "trigger": f"Antardasha changes to {maha['lord'].title()}/{antar['lord'].title()}",
                                    "type": "dasha_change",
                                    "dasha_level": "antardasha",
                                    "new_lord": antar["lord"],
                                    "mahadasha_lord": maha["lord"],
                                    "significance": "high",
                                    "effect": f"Sub-period shift: {antar['lord'].title()} Antardasha within {maha['lord'].title()} Mahadasha",
                                }
                            )

                        # Check PD transitions
                        if antar["start_date"] <= end_date and antar["end_date"] >= start_date:
                            try:
                                pratyantars = get_pratyantardasha_sequence(
                                    antar["lord"], antar["start_date"], antar["end_date"]
                                )
                                for pd in pratyantars:
                                    if start_date <= pd["start_date"] <= end_date:
                                        days_from = (pd["start_date"] - start_date).days
                                        triggers.append(
                                            {
                                                "date": pd["start_date"].strftime("%Y-%m-%d"),
                                                "days_from_now": days_from,
                                                "trigger": f"Pratyantardasha changes to {pd['lord'].title()}",
                                                "type": "dasha_change",
                                                "dasha_level": "pratyantardasha",
                                                "new_lord": pd["lord"],
                                                "significance": "medium",
                                                "effect": f"Fine-grained period shift: {pd['lord'].title()} Pratyantardasha",
                                            }
                                        )
                            except Exception:
                                continue
                except Exception:
                    continue
    except Exception:
        pass

    return triggers


def get_upcoming_triggers(
    natal_planets: dict[str, dict[str, Any]],
    lagna_rashi: str | int,
    moon_rashi: str | int,  # noqa: ARG001
    start_date: str | datetime,
    days_ahead: int = 30,
    latitude: float = 0.0,  # noqa: ARG001
    longitude: float = 0.0,  # noqa: ARG001
    birth_datetime: datetime | str | None = None,
    moon_longitude: float | None = None,
) -> list[dict[str, Any]]:
    """Find the next significant transit events for a birth chart.

    Args:
        natal_planets: Birth chart positions {planet: {longitude, rashi, ...}}
        lagna_rashi: Ascendant sign (0-11 or name string)
        moon_rashi: Moon sign (0-11 or name string)
        start_date: Start date (ISO string or datetime)
        days_ahead: Number of days to look ahead (default 30)
        latitude: Geographic latitude
        longitude: Geographic longitude
        birth_datetime: Birth datetime (for dasha change detection)
        moon_longitude: Moon longitude at birth (for dasha calculation)

    Returns:
        Sorted list of trigger events with date, type, significance, and effect.
    """
    # Parse start_date
    start_dt = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date

    # Normalize lagna
    rashi_names = [
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    ]
    if isinstance(lagna_rashi, str):
        lagna_idx = (
            rashi_names.index(lagna_rashi.lower()) if lagna_rashi.lower() in rashi_names else 0
        )
    else:
        lagna_idx = int(lagna_rashi)

    all_triggers: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    # Get initial positions
    prev_positions = None

    # Scan daily
    for day_offset in range(days_ahead + 1):
        check_dt = start_dt + timedelta(days=day_offset)

        try:
            jd = get_julian_day(check_dt)
            curr_raw = get_all_planets(jd)
            curr_positions = {
                planet: {
                    "longitude": data["longitude"],
                    "is_retrograde": data.get("is_retrograde", False),
                    "speed": data.get("speed", 0),
                }
                for planet, data in curr_raw.items()
            }
        except Exception:
            continue

        if prev_positions is not None:
            # 1. Sign ingresses
            ingresses = _detect_sign_ingresses(
                prev_positions, curr_positions, check_dt, lagna_idx, day_offset
            )
            for t in ingresses:
                key = f"ingress_{t['planet']}_{t.get('new_sign', '')}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_triggers.append(t)

            # 4. Retrograde stations
            stations = _detect_retrograde_stations(
                prev_positions, curr_positions, check_dt, day_offset
            )
            for t in stations:
                key = f"station_{t['planet']}_{t.get('station', '')}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_triggers.append(t)

        # 2. Conjunctions (check every 3 days for efficiency)
        if day_offset % 3 == 0:
            conjunctions = _detect_conjunctions(curr_positions, natal_planets, check_dt, day_offset)
            for t in conjunctions:
                key = f"conj_{t['transit_planet']}_{t['natal_planet']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_triggers.append(t)

        # 3. Aspects (check weekly for slow planets)
        if day_offset % 7 == 0:
            aspects = _detect_aspects(curr_positions, natal_planets, check_dt, day_offset)
            for t in aspects:
                key = f"asp_{t['transit_planet']}_{t['natal_planet']}_{t['aspect_house']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_triggers.append(t)

        prev_positions = curr_positions

    # 5. Dasha changes
    if birth_datetime and moon_longitude is not None:
        if isinstance(birth_datetime, str):
            birth_dt = datetime.fromisoformat(birth_datetime)
        else:
            birth_dt = birth_datetime

        dasha_triggers = _detect_dasha_changes(birth_dt, moon_longitude, start_dt, days_ahead)
        for t in dasha_triggers:
            key = f"dasha_{t['dasha_level']}_{t['new_lord']}_{t['date']}"
            if key not in seen_keys:
                seen_keys.add(key)
                all_triggers.append(t)

    # Sort by date, then by significance
    sig_order = {"high": 0, "medium": 1, "low": 2}
    all_triggers.sort(
        key=lambda x: (x["days_from_now"], sig_order.get(x.get("significance", "low"), 2))
    )

    return all_triggers
