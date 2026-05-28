"""Chara Dasha + transit cross-analysis (Jaimini timing).

The Jaimini Chara Dasha is sign-based: each sign rules for 1-12 years based
on its lord's distance. This module overlays current transits onto the active
Chara Dasha sign, surfacing:

- Current Chara Dasha rashi + sign-lord + remaining duration
- Where the dasha sign's lord is currently transiting (BPHS: dasha-lord's
  transit = manifestation theme)
- Planets transiting the Chara Dasha rashi itself (direct activation)
- Planets in 5th, 8th, 11th from the dasha rashi (Jaimini aspects on the rashi)
- Bhava-from-dasha-sign for each transiting planet (Jaimini Padakrama)

Use to time Jaimini-flavored events when Vimshottari signals are ambiguous.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day
from packages.cosmos.src.houses import SIGN_RULERS
from packages.self.src.jaimini import (
    INDEX_TO_RASHI,
    RASHI_TO_INDEX,
    calculate_chara_dasha,
    get_jaimini_aspects,
)

_RASHI_NAMES = [
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

_HOUSE_THEMES_BY_OFFSET: dict[int, list[str]] = {
    1: ["self", "body", "manifestation"],
    2: ["wealth", "speech", "family resources"],
    3: ["effort", "siblings", "short journeys"],
    4: ["home", "happiness", "mother"],
    5: ["children", "creativity", "intelligence"],
    6: ["enemies", "service", "obstacles"],
    7: ["partnership", "spouse", "public"],
    8: ["transformation", "longevity", "occult"],
    9: ["dharma", "fortune", "long journeys"],
    10: ["career", "status", "karma"],
    11: ["gains", "fulfillment", "friends"],
    12: ["loss", "moksha", "foreign", "expense"],
}


def get_chara_dasha_transit_overlay(
    chart: Any,  # BirthChart
    birth_datetime: datetime,
    query_datetime: datetime | None = None,
) -> dict[str, Any]:
    """Return Chara Dasha + current transit overlay (Jaimini timing).

    Args:
        chart: BirthChart model (typed pydantic).
        birth_datetime: Birth datetime.
        query_datetime: Moment to evaluate (default: now).

    Returns:
        {
          "current_chara_dasha": {rashi, sign_lord, start, end, years_total,
                                   years_remaining, sign_index},
          "dasha_sign_lord_transit": {planet, rashi, sign_index,
                                       house_from_dasha_sign, themes},
          "planets_in_dasha_sign": [planet, ...],   # direct activation
          "jaimini_aspects_active": [
              {planet, in_rashi, aspect_offset_from_dasha}
          ],
          "padakrama": [
              {planet, rashi, house_from_dasha_sign, themes}
          ],   # 1st-12th-from-dasha-sign mapping
          "next_chara_period": {rashi, sign_lord, start, years},
        }
    """
    if query_datetime is None:
        query_datetime = (
            datetime.now(tz=birth_datetime.tzinfo) if birth_datetime.tzinfo else datetime.now()
        )

    # ── 1. Find current Chara Dasha period ──
    periods = calculate_chara_dasha(birth_datetime, chart, years=120)
    current = None
    next_period = None
    for i, p in enumerate(periods):
        # Compare in birth_dt's frame (start_date is naive-or-aware mirroring birth)
        try:
            in_period = p.start_date <= query_datetime < p.end_date
        except TypeError:
            # tz mismatch: align query
            q_aligned = (
                query_datetime.replace(tzinfo=p.start_date.tzinfo)
                if p.start_date.tzinfo
                else query_datetime.replace(tzinfo=None)
            )
            in_period = p.start_date <= q_aligned < p.end_date
        if in_period:
            current = p
            next_period = periods[i + 1] if i + 1 < len(periods) else None
            break

    if current is None:
        return {"error": "Query outside chara dasha range"}

    dasha_rashi = current.rashi
    dasha_sign_idx = RASHI_TO_INDEX[dasha_rashi]
    sign_lord = SIGN_RULERS.get(dasha_sign_idx, "")

    # tz-safe days_remaining
    try:
        days_remaining = max(0, (current.end_date - query_datetime).days)
    except TypeError:
        # tz mismatch — align query into current.end_date frame
        if current.end_date.tzinfo and not query_datetime.tzinfo:
            q_aligned = query_datetime.replace(tzinfo=current.end_date.tzinfo)
        else:
            q_aligned = query_datetime.replace(tzinfo=None)
        days_remaining = max(0, (current.end_date - q_aligned).days)

    # ── 2. Get current planet positions ──
    jd = get_julian_day(query_datetime)
    raw = get_all_planets(jd)

    # ── 3. Dasha sign-lord's current transit ──
    dasha_lord_transit = {}
    if sign_lord and sign_lord in raw:
        lord_lon = float(raw[sign_lord]["longitude"])
        lord_sign_idx = int(lord_lon // 30) % 12
        house_from_dasha = ((lord_sign_idx - dasha_sign_idx) % 12) + 1
        dasha_lord_transit = {
            "planet": sign_lord,
            "rashi": _RASHI_NAMES[lord_sign_idx],
            "sign_index": lord_sign_idx,
            "house_from_dasha_sign": house_from_dasha,
            "themes": _HOUSE_THEMES_BY_OFFSET.get(house_from_dasha, []),
        }

    # ── 4. Planets directly in the Chara Dasha sign ──
    planets_in_dasha_sign: list[str] = []
    for p, pdata in raw.items():
        sidx = int(float(pdata["longitude"]) // 30) % 12
        if sidx == dasha_sign_idx:
            planets_in_dasha_sign.append(p)

    # ── 5. Jaimini aspects: 5th, 8th, 11th from dasha rashi ──
    jaimini_targets = get_jaimini_aspects(dasha_rashi)
    target_indices = {
        RASHI_TO_INDEX[r]: ((RASHI_TO_INDEX[r] - dasha_sign_idx) % 12) + 1 for r in jaimini_targets
    }
    jaimini_aspects_active: list[dict[str, Any]] = []
    for p, pdata in raw.items():
        sidx = int(float(pdata["longitude"]) // 30) % 12
        if sidx in target_indices:
            jaimini_aspects_active.append(
                {
                    "planet": p,
                    "in_rashi": _RASHI_NAMES[sidx],
                    "aspect_offset_from_dasha": target_indices[sidx],
                }
            )

    # ── 6. Padakrama — bhava overlay (1-12) from dasha sign ──
    padakrama: list[dict[str, Any]] = []
    for p, pdata in raw.items():
        sidx = int(float(pdata["longitude"]) // 30) % 12
        offset = ((sidx - dasha_sign_idx) % 12) + 1
        padakrama.append(
            {
                "planet": p,
                "rashi": _RASHI_NAMES[sidx],
                "house_from_dasha_sign": offset,
                "themes": _HOUSE_THEMES_BY_OFFSET.get(offset, []),
            }
        )
    padakrama.sort(key=lambda x: x["house_from_dasha_sign"])

    return {
        "current_chara_dasha": {
            "rashi": dasha_rashi.value,
            "sign_index": dasha_sign_idx,
            "sign_lord": sign_lord,
            "start_date": current.start_date.isoformat(),
            "end_date": current.end_date.isoformat(),
            "years_total": current.duration_years,
            "days_remaining": days_remaining,
        },
        "dasha_sign_lord_transit": dasha_lord_transit,
        "planets_in_dasha_sign": planets_in_dasha_sign,
        "jaimini_aspects_active": jaimini_aspects_active,
        "padakrama": padakrama,
        "next_chara_period": (
            {
                "rashi": next_period.rashi.value,
                "sign_index": RASHI_TO_INDEX[next_period.rashi],
                "sign_lord": SIGN_RULERS.get(RASHI_TO_INDEX[next_period.rashi], ""),
                "start_date": next_period.start_date.isoformat(),
                "years": next_period.duration_years,
            }
            if next_period
            else None
        ),
    }


def get_chara_dasha_overlay_from_raw(
    birth_datetime: datetime,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_longitude: float,
    moon_rashi: str | None = None,
    query_datetime: datetime | None = None,
) -> dict[str, Any]:
    """Wrapper that builds a BirthChart from raw natal dicts and runs the overlay.

    Lets MCP/chat callers pass plain dicts without needing the typed model.
    """
    from packages.context.src.state_engine import _build_birth_chart

    chart = _build_birth_chart(
        birth_datetime,
        birth_lat,
        birth_lon,
        natal_planets,
        lagna_rashi,
        moon_rashi,
        moon_longitude,
    )
    return get_chara_dasha_transit_overlay(chart, birth_datetime, query_datetime)


# Re-export for convenience
__all__ = [
    "INDEX_TO_RASHI",
    "get_chara_dasha_overlay_from_raw",
    "get_chara_dasha_transit_overlay",
]
