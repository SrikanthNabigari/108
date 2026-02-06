"""Transit-to-Natal Aspect Engine for 108 Vedic Astrology.

Calculates when transiting planets form aspects to natal planet positions,
using both Western-style degree-based aspects and Vedic Parashari sign-based aspects.

Aspect types tracked:
- Conjunction (0 deg), Opposition (180 deg), Trine (120 deg), Square (90 deg), Sextile (60 deg)
- Parashari special: Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th

Each aspect is evaluated for:
- Exact orb (how close to exact the aspect is)
- Applying vs separating (approaching exactness or moving away)
- Effect description based on the planets involved
"""

from datetime import datetime, timedelta
from typing import Any

from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

# Standard Western aspects with default orbs
ASPECT_TYPES: dict[str, dict[str, Any]] = {
    "conjunction": {"degrees": 0, "default_orb": 8.0, "nature": "major"},
    "opposition": {"degrees": 180, "default_orb": 8.0, "nature": "major"},
    "trine": {"degrees": 120, "default_orb": 7.0, "nature": "major"},
    "square": {"degrees": 90, "default_orb": 7.0, "nature": "major"},
    "sextile": {"degrees": 60, "default_orb": 5.0, "nature": "minor"},
}

# Parashari special aspects (house-based, not degree-based)
PARASHARI_SPECIAL: dict[str, list[int]] = {
    "mars": [4, 8],
    "jupiter": [5, 9],
    "saturn": [3, 10],
}

# Planet speeds for applying/separating determination (degrees per day)
_PLANET_SPEEDS: dict[str, float] = {
    "sun": 1.0,
    "moon": 13.2,
    "mars": 0.52,
    "mercury": 1.38,
    "jupiter": 0.08,
    "venus": 1.2,
    "saturn": 0.03,
    "rahu": 0.05,
    "ketu": 0.05,
}

# Effect descriptions for transit aspects
_TRANSIT_ASPECT_EFFECTS: dict[str, dict[str, str]] = {
    "saturn": {
        "sun": "Tests authority, discipline in career, health caution",
        "moon": "Emotional heaviness, mental discipline, patience needed",
        "mars": "Frustration, delayed action, need for careful planning",
        "mercury": "Serious thinking, communication blocks, focused study",
        "jupiter": "Structured growth, disciplined expansion, karmic duty",
        "venus": "Relationship tests, financial discipline, delayed pleasure",
        "saturn": "Saturn return, major life restructuring, karmic accounting",
    },
    "jupiter": {
        "sun": "Expansion of self, leadership opportunities, optimism",
        "moon": "Emotional growth, family blessings, inner peace",
        "mars": "Energetic expansion, bold ventures, confident action",
        "mercury": "Intellectual growth, educational success, good communication",
        "jupiter": "Jupiter return, wisdom peak, spiritual expansion",
        "venus": "Relationship blessings, financial growth, artistic success",
        "saturn": "Balanced growth, wise discipline, structural improvement",
    },
    "mars": {
        "sun": "Energy surge, action drive, courage tested",
        "moon": "Emotional intensity, impulsive reactions, physical energy",
        "mars": "Mars return, high energy, conflict potential",
        "mercury": "Sharp thinking, argumentative, quick decisions",
        "jupiter": "Courageous expansion, bold faith, warrior spirit",
        "venus": "Passionate attraction, impulsive spending, creative fire",
        "saturn": "Frustration with limits, need for patience, controlled force",
    },
}


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _check_aspect(lon1: float, lon2: float, orb: float) -> list[dict[str, Any]]:
    """Check if two longitudes form any standard aspect within the given orb.

    Returns list of matching aspects.
    """
    dist = _angular_distance(lon1, lon2)
    matches = []

    for name, info in ASPECT_TYPES.items():
        target_deg = info["degrees"]
        aspect_orb = min(orb, info["default_orb"])
        diff_from_exact = abs(dist - target_deg)

        if diff_from_exact <= aspect_orb:
            matches.append(
                {
                    "aspect_type": name,
                    "aspect_degree": target_deg,
                    "orb": round(diff_from_exact, 2),
                    "exact": diff_from_exact < 1.0,
                }
            )

    return matches


def _is_applying(transit_lon: float, natal_lon: float, transit_speed: float) -> bool:
    """Determine if the transit planet is applying to (approaching) the natal position."""
    diff = (natal_lon - transit_lon) % 360
    if diff > 180:
        diff -= 360
    # If diff is positive and planet moving forward (positive speed), it's applying
    if transit_speed > 0 and 0 < diff < 180:
        return True
    return bool(transit_speed < 0 and -180 < diff < 0)


def _get_effect(transit_planet: str, natal_planet: str) -> str:
    """Get effect description for a transit-natal aspect."""
    t = transit_planet.lower()
    n = natal_planet.lower()
    planet_effects = _TRANSIT_ASPECT_EFFECTS.get(t, {})
    if n in planet_effects:
        return planet_effects[n]
    # Try reverse
    planet_effects = _TRANSIT_ASPECT_EFFECTS.get(n, {})
    if t in planet_effects:
        return planet_effects[t]
    return f"Transit {t.title()} activating natal {n.title()}"


def get_transit_natal_aspects(
    natal_planets: dict[str, dict[str, Any]],
    transit_planets: dict[str, dict[str, Any]],
    orb: float = 5.0,
) -> list[dict[str, Any]]:
    """Calculate all aspects between transiting and natal planets.

    Args:
        natal_planets: Birth chart positions {planet: {longitude, rashi, ...}}
        transit_planets: Current transit positions {planet: {longitude, rashi, ...}}
        orb: Maximum orb in degrees (default 5.0)

    Returns:
        List of aspect dictionaries with transit_planet, natal_planet,
        aspect_type, aspect_degree, orb, applying, transit_house,
        natal_house, and effect.
    """
    aspects: list[dict[str, Any]] = []

    for t_planet, t_data in transit_planets.items():
        t_lon = t_data.get("longitude", 0.0)
        t_speed = t_data.get("speed", _PLANET_SPEEDS.get(t_planet.lower(), 1.0))
        t_rashi = t_data.get("rashi")
        if t_rashi is None:
            t_rashi = int(t_lon // 30)

        for n_planet, n_data in natal_planets.items():
            n_lon = n_data.get("longitude", 0.0)
            n_rashi = n_data.get("rashi")
            if n_rashi is None:
                n_rashi = int(n_lon // 30)

            # Check standard aspects
            matches = _check_aspect(t_lon, n_lon, orb)

            for match in matches:
                applying = _is_applying(t_lon, n_lon, t_speed)
                effect = _get_effect(t_planet, n_planet)

                aspects.append(
                    {
                        "transit_planet": t_planet.lower(),
                        "natal_planet": n_planet.lower(),
                        "aspect_type": match["aspect_type"],
                        "aspect_degree": match["aspect_degree"],
                        "orb": match["orb"],
                        "exact": match["exact"],
                        "applying": applying,
                        "transit_rashi": t_rashi,
                        "natal_rashi": n_rashi,
                        "effect": effect,
                    }
                )

            # Check Parashari special aspects (sign-based)
            if t_planet.lower() in PARASHARI_SPECIAL:
                special_houses = PARASHARI_SPECIAL[t_planet.lower()]
                if isinstance(t_rashi, int) and isinstance(n_rashi, int):
                    house_dist = ((n_rashi - t_rashi) % 12) or 12
                    if house_dist in special_houses:
                        # Don't duplicate if already found via degree-based check
                        already_found = any(
                            a["transit_planet"] == t_planet.lower()
                            and a["natal_planet"] == n_planet.lower()
                            for a in aspects
                        )
                        if not already_found:
                            effect = _get_effect(t_planet, n_planet)
                            aspects.append(
                                {
                                    "transit_planet": t_planet.lower(),
                                    "natal_planet": n_planet.lower(),
                                    "aspect_type": f"parashari_{house_dist}th",
                                    "aspect_degree": house_dist * 30,
                                    "orb": 0.0,
                                    "exact": False,
                                    "applying": False,
                                    "transit_rashi": t_rashi,
                                    "natal_rashi": n_rashi,
                                    "effect": effect,
                                }
                            )

    # Sort by orb (tightest aspects first)
    aspects.sort(key=lambda x: x["orb"])
    return aspects


def find_upcoming_aspects(
    natal_planets: dict[str, dict[str, Any]],
    start_date: str | datetime,
    days_ahead: int = 30,
    latitude: float = 0.0,  # noqa: ARG001
    longitude: float = 0.0,  # noqa: ARG001
    orb: float = 3.0,
) -> list[dict[str, Any]]:
    """Find all transit-natal aspects in the next N days with approximate dates.

    Scans at daily intervals to find when transit planets form aspects
    to natal positions.

    Args:
        natal_planets: Birth chart positions {planet: {longitude, ...}}
        start_date: Start date (ISO string or datetime)
        days_ahead: Number of days to scan ahead (default 30)
        latitude: Geographic latitude
        longitude: Geographic longitude
        orb: Maximum orb for aspect detection (default 3.0 for tighter scan)

    Returns:
        List of upcoming aspects with date, planets, type, and effect.
    """
    start_dt = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date

    upcoming: list[dict[str, Any]] = []
    seen: set[str] = set()  # Avoid duplicate aspects on consecutive days

    for day_offset in range(days_ahead):
        check_dt = start_dt + timedelta(days=day_offset)

        try:
            jd = get_julian_day(check_dt)
            transit_raw = get_all_planets(jd)

            # Convert to expected format
            transits = {}
            for planet, data in transit_raw.items():
                transits[planet] = {
                    "longitude": data["longitude"],
                    "rashi": int(data["longitude"] // 30),
                    "speed": data.get("speed", 0),
                }

            aspects = get_transit_natal_aspects(natal_planets, transits, orb=orb)

            for asp in aspects:
                key = f"{asp['transit_planet']}-{asp['natal_planet']}-{asp['aspect_type']}"
                if key not in seen:
                    seen.add(key)
                    asp["date"] = check_dt.strftime("%Y-%m-%d")
                    asp["days_from_now"] = day_offset
                    upcoming.append(asp)
        except Exception:
            continue

    # Sort by days from now, then by orb
    upcoming.sort(key=lambda x: (x["days_from_now"], x["orb"]))
    return upcoming
