"""Varshaphal (Solar Return / Tajika) engine for 108 Vedic Astrology.

Implements annual horoscope calculations including:
- Solar return date calculation via Swiss Ephemeris
- Muntha progression
- Varshesha (Year Lord) determination
- Tajika yoga detection (all 16 yogas)
- Saham (sensitive point) calculation
- Annual Dreshkana (D3) and Trimshamsha (D30) analysis
- Natal-to-annual comparison
- Full Varshaphal analysis

Uses knowledge/rules/varshaphal_rules.json.
"""

from datetime import datetime
from typing import Any

import swisseph as swe

from packages.core.src.knowledge_loader import get_varshaphal_rules

_varshaphal_cache: dict[str, Any] | None = None


def _get_rules() -> dict[str, Any]:
    """Get cached varshaphal rules."""
    global _varshaphal_cache
    if _varshaphal_cache is None:
        _varshaphal_cache = get_varshaphal_rules()
    return _varshaphal_cache


# Rashi lords mapping (0=Aries..11=Pisces -> ruling planet)
RASHI_LORDS = {
    0: "mars",  # Aries
    1: "venus",  # Taurus
    2: "mercury",  # Gemini
    3: "moon",  # Cancer
    4: "sun",  # Leo
    5: "mercury",  # Virgo
    6: "venus",  # Libra
    7: "mars",  # Scorpio
    8: "jupiter",  # Sagittarius
    9: "saturn",  # Capricorn
    10: "saturn",  # Aquarius
    11: "jupiter",  # Pisces
}

# Day lords (0=Monday..6=Sunday)
DAY_LORDS = {
    0: "moon",  # Monday
    1: "mars",  # Tuesday
    2: "mercury",  # Wednesday
    3: "jupiter",  # Thursday
    4: "venus",  # Friday
    5: "saturn",  # Saturday
    6: "sun",  # Sunday
}


def calculate_muntha(birth_lagna_rashi: int, age: int) -> dict[str, Any]:
    """Calculate Muntha position for a given age.

    Muntha progresses one sign per year from the birth ascendant.

    Args:
        birth_lagna_rashi: Birth ascendant sign (0=Aries to 11=Pisces)
        age: Completed age (years since birth)

    Returns:
        Dictionary with muntha_rashi, house_from_lagna, and effects.
    """
    rules = _get_rules()
    muntha_data = rules.get("muntha", {})

    # Muntha sign: (lagna - 1 + age - 1) % 12 + 1 expressed as 0-indexed
    # More simply: lagna + (age % 12), wrapping around
    muntha_rashi = (birth_lagna_rashi + (age % 12)) % 12

    # House from lagna (1-12)
    house = ((muntha_rashi - birth_lagna_rashi) % 12) + 1

    house_effects = muntha_data.get("house_effects", {}).get(str(house), {})

    return {
        "muntha_rashi": muntha_rashi,
        "house_from_lagna": house,
        "theme": house_effects.get("theme", ""),
        "effects": house_effects.get("effects", []),
        "overall": house_effects.get("overall", "mixed"),
    }


def determine_varshesha(varshaphal_lagna_rashi: int) -> dict[str, Any]:
    """Determine Year Lord from the annual chart's ascendant.

    Simplified determination: uses the lord of the annual chart lagna sign.

    Args:
        varshaphal_lagna_rashi: Annual chart ascendant sign (0-11)

    Returns:
        Dictionary with year_lord and its effects.
    """
    rules = _get_rules()
    varshesha_data = rules.get("varshesha", {})

    year_lord = RASHI_LORDS.get(varshaphal_lagna_rashi, "sun")
    lord_effects = varshesha_data.get("year_lord_by_planet", {}).get(year_lord, {})

    return {
        "year_lord": year_lord,
        "lagna_rashi": varshaphal_lagna_rashi,
        "theme": lord_effects.get("theme", ""),
        "favorable": lord_effects.get("favorable", []),
        "unfavorable": lord_effects.get("unfavorable", []),
        "best_placement": lord_effects.get("best_placement", ""),
        "difficult_placement": lord_effects.get("difficult_placement", ""),
    }


def detect_tajika_yogas(planet_positions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect Tajika yogas in the Varshaphal chart.

    Checks 16 Tajika yoga conditions from the JSON rules.

    Args:
        planet_positions: Dict mapping planet name -> {longitude, rashi, house, ...}

    Returns:
        List of detected Tajika yogas with name, type, and effect.
    """
    rules = _get_rules()
    tajika_data = rules.get("tajika_yogas", {}).get("yogas", {})

    detected: list[dict[str, Any]] = []

    for yoga_id, yoga_info in tajika_data.items():
        # Check each yoga's condition based on available data
        is_present = _check_tajika_yoga(yoga_id, yoga_info, planet_positions)
        if is_present:
            detected.append(
                {
                    "yoga_id": yoga_id,
                    "name": yoga_info.get("name", yoga_id),
                    "type": yoga_info.get("type", "mixed"),
                    "condition": yoga_info.get("condition", ""),
                    "effect": yoga_info.get("effect", ""),
                }
            )

    return detected


def _angular_distance(lon1: float, lon2: float) -> float:
    """Calculate the shortest angular distance between two longitudes.

    Args:
        lon1: First longitude (0-360)
        lon2: Second longitude (0-360)

    Returns:
        Shortest angular distance (0-180)
    """
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


# Tajika aspect orbs: conjunction/opposition=15, square/trine=9, sextile=7
_TAJIKA_ASPECTS = {
    0: 15,  # conjunction
    60: 7,  # sextile
    90: 9,  # square
    120: 9,  # trine
    180: 15,  # opposition
}

# Average daily speeds (degrees/day) for speed-based yoga checks
_PLANET_SPEEDS = {
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

# Exaltation signs for planets (0-based rashi index)
_EXALTATION_SIGNS = {
    "sun": 0,
    "moon": 1,
    "mars": 9,
    "mercury": 5,
    "jupiter": 3,
    "venus": 11,
    "saturn": 6,
}

# Own signs for planets
_OWN_SIGNS = {
    "sun": {4},
    "moon": {3},
    "mars": {0, 7},
    "mercury": {2, 5},
    "jupiter": {8, 11},
    "venus": {1, 6},
    "saturn": {9, 10},
}

# Debilitation signs
_DEBILITATION_SIGNS = {
    "sun": 6,
    "moon": 7,
    "mars": 3,
    "mercury": 11,
    "jupiter": 9,
    "venus": 5,
    "saturn": 0,
}


def _has_tajika_aspect(lon1: float, lon2: float) -> bool:
    """Check if two planets are in Tajika aspect (within orb)."""
    dist = _angular_distance(lon1, lon2)
    return any(abs(dist - aspect_deg) <= orb for aspect_deg, orb in _TAJIKA_ASPECTS.items())


def _is_applying(faster_lon: float, slower_lon: float, faster_speed: float) -> bool:
    """Check if faster planet is applying to (approaching) slower planet."""
    diff = (slower_lon - faster_lon) % 360
    return diff < 180 and faster_speed > 0


def _check_tajika_yoga(
    yoga_id: str,
    _yoga_info: dict[str, Any],
    planet_positions: dict[str, dict[str, Any]],
) -> bool:
    """Check if a specific Tajika yoga is present.

    Implements detection for all 16 Tajika yogas based on house positions,
    planetary aspects, and longitudinal relationships.
    """
    kendra = {1, 4, 7, 10}
    trikona = {1, 5, 9}

    # Get year lord (assume ascendant lord is planet with house=1, or sun as fallback)
    year_lord_planet = None
    year_lord_house = None
    asc_lord_house = None

    for planet, data in planet_positions.items():
        house = data.get("house", 0)
        if house == 1 and year_lord_planet is None:
            year_lord_planet = planet.lower()
            year_lord_house = house
        if planet.lower() == "sun":
            asc_lord_house = data.get("house")

    sun_lon = planet_positions.get("sun", {}).get("longitude", 0)
    moon_data = planet_positions.get("moon", {})
    moon_lon = moon_data.get("longitude", 0)

    # ---- ikkabal ----
    if yoga_id == "ikkabal":
        if asc_lord_house and asc_lord_house in (kendra | trikona):
            return True

    # ---- induvara ----
    elif yoga_id == "induvara":
        houses = {data.get("house", 0) for data in planet_positions.values()}
        if houses and houses.issubset(kendra):
            return True

    # ---- ithasala ----
    elif yoga_id == "ithasala":
        # Faster planet applying to slower planet within Tajika aspect orb
        planets = list(planet_positions.items())
        for i, (p1, d1) in enumerate(planets):
            for p2, d2 in planets[i + 1 :]:
                lon1 = d1.get("longitude", 0)
                lon2 = d2.get("longitude", 0)
                if not _has_tajika_aspect(lon1, lon2):
                    continue
                s1 = _PLANET_SPEEDS.get(p1.lower(), 1.0)
                s2 = _PLANET_SPEEDS.get(p2.lower(), 1.0)
                faster, _slower = (p1, p2) if s1 > s2 else (p2, p1)
                flon = d1.get("longitude", 0) if faster == p1 else d2.get("longitude", 0)
                slon = d2.get("longitude", 0) if faster == p1 else d1.get("longitude", 0)
                fspeed = max(s1, s2)
                if _is_applying(flon, slon, fspeed):
                    return True

    # ---- ishrafa (easarapha) ----
    elif yoga_id == "ishrafa":
        # Faster planet separating from slower planet
        planets = list(planet_positions.items())
        for i, (p1, d1) in enumerate(planets):
            for p2, d2 in planets[i + 1 :]:
                lon1 = d1.get("longitude", 0)
                lon2 = d2.get("longitude", 0)
                if not _has_tajika_aspect(lon1, lon2):
                    continue
                s1 = _PLANET_SPEEDS.get(p1.lower(), 1.0)
                s2 = _PLANET_SPEEDS.get(p2.lower(), 1.0)
                faster = p1 if s1 > s2 else p2
                flon = d1.get("longitude", 0) if faster == p1 else d2.get("longitude", 0)
                slon = d2.get("longitude", 0) if faster == p1 else d1.get("longitude", 0)
                fspeed = max(s1, s2)
                if not _is_applying(flon, slon, fspeed):
                    return True

    # ---- nakta ----
    elif yoga_id == "nakta":
        # No direct ithasala between two significators, but a third planet
        # transfers light between them (collecting light)
        planets = list(planet_positions.items())
        for i, (_p1, d1) in enumerate(planets):
            for j, (_p2, d2) in enumerate(planets):
                if i == j:
                    continue
                lon1 = d1.get("longitude", 0)
                lon2 = d2.get("longitude", 0)
                if _has_tajika_aspect(lon1, lon2):
                    continue  # They already have direct aspect
                # Look for a third planet that aspects both
                for k, (_p3, d3) in enumerate(planets):
                    if k in (i, j):
                        continue
                    lon3 = d3.get("longitude", 0)
                    if _has_tajika_aspect(lon1, lon3) and _has_tajika_aspect(lon2, lon3):
                        return True

    # ---- yamaya ----
    elif yoga_id == "yamaya":
        # Two planets in mutual aspect but separating, with light transfer
        planets = list(planet_positions.items())
        for i, (p1, d1) in enumerate(planets):
            for j, (p2, d2) in enumerate(planets):
                if i >= j:
                    continue
                lon1 = d1.get("longitude", 0)
                lon2 = d2.get("longitude", 0)
                if not _has_tajika_aspect(lon1, lon2):
                    continue
                # Check if separating
                s1 = _PLANET_SPEEDS.get(p1.lower(), 1.0)
                s2 = _PLANET_SPEEDS.get(p2.lower(), 1.0)
                faster = p1 if s1 > s2 else p2
                flon = lon1 if faster == p1 else lon2
                slon = lon2 if faster == p1 else lon1
                if not _is_applying(flon, slon, max(s1, s2)):
                    # Separating; now check for light transfer via third
                    for k, (_p3, d3) in enumerate(planets):
                        if k in (i, j):
                            continue
                        lon3 = d3.get("longitude", 0)
                        if _has_tajika_aspect(lon1, lon3) or _has_tajika_aspect(lon2, lon3):
                            return True

    # ---- manau ----
    elif yoga_id == "manau":
        # No ithasala between significators AND no transfer of light possible
        if not planet_positions:
            return False
        planets = list(planet_positions.items())
        has_any_ithasala = False
        for i, (_p1, d1) in enumerate(planets):
            for _p2, d2 in planets[i + 1 :]:
                lon1 = d1.get("longitude", 0)
                lon2 = d2.get("longitude", 0)
                if _has_tajika_aspect(lon1, lon2):
                    has_any_ithasala = True
                    break
            if has_any_ithasala:
                break
        if not has_any_ithasala and len(planets) >= 2:
            return True

    # ---- kamboola ----
    elif yoga_id == "kamboola":
        # Moon in ithasala with year lord, year lord in kendra
        if year_lord_planet and year_lord_house in kendra:
            yl_data = planet_positions.get(year_lord_planet, {})
            yl_lon = yl_data.get("longitude", 0)
            if _has_tajika_aspect(moon_lon, yl_lon):
                moon_speed = _PLANET_SPEEDS.get("moon", 13.2)
                if _is_applying(moon_lon, yl_lon, moon_speed):
                    return True

    # ---- gairi_kamboola ----
    elif yoga_id == "gairi_kamboola":
        # Moon in ithasala with year lord, but year lord NOT in kendra
        if year_lord_planet and year_lord_house not in kendra:
            yl_data = planet_positions.get(year_lord_planet, {})
            yl_lon = yl_data.get("longitude", 0)
            if _has_tajika_aspect(moon_lon, yl_lon):
                moon_speed = _PLANET_SPEEDS.get("moon", 13.2)
                if _is_applying(moon_lon, yl_lon, moon_speed):
                    return True

    # ---- khallasara ----
    elif yoga_id == "khallasara":
        # Moon separating from both year lord and ascendant lord
        if not planet_positions:
            return False
        moon_speed = _PLANET_SPEEDS.get("moon", 13.2)
        separating_count = 0
        for planet, data in planet_positions.items():
            if planet.lower() == "moon":
                continue
            plon = data.get("longitude", 0)
            if _has_tajika_aspect(moon_lon, plon) and not _is_applying(moon_lon, plon, moon_speed):
                separating_count += 1
        if separating_count >= 2:
            return True

    # ---- radda ----
    elif yoga_id == "radda":
        # Retrograde planet forming ithasala
        for planet, data in planet_positions.items():
            if data.get("is_retrograde", False):
                plon = data.get("longitude", 0)
                for other, odata in planet_positions.items():
                    if other == planet:
                        continue
                    olon = odata.get("longitude", 0)
                    if _has_tajika_aspect(plon, olon):
                        return True

    # ---- duhphali_kuttha ----
    elif yoga_id == "duhphali_kuttha":
        # Significators in 6-8 or 2-12 positions from each other
        planets = list(planet_positions.items())
        for i, (_p1, d1) in enumerate(planets):
            h1 = d1.get("house", 0)
            for _p2, d2 in planets[i + 1 :]:
                h2 = d2.get("house", 0)
                if h1 == 0 or h2 == 0:
                    continue
                diff = ((h2 - h1) % 12) + 1
                rev_diff = ((h1 - h2) % 12) + 1
                # 6-8 relationship
                if (diff in (6, 8)) or (rev_diff in (6, 8)):
                    lon1 = d1.get("longitude", 0)
                    lon2 = d2.get("longitude", 0)
                    if not _has_tajika_aspect(lon1, lon2):
                        return True
                # 2-12 relationship
                if (diff in (2, 12)) or (rev_diff in (2, 12)):
                    lon1 = d1.get("longitude", 0)
                    lon2 = d2.get("longitude", 0)
                    if not _has_tajika_aspect(lon1, lon2):
                        return True

    # ---- dutthotthi_davira ----
    elif yoga_id == "dutthotthi_davira":
        # A planet in exaltation or own sign aspecting the ascendant (house 1)
        for planet, data in planet_positions.items():
            p_lower = planet.lower()
            rashi = data.get("rashi", -1)
            if isinstance(rashi, str):
                continue
            is_exalted = _EXALTATION_SIGNS.get(p_lower) == rashi
            is_own = rashi in _OWN_SIGNS.get(p_lower, set())
            if is_exalted or is_own:
                # Check aspect to house 1 (simplified: planet in kendra/trikona from house 1)
                house = data.get("house", 0)
                if house in (kendra | trikona) and house != 1:
                    return True

    # ---- tambira ----
    elif yoga_id == "tambira":
        # Year lord and asc lord in mutual kendra/trikona
        house_list = [data.get("house", 0) for data in planet_positions.values()]
        kendra_count = sum(1 for h in house_list if h in kendra)
        if kendra_count >= 3:
            return True

    # ---- kuttha ----
    elif yoga_id == "kuttha":
        # Year lord combust (close to Sun)
        for planet, data in planet_positions.items():
            if planet.lower() == "sun":
                continue
            lon = data.get("longitude", 0)
            dist = _angular_distance(lon, sun_lon)
            if dist < 15 and data.get("house") == asc_lord_house:
                return True

    # ---- durphali ----
    elif yoga_id == "durphali" and year_lord_planet:
        # Year lord in debilitation or enemy sign
        yl_data = planet_positions.get(year_lord_planet, {})
        rashi = yl_data.get("rashi", -1)
        if isinstance(rashi, int) and _DEBILITATION_SIGNS.get(year_lord_planet) == rashi:
            return True

    return False


def calculate_sahams(
    planet_longitudes: dict[str, float],
    lagna_lon: float,
    is_day_chart: bool = True,
) -> dict[str, dict[str, Any]]:
    """Calculate Saham (sensitive point) positions.

    Args:
        planet_longitudes: Dict mapping planet name -> longitude (0-360)
        lagna_lon: Ascendant longitude
        is_day_chart: True if birth is during daytime

    Returns:
        Dictionary of saham names -> {longitude, rashi, signifies}.
    """
    rules = _get_rules()
    saham_rules = rules.get("sahams", {}).get("points", {})

    sun_lon = planet_longitudes.get("sun", 0.0)
    moon_lon = planet_longitudes.get("moon", 0.0)
    mars_lon = planet_longitudes.get("mars", 0.0)
    mercury_lon = planet_longitudes.get("mercury", 0.0)
    jupiter_lon = planet_longitudes.get("jupiter", 0.0)
    venus_lon = planet_longitudes.get("venus", 0.0)
    saturn_lon = planet_longitudes.get("saturn", 0.0)

    # Calculate each saham using its formula
    formulas: dict[str, float] = {
        "punya_saham": (lagna_lon + moon_lon - sun_lon)
        if is_day_chart
        else (lagna_lon + sun_lon - moon_lon),
        "vidya_saham": lagna_lon + jupiter_lon - mercury_lon,
        "yashas_saham": lagna_lon + jupiter_lon - sun_lon,
        "mrityu_saham": lagna_lon + saturn_lon - moon_lon,
        "vivaha_saham": lagna_lon + venus_lon - saturn_lon,
        "santana_saham": lagna_lon + jupiter_lon - saturn_lon,
        "karma_saham": lagna_lon + saturn_lon - sun_lon,
        "rajya_saham": lagna_lon + saturn_lon - moon_lon,
        "roga_saham": lagna_lon + mars_lon - saturn_lon,
        "bandhu_saham": lagna_lon + mercury_lon - moon_lon,
    }

    result: dict[str, dict[str, Any]] = {}
    for saham_id, longitude in formulas.items():
        lon = longitude % 360
        rashi = int(lon / 30)
        saham_info = saham_rules.get(saham_id, {})

        result[saham_id] = {
            "name": saham_info.get("name", saham_id),
            "longitude": round(lon, 4),
            "rashi": rashi,
            "degree_in_rashi": round(lon % 30, 4),
            "signifies": saham_info.get("signifies", ""),
        }

    return result


def get_varshaphal_analysis(
    birth_lagna_rashi: int,
    age: int,
    varshaphal_lagna_rashi: int | None = None,
    planet_longitudes: dict[str, float] | None = None,
    lagna_lon: float = 0.0,
    is_day_chart: bool = True,
) -> dict[str, Any]:
    """Full Varshaphal (annual prediction) analysis.

    Args:
        birth_lagna_rashi: Birth chart ascendant sign (0-11)
        age: Completed age
        varshaphal_lagna_rashi: Annual chart lagna (0-11). If None, defaults to birth lagna.
        planet_longitudes: Planet longitudes in annual chart for saham calculation
        lagna_lon: Ascendant longitude for saham calculation
        is_day_chart: Whether birth/return is during daytime

    Returns:
        Comprehensive annual prediction dictionary.
    """
    # 1. Muntha
    muntha = calculate_muntha(birth_lagna_rashi, age)

    # 2. Varshesha
    vp_lagna = varshaphal_lagna_rashi if varshaphal_lagna_rashi is not None else birth_lagna_rashi
    varshesha = determine_varshesha(vp_lagna)

    # 3. Sahams (if planet positions provided)
    sahams = {}
    if planet_longitudes:
        sahams = calculate_sahams(planet_longitudes, lagna_lon, is_day_chart)

    # 4. Annual house effects
    rules = _get_rules()
    annual_effects = rules.get("annual_house_effects", {})

    # Get effects for the house Muntha falls in
    muntha_house = str(muntha["house_from_lagna"])
    muntha_annual = annual_effects.get(muntha_house, {})

    return {
        "age": age,
        "birth_lagna_rashi": birth_lagna_rashi,
        "varshaphal_lagna_rashi": vp_lagna,
        "muntha": muntha,
        "varshesha": varshesha,
        "sahams": sahams,
        "muntha_annual_themes": muntha_annual.get("themes", []),
        "annual_outlook": muntha["overall"],
    }


def calculate_solar_return_date(birth_sun_longitude: float, year: int) -> datetime:
    """Find the exact datetime when the Sun returns to the birth longitude in a given year.

    Uses Swiss Ephemeris with binary search to find the precise moment.

    Args:
        birth_sun_longitude: Sidereal Sun longitude at birth (0-360)
        year: Calendar year for which to find the solar return

    Returns:
        datetime of the solar return moment (UTC)

    Example:
        >>> dt = calculate_solar_return_date(227.5, 2025)
        >>> dt.year
        2025
    """
    # Set Lahiri ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Start search around the expected date (mid-year as initial guess)
    # Solar return typically falls within a few days of the birthday
    jd_start = swe.julday(year, 1, 1, 0.0)
    jd_end = swe.julday(year, 12, 31, 23.99)

    target = birth_sun_longitude % 360

    def _get_sid_sun_lon(jd: float) -> float:
        """Get sidereal Sun longitude for a given JD."""
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        result = swe.calc_ut(jd, swe.SUN, flags)
        return result[0][0] % 360

    # Coarse search: step through the year in 1-day increments
    # to find the approximate window where Sun crosses birth longitude
    prev_lon = _get_sid_sun_lon(jd_start)
    best_jd = jd_start
    best_diff = 360.0

    jd = jd_start
    while jd <= jd_end:
        cur_lon = _get_sid_sun_lon(jd)
        diff = _angular_distance(cur_lon, target)
        if diff < best_diff:
            best_diff = diff
            best_jd = jd

        # Detect crossing (longitude wraps around 360->0)
        if _crossed_target(prev_lon, cur_lon, target):
            best_jd = jd - 0.5  # Midpoint for refinement start
            break

        prev_lon = cur_lon
        jd += 1.0

    # Fine search: binary search to find exact JD within +/- 1 day
    jd_lo = best_jd - 1.0
    jd_hi = best_jd + 1.0

    for _ in range(60):  # 60 iterations gives sub-second precision
        jd_mid = (jd_lo + jd_hi) / 2.0
        mid_lon = _get_sid_sun_lon(jd_mid)
        diff = (mid_lon - target) % 360
        if diff > 180:
            diff -= 360

        if abs(diff) < 0.00001:  # ~0.036 arc-seconds precision
            break

        if diff > 0:
            jd_hi = jd_mid
        else:
            jd_lo = jd_mid

    # Convert JD to datetime
    result_jd = (jd_lo + jd_hi) / 2.0
    year_r, month_r, day_r, hour_r = swe.revjul(result_jd)
    h = int(hour_r)
    m = int((hour_r - h) * 60)
    s = int(((hour_r - h) * 60 - m) * 60)

    return datetime(int(year_r), int(month_r), int(day_r), h, m, s)


def _crossed_target(prev_lon: float, cur_lon: float, target: float) -> bool:
    """Check if the Sun crossed the target longitude between two JDs."""
    # Handle wrap-around at 360/0
    if abs(prev_lon - cur_lon) > 180:
        return False  # Probably a wrap, not a real crossing
    return (prev_lon <= target <= cur_lon) or (cur_lon <= target <= prev_lon)


def analyze_annual_dreshkana(varshaphal_chart: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Analyze the Dreshkana (D3) of the annual chart for courage and siblings.

    The Dreshkana divides each sign into 3 equal parts (10 degrees each).
    - 0-10: Mapped to same sign (movable triplicity)
    - 10-20: 5th sign from current
    - 20-30: 9th sign from current

    Args:
        varshaphal_chart: Dict mapping planet name -> {longitude, rashi, house, ...}

    Returns:
        Dictionary with d3 positions and interpretation.
    """
    d3_positions: dict[str, dict[str, Any]] = {}

    for planet, data in varshaphal_chart.items():
        lon = data.get("longitude", 0.0)
        rashi = int(lon / 30)
        degree_in_rashi = lon % 30

        if degree_in_rashi < 10:
            d3_rashi = rashi
        elif degree_in_rashi < 20:
            d3_rashi = (rashi + 4) % 12  # 5th from sign
        else:
            d3_rashi = (rashi + 8) % 12  # 9th from sign

        d3_positions[planet] = {
            "d3_rashi": d3_rashi,
            "original_rashi": rashi,
            "degree_in_rashi": round(degree_in_rashi, 4),
            "drekkana": 1 if degree_in_rashi < 10 else (2 if degree_in_rashi < 20 else 3),
        }

    # Interpretation based on Mars and 3rd house lord in D3
    mars_d3 = d3_positions.get("mars", {}).get("d3_rashi")
    sun_d3 = d3_positions.get("sun", {}).get("d3_rashi")

    themes = []
    if mars_d3 is not None:
        if mars_d3 in (0, 7):  # Mars in own D3 sign
            themes.append("Strong courage and initiative this year")
        elif mars_d3 in (3, 9):  # Mars in debilitation/exaltation D3
            themes.append("Variable energy levels, need for balanced action")

    if sun_d3 is not None and sun_d3 in (0, 4):  # Sun strong in D3
        themes.append("Leadership qualities enhanced")

    return {
        "d3_positions": d3_positions,
        "themes": themes or ["Moderate courage and sibling dynamics this year"],
        "focus": "courage, siblings, self-effort",
    }


def analyze_annual_trimshamsha(varshaphal_chart: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Analyze the Trimshamsha (D30) of the annual chart for misfortunes.

    The Trimshamsha divides each sign into 5 unequal parts:
    For odd signs: Mars(5), Saturn(5), Jupiter(8), Mercury(7), Venus(5)
    For even signs: Venus(5), Mercury(7), Jupiter(8), Saturn(5), Mars(5)

    Args:
        varshaphal_chart: Dict mapping planet name -> {longitude, rashi, house, ...}

    Returns:
        Dictionary with d30 positions and interpretation of potential misfortunes.
    """
    # Trimshamsha divisions for odd signs: cumulative boundaries
    _ODD_D30 = [
        (5, "mars"),
        (10, "saturn"),
        (18, "jupiter"),
        (25, "mercury"),
        (30, "venus"),
    ]
    _EVEN_D30 = [
        (5, "venus"),
        (12, "mercury"),
        (20, "jupiter"),
        (25, "saturn"),
        (30, "mars"),
    ]

    d30_positions: dict[str, dict[str, Any]] = {}

    for planet, data in varshaphal_chart.items():
        lon = data.get("longitude", 0.0)
        rashi = int(lon / 30)
        degree_in_rashi = lon % 30

        is_odd = rashi % 2 == 0  # 0-based: even index = odd sign (Aries, Gemini...)
        boundaries = _ODD_D30 if is_odd else _EVEN_D30

        d30_lord = "mars"
        for boundary, lord in boundaries:
            if degree_in_rashi < boundary:
                d30_lord = lord
                break

        d30_positions[planet] = {
            "d30_lord": d30_lord,
            "original_rashi": rashi,
            "degree_in_rashi": round(degree_in_rashi, 4),
        }

    # Interpretation: check if malefics are strong in D30
    warnings = []
    saturn_d30 = d30_positions.get("saturn", {}).get("d30_lord", "")
    mars_d30 = d30_positions.get("mars", {}).get("d30_lord", "")

    if saturn_d30 == "saturn":
        warnings.append("Saturn strong in D30: potential for chronic issues, delays")
    if mars_d30 == "mars":
        warnings.append("Mars strong in D30: accident risk, need caution")

    moon_d30 = d30_positions.get("moon", {}).get("d30_lord", "")
    if moon_d30 in ("mars", "saturn"):
        warnings.append("Moon afflicted in D30: emotional stress, health vigilance needed")

    return {
        "d30_positions": d30_positions,
        "warnings": warnings or ["No major misfortune indicators in D30"],
        "focus": "potential misfortunes, health risks, caution areas",
    }


def compare_natal_annual(
    natal_planets: dict[str, dict[str, Any]],
    annual_planets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compare natal planetary positions with annual chart positions.

    Key analysis: aspects between natal and annual lords of the same house,
    sign changes, and close conjunctions.

    Args:
        natal_planets: Dict mapping planet name -> {longitude, rashi, house, ...}
        annual_planets: Dict mapping planet name -> {longitude, rashi, house, ...}

    Returns:
        Dictionary with comparison results, sign changes, and aspect analysis.
    """
    comparisons: dict[str, dict[str, Any]] = {}
    sign_changes = []
    close_conjunctions = []
    house_changes = []

    for planet in natal_planets:
        if planet not in annual_planets:
            continue

        natal = natal_planets[planet]
        annual = annual_planets[planet]

        n_lon = natal.get("longitude", 0)
        a_lon = annual.get("longitude", 0)
        n_rashi = natal.get("rashi", 0)
        a_rashi = annual.get("rashi", 0)
        n_house = natal.get("house", 0)
        a_house = annual.get("house", 0)

        distance = _angular_distance(n_lon, a_lon)
        same_sign = n_rashi == a_rashi
        same_house = n_house == a_house

        comp = {
            "natal_longitude": n_lon,
            "annual_longitude": a_lon,
            "distance": round(distance, 4),
            "natal_rashi": n_rashi,
            "annual_rashi": a_rashi,
            "same_sign": same_sign,
            "natal_house": n_house,
            "annual_house": a_house,
            "same_house": same_house,
        }

        if not same_sign:
            sign_changes.append(planet)
            comp["event"] = "sign_change"

        if distance < 5:
            close_conjunctions.append(planet)
            comp["event"] = "close_return"

        if not same_house:
            house_changes.append(planet)

        comparisons[planet] = comp

    # Cross-planet aspects: check if natal planet A aspects annual planet B
    cross_aspects = []
    for n_planet, n_data in natal_planets.items():
        for a_planet, a_data in annual_planets.items():
            if n_planet == a_planet:
                continue
            n_lon = n_data.get("longitude", 0)
            a_lon = a_data.get("longitude", 0)
            dist = _angular_distance(n_lon, a_lon)
            # Check for major Tajika aspects
            for aspect_deg, orb in _TAJIKA_ASPECTS.items():
                if abs(dist - aspect_deg) <= orb:
                    aspect_name = {
                        0: "conjunction",
                        60: "sextile",
                        90: "square",
                        120: "trine",
                        180: "opposition",
                    }.get(aspect_deg, "")
                    cross_aspects.append(
                        {
                            "natal_planet": n_planet,
                            "annual_planet": a_planet,
                            "aspect": aspect_name,
                            "distance": round(dist, 4),
                        }
                    )
                    break

    # Summary interpretation
    themes = []
    if close_conjunctions:
        themes.append(f"Near-return for {', '.join(close_conjunctions)}: familiar themes resurface")
    if sign_changes:
        themes.append(
            f"Sign changes for {', '.join(sign_changes)}: new expressions of planetary energy"
        )
    if len(house_changes) > 4:
        themes.append("Major house shifts: significant change in life areas")

    return {
        "planet_comparisons": comparisons,
        "sign_changes": sign_changes,
        "close_conjunctions": close_conjunctions,
        "house_changes": house_changes,
        "cross_aspects": cross_aspects[:10],  # Limit to most relevant
        "themes": themes or ["Stable planetary patterns between natal and annual charts"],
    }


def get_current_varshaphal(
    birth_datetime: str | datetime,
    birth_lat: float,
    birth_lon: float,
    query_date: str | datetime | None = None,
) -> dict[str, Any]:
    """Calculate Varshaphal for the current solar year.

    Convenience function that calculates the solar return for the year
    containing query_date, then produces Muntha, Varshesha, Tajika yogas,
    and Sahams.

    Args:
        birth_datetime: Birth date and time (ISO string or datetime)
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        query_date: Date to analyze (ISO string, datetime, or None for today)

    Returns:
        Dictionary with solar_return_date, age, muntha, varshesha, tajika_yogas,
        sahams, and annual planet positions.
    """
    from packages.cosmos.src.ephemeris import (
        get_all_planets,
        get_house_cusps,
        get_julian_day,
    )

    # Parse dates
    if isinstance(birth_datetime, str):
        birth_dt = datetime.fromisoformat(birth_datetime)
    else:
        birth_dt = birth_datetime

    if query_date is None:
        query_dt = datetime.now()
    elif isinstance(query_date, str):
        query_dt = datetime.fromisoformat(query_date)
    else:
        query_dt = query_date

    # Calculate birth Sun longitude
    birth_jd = get_julian_day(birth_dt)
    birth_planets = get_all_planets(birth_jd)
    birth_sun_lon = birth_planets["sun"]["longitude"]

    # Get birth lagna
    birth_houses = get_house_cusps(birth_jd, birth_lat, birth_lon)
    birth_lagna_lon = birth_houses["ascendant"]
    birth_lagna_rashi = int(birth_lagna_lon // 30)

    # Determine the solar return year
    # The solar return for a given year happens when Sun returns to birth longitude
    # Use the query year as the solar return year
    sr_year = query_dt.year

    # Calculate solar return date
    sr_date = calculate_solar_return_date(birth_sun_lon, sr_year)

    # If the solar return hasn't happened yet this year, use previous year
    if sr_date > query_dt:
        sr_year -= 1
        sr_date = calculate_solar_return_date(birth_sun_lon, sr_year)

    # Age at solar return
    age = sr_year - birth_dt.year

    # Get solar return chart positions
    sr_jd = get_julian_day(sr_date)
    sr_planets_raw = get_all_planets(sr_jd)
    sr_houses = get_house_cusps(sr_jd, birth_lat, birth_lon)
    sr_lagna_lon = sr_houses["ascendant"]
    sr_lagna_rashi = int(sr_lagna_lon // 30)

    # Build planet position dict with house info
    sr_planet_positions = {}
    sr_planet_longitudes = {}
    for planet, data in sr_planets_raw.items():
        lon = data["longitude"]
        rashi = int(lon // 30)
        house = ((rashi - sr_lagna_rashi) % 12) + 1
        sr_planet_positions[planet] = {
            "longitude": lon,
            "rashi": rashi,
            "house": house,
            "is_retrograde": data.get("is_retrograde", False),
        }
        sr_planet_longitudes[planet] = lon

    # Determine if day chart (Sun above horizon)
    sun_house = sr_planet_positions.get("sun", {}).get("house", 1)
    is_day_chart = sun_house in (7, 8, 9, 10, 11, 12)  # Simplified: above-horizon houses

    # 1. Muntha
    muntha = calculate_muntha(birth_lagna_rashi, age)

    # 2. Varshesha
    varshesha = determine_varshesha(sr_lagna_rashi)

    # 3. Tajika yogas
    tajika_yogas = detect_tajika_yogas(sr_planet_positions)

    # 4. Sahams
    sahams = calculate_sahams(sr_planet_longitudes, sr_lagna_lon, is_day_chart)

    return {
        "solar_return_date": sr_date.strftime("%Y-%m-%d %H:%M:%S"),
        "solar_return_year": sr_year,
        "age": age,
        "birth_sun_longitude": round(birth_sun_lon, 4),
        "sr_lagna_rashi": sr_lagna_rashi,
        "sr_lagna_longitude": round(sr_lagna_lon, 4),
        "muntha": muntha,
        "varshesha": varshesha,
        "tajika_yogas": tajika_yogas,
        "sahams": sahams,
        "annual_planets": sr_planet_positions,
        "is_day_chart": is_day_chart,
    }
