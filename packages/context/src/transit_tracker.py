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
    NAKSHATRA_LORDS,
    get_antardasha_sequence,
    get_mahadasha_sequence,
    get_pratyantardasha_sequence,
)
from packages.core.src.knowledge_loader import get_transit_aspect_effects
from packages.cosmos.src.ephemeris import get_all_planets, get_ayanamsa, get_julian_day
from packages.cosmos.src.nakshatras import longitude_to_nakshatra

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


def _lookup_what(transit_planet: str, natal_planet: str, aspect_type: str = "conjunction") -> str:
    """Look up WHAT interpretation from knowledge for a transit-natal aspect."""
    try:
        knowledge = get_transit_aspect_effects()
        t = transit_planet.lower()
        n = natal_planet.lower()
        if knowledge and t in knowledge:
            planet_data = knowledge[t].get(n, {})
            if aspect_type in planet_data:
                return planet_data[aspect_type].get("effect", "")
    except Exception:
        pass
    return ""


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
        # Skip Moon conjunctions — too frequent (every ~2.5 days per planet)
        if t_planet.lower() == "moon":
            continue
        t_lon = t_data["longitude"]
        for n_planet, n_data in natal_planets.items():
            n_lon = n_data.get("longitude", 0)
            dist = _angular_distance(t_lon, n_lon)

            if dist <= orb:
                what = _lookup_what(t_planet, n_planet, "conjunction")
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
                        "what": what,
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

                # Map house distance to aspect type for knowledge lookup
                aspect_lookup = {7: "opposition", 4: "square", 8: "square"}.get(house_dist, "")
                what = _lookup_what(t_planet, n_planet, aspect_lookup) if aspect_lookup else ""

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
                        "what": what,
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

        # 2. Conjunctions (check every 3 days, skip day 0 — current aspects belong in snapshot)
        if day_offset >= 1 and day_offset % 3 == 0:
            conjunctions = _detect_conjunctions(curr_positions, natal_planets, check_dt, day_offset)
            for t in conjunctions:
                key = f"conj_{t['transit_planet']}_{t['natal_planet']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    all_triggers.append(t)

        # 3. Aspects (check weekly, skip day 0 — only report when sign change creates new aspect)
        if day_offset >= 7 and day_offset % 7 == 0:
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


def get_nakshatra_transit_triggers(
    significator_planets: list[str],
    start_date: datetime | str,
    end_date: datetime | str,
) -> list[dict[str, Any]]:
    """Find dates when Sun/Moon transit nakshatras ruled by significator planets.

    In KP astrology, events manifest when fast-moving planets (Sun, Moon) transit
    through nakshatras whose lords are significators of an event. Each Vimshottari
    lord rules exactly 3 nakshatras out of 27.

    Args:
        significator_planets: List of planet names that are significators
            (e.g. ["saturn", "venus", "mercury"]).
        start_date: Start of search window (ISO string or datetime).
        end_date: End of search window (ISO string or datetime).

    Returns:
        List of trigger dicts sorted by date, each containing:
        - date: ISO date string
        - planet: "sun" or "moon"
        - nakshatra: Nakshatra name (e.g. "Pushya")
        - nakshatra_lord: The significator planet being activated
        - type: "sun_nakshatra_trigger" or "moon_nakshatra_trigger"
        - precision: Approximate duration ("~13 days" for Sun, "~1 day" for Moon)
    """
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
    end_dt = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date

    # Build reverse map: planet -> set of nakshatra numbers
    planet_to_nakshatras: dict[str, list[int]] = {}
    for nak_num, lord in NAKSHATRA_LORDS.items():
        planet_to_nakshatras.setdefault(lord, []).append(nak_num)

    # Collect target nakshatra numbers from significator planets
    target_nakshatras: set[int] = set()
    sig_lower = [p.lower() for p in significator_planets]
    for planet in sig_lower:
        if planet in planet_to_nakshatras:
            target_nakshatras.update(planet_to_nakshatras[planet])

    if not target_nakshatras:
        return []

    triggers: list[dict[str, Any]] = []
    luminaries = ["sun", "moon"]

    # Track previous day's nakshatra per planet to detect changes
    prev_nak: dict[str, int] = {}

    total_days = (end_dt - start_dt).days
    for day_offset in range(total_days + 1):
        check_dt = start_dt + timedelta(days=day_offset)

        try:
            jd = get_julian_day(check_dt)
            positions = get_all_planets(jd)
            ayanamsa = get_ayanamsa(jd)
        except Exception:
            continue

        for body in luminaries:
            if body not in positions:
                continue

            tropical_lon = positions[body]["longitude"]
            sidereal_lon = (tropical_lon - ayanamsa) % 360

            nak_num = int(sidereal_lon / 13.333333333) + 1
            if nak_num > 27:
                nak_num = 27

            prev = prev_nak.get(body)
            prev_nak[body] = nak_num

            # Only emit on nakshatra change (or first day if already in target)
            if prev is not None and nak_num == prev:
                continue

            if nak_num in target_nakshatras:
                # Look up nakshatra name
                try:
                    nak_info = longitude_to_nakshatra(sidereal_lon)
                    nak_name = nak_info["name"]
                except Exception:
                    nak_name = f"Nakshatra {nak_num}"

                # Find which significator lord this nakshatra belongs to
                nak_lord = NAKSHATRA_LORDS.get(nak_num, "unknown")

                triggers.append(
                    {
                        "date": check_dt.strftime("%Y-%m-%d"),
                        "planet": body,
                        "nakshatra": nak_name,
                        "nakshatra_lord": nak_lord,
                        "type": f"{body}_nakshatra_trigger",
                        "precision": "~13 days" if body == "sun" else "~1 day",
                    }
                )

    # Sort by date, then sun before moon
    body_order = {"sun": 0, "moon": 1}
    triggers.sort(key=lambda x: (x["date"], body_order.get(x["planet"], 2)))

    return triggers


# ── Ambient (slow-burn) transit signals ──
#
# Discrete-event triggers (above) only fire on ingresses, exact aspects, retros,
# and dasha changes. They miss the BPHS reality that a slow planet sitting in
# a house for months is the dominant timing signal — Jupiter in 9H is "the
# pilgrimage year" whether or not anything new happens this week.

# Slow planets and their typical sign-occupation duration in days
_SLOW_PLANETS = {
    "jupiter": 365,  # ~1 year per sign
    "saturn": 912,  # ~2.5 years per sign
    "rahu": 548,  # ~1.5 years per sign (retrograde)
    "ketu": 548,  # ~1.5 years per sign (retrograde)
}

# House → life-domain map used by ambient narrator (BPHS bhavas)
_HOUSE_DOMAINS: dict[int, list[str]] = {
    1: ["self", "vitality", "identity"],
    2: ["wealth", "family", "speech"],
    3: ["short journeys", "courage", "siblings"],
    4: ["home", "mother", "happiness"],
    5: ["children", "creativity", "intelligence", "purva-punya"],
    6: ["work", "health", "enemies", "debts"],
    7: ["spouse", "partnership", "business"],
    8: ["transformation", "longevity", "occult"],
    9: ["long journeys", "dharma", "guru", "fortune", "pilgrimage"],
    10: ["career", "status", "public role"],
    11: ["gains", "friends", "fulfillment"],
    12: ["foreign lands", "moksha", "isolation", "spiritual retreat", "expenses"],
}


def get_ambient_signals(
    natal_planets: dict[str, dict[str, Any]],  # noqa: ARG001 — reserved for natal-Saturn refinements
    lagna_rashi: str | int,
    moon_longitude: float,
    query_datetime: datetime | str | None = None,
    birth_datetime: datetime | str | None = None,
) -> dict[str, Any]:
    """Return the slow-burn transit picture: what's been true for weeks/months.

    Classical BPHS timing rests on three pillars: (1) the dasha lord's nature
    and current transit position, (2) the house occupation of slow benefics
    (Jupiter, Venus) and slow malefics (Saturn, Rahu, Ketu), and (3) functional
    lordship for the lagna. None of these change daily, so they don't appear in
    discrete-event triggers — but they ARE the dominant signal for "what
    domains are active right now." This function surfaces them.

    Args:
        natal_planets: {planet: {longitude, ...}} for at least the natal Moon.
        lagna_rashi: Lagna sign (name or 0-11 index).
        moon_longitude: Natal Moon longitude (0-360).
        query_datetime: Moment to evaluate (default: now).
        birth_datetime: Birth datetime (needed for dasha lord identification).

    Returns:
        {
          "query_date": ISO,
          "slow_transits": [ {planet, house_from_lagna, house_from_moon,
                              functional_nature, days_in_sign, days_until_exit,
                              activated_domains, themes} ],
          "dasha_lord_transits": [ {level, lord, house_from_lagna,
                                    house_from_moon, functional_nature, themes} ],
          "moon_signals": {janma_nakshatra_active: bool, chandra_ashtama: bool},
          "saturn_signals": {sade_sati_phase, kantaka_shani_house, ashtama_shani},
          "active_domains": [ {domain, weight, sources} ],   # cross-aggregated
        }
    """
    from packages.self.src.transit_lordship import classify_planet_role

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
        lagna_idx = int(lagna_rashi) % 12

    moon_rashi_idx = int(moon_longitude // 30) % 12

    if query_datetime is None:
        query_dt = datetime.now()
    elif isinstance(query_datetime, str):
        query_dt = datetime.fromisoformat(query_datetime)
    else:
        query_dt = query_datetime

    jd = get_julian_day(query_dt)
    raw = get_all_planets(jd)

    def _house_from(rashi_idx: int, ref_idx: int) -> int:
        return ((rashi_idx - ref_idx) % 12) + 1

    # ── Slow-planet narrator ──
    slow_transits: list[dict[str, Any]] = []
    for planet, typical_days in _SLOW_PLANETS.items():
        if planet not in raw:
            continue
        lon = float(raw[planet]["longitude"])
        rashi_idx = int(lon // 30) % 12
        deg_in_sign = lon % 30
        speed = float(raw[planet].get("speed", 0))
        is_retro = bool(raw[planet].get("is_retrograde", False)) or speed < 0

        house_lagna = _house_from(rashi_idx, lagna_idx)
        house_moon = _house_from(rashi_idx, moon_rashi_idx)

        # Estimate days remaining in current sign — coarse but useful
        if abs(speed) > 1e-6:
            if speed > 0:
                days_until_exit = int((30 - deg_in_sign) / speed)
            else:
                days_until_exit = int(deg_in_sign / abs(speed))
        else:
            days_until_exit = typical_days // 2
        days_in_sign = max(0, typical_days - days_until_exit)

        role = classify_planet_role(planet, lagna_idx)

        slow_transits.append(
            {
                "planet": planet,
                "rashi": rashi_names[rashi_idx],
                "is_retrograde": is_retro,
                "house_from_lagna": house_lagna,
                "house_from_moon": house_moon,
                "functional_nature": role["functional_nature"],
                "houses_ruled": role["houses_ruled"],
                "days_in_sign": days_in_sign,
                "days_until_exit": days_until_exit,
                "themes_lagna": _HOUSE_DOMAINS.get(house_lagna, []),
                "themes_moon": _HOUSE_DOMAINS.get(house_moon, []),
            }
        )

    # ── Dasha lord transit positions (BPHS: dasha lord's transit = manifestation) ──
    dasha_lord_transits: list[dict[str, Any]] = []
    if birth_datetime is not None:
        try:
            from packages.context.src.dasha import get_current_dasha

            if isinstance(birth_datetime, str):
                birth_dt = datetime.fromisoformat(birth_datetime)
            else:
                birth_dt = birth_datetime
            dasha = get_current_dasha(birth_dt, moon_longitude, query_dt)
            if dasha:
                for level in ("mahadasha", "antardasha", "pratyantardasha"):
                    info = dasha.get(level) or {}
                    lord = info.get("lord")
                    if not lord or lord not in raw:
                        continue
                    lon = float(raw[lord]["longitude"])
                    rashi_idx = int(lon // 30) % 12
                    h_lag = _house_from(rashi_idx, lagna_idx)
                    h_moon = _house_from(rashi_idx, moon_rashi_idx)
                    role = classify_planet_role(lord, lagna_idx)
                    dasha_lord_transits.append(
                        {
                            "level": level,
                            "lord": lord,
                            "rashi": rashi_names[rashi_idx],
                            "house_from_lagna": h_lag,
                            "house_from_moon": h_moon,
                            "functional_nature": role["functional_nature"],
                            "houses_ruled": role["houses_ruled"],
                            "themes_lagna": _HOUSE_DOMAINS.get(h_lag, []),
                            "is_in_own_lordship_house": h_lag in role["houses_ruled"],
                        }
                    )
        except Exception:
            pass

    # ── Moon signals ──
    moon_signals: dict[str, Any] = {}
    if "moon" in raw:
        transit_moon_lon = float(raw["moon"]["longitude"])
        natal_nak = int(moon_longitude // 13.333333333) % 27
        transit_nak = int(transit_moon_lon // 13.333333333) % 27
        transit_moon_rashi = int(transit_moon_lon // 30) % 12
        h_from_natal_moon = _house_from(transit_moon_rashi, moon_rashi_idx)
        moon_signals = {
            "janma_nakshatra_active": natal_nak == transit_nak,
            "chandra_ashtama": h_from_natal_moon == 8,
            "transit_house_from_moon": h_from_natal_moon,
        }

    # ── Saturn signals: Sade Sati phase, Kantaka Shani, Ashtama Shani ──
    saturn_signals: dict[str, Any] = {}
    if "saturn" in raw:
        sat_lon = float(raw["saturn"]["longitude"])
        sat_rashi = int(sat_lon // 30) % 12
        h_from_moon = _house_from(sat_rashi, moon_rashi_idx)
        sade_sati_phase: str | None = None
        if h_from_moon == 12:
            sade_sati_phase = "rising"
        elif h_from_moon == 1:
            sade_sati_phase = "peak"
        elif h_from_moon == 2:
            sade_sati_phase = "setting"
        saturn_signals = {
            "transit_house_from_moon": h_from_moon,
            "sade_sati_phase": sade_sati_phase,
            "in_sade_sati": sade_sati_phase is not None,
            "kantaka_shani": h_from_moon in (4, 7, 10),
            "ashtama_shani": h_from_moon == 8,
        }

    # ── Aggregate active domains (slow transits + dasha lord transits) ──
    domain_acc: dict[str, dict[str, Any]] = {}

    def _add(domain: str, weight: float, source: str) -> None:
        slot = domain_acc.setdefault(domain, {"weight": 0.0, "sources": []})
        slot["weight"] += weight
        slot["sources"].append(source)

    nature_weight = {
        "yogakaraka": 1.4,
        "benefic": 1.2,
        "neutral": 0.7,
        "malefic": 0.5,
        "maraka": 0.4,
    }
    planet_weight = {"jupiter": 2.0, "saturn": 1.6, "rahu": 1.4, "ketu": 1.4}

    for st in slow_transits:
        w = planet_weight.get(st["planet"], 1.0) * nature_weight.get(st["functional_nature"], 0.7)
        for d in st["themes_lagna"]:
            _add(d, w, f"{st['planet']} in H{st['house_from_lagna']}")
        # House lordship activation: domains of houses this planet rules
        for ruled in st["houses_ruled"]:
            for d in _HOUSE_DOMAINS.get(ruled, []):
                _add(
                    d,
                    w * 0.6,
                    f"{st['planet']} (lord of H{ruled}) transits H{st['house_from_lagna']}",
                )

    level_weight = {"mahadasha": 2.5, "antardasha": 1.8, "pratyantardasha": 1.0}
    for dl in dasha_lord_transits:
        w = level_weight.get(dl["level"], 1.0) * nature_weight.get(dl["functional_nature"], 0.7)
        for d in dl["themes_lagna"]:
            _add(d, w, f"{dl['level']} lord {dl['lord']} transits H{dl['house_from_lagna']}")
        for ruled in dl["houses_ruled"]:
            for d in _HOUSE_DOMAINS.get(ruled, []):
                _add(d, w * 0.7, f"{dl['lord']} (lord of H{ruled}) active in {dl['level']}")

    active_domains = [
        {"domain": d, "weight": round(v["weight"], 2), "sources": v["sources"][:5]}
        for d, v in sorted(domain_acc.items(), key=lambda x: -x[1]["weight"])
    ]

    return {
        "query_date": query_dt.isoformat(),
        "slow_transits": slow_transits,
        "dasha_lord_transits": dasha_lord_transits,
        "moon_signals": moon_signals,
        "saturn_signals": saturn_signals,
        "active_domains": active_domains[:15],
    }
