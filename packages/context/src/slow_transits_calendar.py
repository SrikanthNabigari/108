"""Slow-Transits Calendar — Saturn / Jupiter / Rahu sign-ingresses for the
customer's next 20 years.

The slow planets are the "weather system" of life events. Saturn changes
sign every ~2.5 years, Jupiter every ~1 year, Rahu/Ketu every ~1.5 years.
Each ingress changes which house they activate from your Lagna and Moon —
that's when life themes shift in a way you can FEEL.

This module finds every ingress in a 20-year window and tags it with:
  - planet · sign entered · house from Lagna · house from Moon
  - whether it activates a key natal placement (planets/Lagna lord)
  - classical reading of "this planet in that house from natal"

Output drives both the Life Story Spine and inline transit-context for
year-ahead forecasts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Sign names by index 0-11
_SIGNS = [
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


def _strip_tz(dt):
    if isinstance(dt, str):
        d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return d.replace(tzinfo=None) if d.tzinfo else d
    if hasattr(dt, "tzinfo") and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt


def _find_planet_ingresses(
    planet: str,
    start: datetime,
    end: datetime,
    step_days: int = 7,
) -> list[tuple[datetime, int]]:
    """Find all sign-ingresses for a planet between start and end.

    Returns list of (date, new_sign_idx) pairs. Sweeps in steps; when sign
    changes, binary-searches to the day for accuracy.
    """
    from packages.cosmos.src.ephemeris import (
        get_all_planets,
        get_ayanamsa,
        get_julian_day,
    )

    ingresses: list[tuple[datetime, int]] = []

    def _sign_at(dt: datetime) -> int:
        jd = get_julian_day(dt)
        ayan = get_ayanamsa(jd, "lahiri")
        planets = get_all_planets(jd, ayanamsa=ayan)
        p = planets.get(planet)
        if not p:
            return -1
        return int(float(p["longitude"]) // 30) % 12

    cur = start
    prev_sign = _sign_at(cur)
    if prev_sign < 0:
        return []
    while cur < end:
        nxt = cur + timedelta(days=step_days)
        if nxt > end:
            nxt = end
        next_sign = _sign_at(nxt)
        if next_sign != prev_sign and next_sign >= 0:
            # Binary-search to the day
            lo, hi = cur, nxt
            while (hi - lo).days > 1:
                mid = lo + (hi - lo) / 2
                if _sign_at(mid) == prev_sign:
                    lo = mid
                else:
                    hi = mid
            ingresses.append((hi, next_sign))
            prev_sign = next_sign
        cur = nxt
    return ingresses


def _house_of_sign(sign_idx: int, reference_sign_idx: int) -> int:
    """Return 1-12 house number of sign_idx from reference_sign_idx."""
    return ((sign_idx - reference_sign_idx) % 12) + 1


# Classical readings of slow-planet transits per house from natal Moon / Lagna
_SATURN_HOUSE_READING = {
    1: ("Sade Sati Phase 2", "Body and identity get audited. Slow grind."),
    2: ("Sade Sati Phase 3", "Wealth and family weights tested. Last leg."),
    3: ("Saturn 3rd transit", "Auspicious — strength returns, courage rewarded, gains via effort."),
    4: (
        "Kantaka Shani",
        "Home/family/inner ground pressured. Mother's health, vehicle issues, domestic strain.",
    ),
    5: ("Saturn 5th transit", "Children/creativity/romance face delays. Investments need caution."),
    6: (
        "Saturn 6th transit",
        "Enemies disabled, debts cleared, work success. Generally favourable.",
    ),
    7: (
        "Saturn 7th transit",
        "Partnership audit. Marriage tested or formalised. 2.5y of relationship reshape.",
    ),
    8: (
        "Ashtama Shani",
        "Heaviest phase. Transformation, possible loss, deep work. 2.5y of restructuring.",
    ),
    9: ("Saturn 9th transit", "Father/dharma/fortune tested. Pilgrimage themes, guru contact."),
    10: (
        "Saturn 10th transit",
        "Career structural test. Promotion or stagnation; depends on chart.",
    ),
    11: (
        "Saturn 11th transit",
        "Strongest period for gains, network, ambitions. Saturn rewards effort here.",
    ),
    12: (
        "Sade Sati Phase 1",
        "Beginning of 7.5y reshape. Hidden losses, foreign themes, foundation prep.",
    ),
}

_JUPITER_HOUSE_READING = {
    1: ("Jupiter on Lagna", "Identity expansion, weight gain, marriage signals, optimism returns."),
    2: ("Jupiter 2nd transit", "Wealth grows, family expands, voice gets respected."),
    3: ("Jupiter 3rd transit", "Mixed — siblings tense, but courage and writing flourish."),
    4: ("Jupiter 4th transit", "Property/home opportunities, mother's grace, domestic peace."),
    5: (
        "Jupiter 5th transit",
        "Children/creativity/romance peak. Best for child-birth, learning, performance.",
    ),
    6: (
        "Jupiter 6th transit",
        "Mixed — health audits, debt resolution, but service-work succeeds.",
    ),
    7: ("Jupiter 7th transit", "Marriage window for unmarried; partnership growth for married."),
    8: (
        "Jupiter 8th transit",
        "Mixed — sudden gains possible but watch health and shared resources.",
    ),
    9: (
        "Jupiter 9th transit",
        "Dharma activates, foreign opportunities, father blessings, pilgrimage.",
    ),
    10: (
        "Jupiter 10th transit",
        "Career peak window. Recognition, promotion, public role expands.",
    ),
    11: (
        "Jupiter 11th transit",
        "Gains peak. Best window for income, network, ambition realisation.",
    ),
    12: (
        "Jupiter 12th transit",
        "Foreign/spiritual themes. Expenses on dharma OR meaningful losses.",
    ),
}

_RAHU_HOUSE_READING = {
    1: ("Rahu on Lagna", "Identity rebuilt unconventionally. Sudden visibility or obsessions."),
    2: ("Rahu 2nd transit", "Family/wealth themes get unconventional. Speech becomes sharper."),
    3: (
        "Rahu 3rd transit",
        "Courage surge, sibling tension, foreign communications, ambition fires.",
    ),
    4: ("Rahu 4th transit", "Home reshaped — relocations, foreign elements in domestic life."),
    5: ("Rahu 5th transit", "Romance/children themes get unconventional. Creativity spikes."),
    6: ("Rahu 6th transit", "Hidden enemies, foreign service, unconventional health issues."),
    7: ("Rahu 7th transit", "Partnership becomes unconventional — foreign or unusual spouse."),
    8: ("Rahu 8th transit", "Transformation accelerates. Hidden discoveries, sudden gains/losses."),
    9: ("Rahu 9th transit", "Foreign opportunities, unconventional dharma, gurus from afar."),
    10: ("Rahu 10th transit", "Career goes unconventional — tech, foreign, fame, status spikes."),
    11: ("Rahu 11th transit", "Gains amplify abnormally. Best for income surge."),
    12: (
        "Rahu 12th transit",
        "Foreign moves, hidden work, spiritual obsession, mysterious losses.",
    ),
}


def compute_slow_transits_calendar(
    chart_data: dict,
    years_ahead: int = 20,
) -> list[dict]:
    """Compute Saturn, Jupiter, and Rahu/Ketu sign-ingresses for next N years.

    Returns list of events, each:
        {
          "date": "2027-04-07",
          "planet": "saturn",
          "from_sign": "Pisces",
          "to_sign": "Aries",
          "house_from_lagna": 7,
          "house_from_moon": 3,
          "lagna_reading": ("Saturn 7th transit", "Partnership audit..."),
          "moon_reading": ("Saturn 3rd transit", "Auspicious — strength returns..."),
          "is_major": True,  # if hits a natal placement strongly
        }
    """
    natal = chart_data["natal_planets_dict"]
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    moon_sign_idx = (
        int(float(natal["moon"]["longitude"]) // 30) if "moon" in natal else lagna_sign_idx
    )

    # Set of signs that hold natal planets (for "is_major" flag)
    natal_planet_signs: set[int] = set()
    for _p, pd in natal.items():
        if not isinstance(pd, dict):
            continue
        natal_planet_signs.add(int(float(pd["longitude"]) // 30) % 12)

    now = datetime.now()
    end = now + timedelta(days=years_ahead * 365.25)

    events: list[dict] = []
    for planet, reading_map, step in [
        ("saturn", _SATURN_HOUSE_READING, 30),
        ("jupiter", _JUPITER_HOUSE_READING, 20),
        ("rahu", _RAHU_HOUSE_READING, 30),
    ]:
        try:
            ingresses = _find_planet_ingresses(planet, now, end, step_days=step)
            prev_sign = -1
            for dt, new_sign in ingresses:
                from_sign = _SIGNS[prev_sign] if prev_sign >= 0 else "—"
                to_sign = _SIGNS[new_sign]
                house_l = _house_of_sign(new_sign, lagna_sign_idx)
                house_m = _house_of_sign(new_sign, moon_sign_idx)
                # is_major = enters sign with natal planet OR enters one of
                # the most-structural houses (1/4/7/10 or 12/1/2 sade sati)
                is_major = (
                    new_sign in natal_planet_signs
                    or house_l in {1, 7, 10}
                    or (planet == "saturn" and house_m in {12, 1, 2, 8})
                )
                events.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "planet": planet,
                        "from_sign": from_sign,
                        "to_sign": to_sign,
                        "house_from_lagna": house_l,
                        "house_from_moon": house_m,
                        "lagna_reading": reading_map.get(house_l, ("", "")),
                        "moon_reading": reading_map.get(house_m, ("", "")),
                        "is_major": is_major,
                    }
                )
                prev_sign = new_sign
        except Exception as e:
            logger.warning(f"Failed to compute {planet} ingresses: {e}")

    events.sort(key=lambda x: x["date"])
    return events
