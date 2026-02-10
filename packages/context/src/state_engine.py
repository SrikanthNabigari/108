"""State Vector Engine — normalizes 108-core outputs into 0-10 scores.

Computes a StateVector for any given datetime by calling existing
108-core functions (panchanga, gochara, dasha, etc.) and normalizing
all outputs to a unified 0-10 scale.

Each vector contains:
- 7 factor scores (panchanga, transit_moon, gochara, dasha, yoga, shadbala, ashtakavarga)
- 5 area scores (career, relationships, health, finance, spiritual)
- 1 composite score (weighted average)
- mental state label + confluence measure + hora lord
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition
from packages.self.src.dosha_detector import DoshaDetector
from packages.self.src.strength import StrengthCalculator
from packages.self.src.yoga_detector import YogaDetector

logger = logging.getLogger(__name__)

# Module-level singletons — rules are lazily loaded once.
_strength_calculator = StrengthCalculator()
_yoga_detector = YogaDetector()
_dosha_detector = DoshaDetector()

# ── Factor weights for composite calculation ──

FACTOR_WEIGHTS: dict[str, float] = {
    "panchanga": 0.15,
    "transit_moon": 0.15,
    "gochara": 0.15,
    "dasha": 0.20,
    "yoga_activation": 0.10,
    "shadbala": 0.10,
    "ashtakavarga": 0.15,
}

# ── Area → House mapping ──

AREA_HOUSES: dict[str, list[int]] = {
    "career": [10, 6, 2],
    "relationships": [7, 5, 11],
    "health": [1, 6, 8],
    "finance": [2, 11, 5],
    "spiritual": [9, 12, 5],
}

AREA_PLANETS: dict[str, str] = {
    "career": "saturn",
    "relationships": "venus",
    "health": "sun",
    "finance": "jupiter",
    "spiritual": "ketu",
}

RASHI_NAMES = [
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

# Hora lords sequence (Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars)
_HORA_SEQUENCE = ["sun", "venus", "mercury", "moon", "saturn", "jupiter", "mars"]

# Python weekday() → index into _HORA_SEQUENCE
_DAY_LORD_INDEX = {
    0: 3,  # Monday → Moon
    1: 6,  # Tuesday → Mars
    2: 2,  # Wednesday → Mercury
    3: 5,  # Thursday → Jupiter
    4: 1,  # Friday → Venus
    5: 4,  # Saturday → Saturn
    6: 0,  # Sunday → Sun
}

# Fallback vara lord by weekday
_VARA_LORD = {
    0: "moon",
    1: "mars",
    2: "mercury",
    3: "jupiter",
    4: "venus",
    5: "saturn",
    6: "sun",
}

# Natural benefic/malefic quality
_PLANET_NATURE: dict[str, float] = {
    "jupiter": 1.5,
    "venus": 1.0,
    "mercury": 0.5,
    "moon": 0.5,
    "sun": 0.0,
    "mars": -0.5,
    "saturn": -0.5,
    "rahu": -0.5,
    "ketu": -0.5,
}

# ── Per-house gochara scores (planet → house_from_moon → score 0-10) ──
# Classical Jyotish grades: favorable houses get 6.5-9.5, unfavorable 1.5-4.5
# Within favorable, house 11 (gains) is universally strongest.
# Within unfavorable, house 8 (obstacles/death) is worst.
_GOCHARA_HOUSE_SCORES: dict[str, dict[int, float]] = {
    "sun": {  # favorable: 3, 6, 10, 11
        1: 4.0,
        2: 3.5,
        3: 7.0,
        4: 3.0,
        5: 3.5,
        6: 7.5,
        7: 3.0,
        8: 2.0,
        9: 4.5,
        10: 8.5,
        11: 9.0,
        12: 2.5,
    },
    "moon": {  # favorable: 1, 3, 6, 7, 10, 11
        1: 7.5,
        2: 5.0,
        3: 7.0,
        4: 4.5,
        5: 5.0,
        6: 6.5,
        7: 7.0,
        8: 2.5,
        9: 5.0,
        10: 7.5,
        11: 8.5,
        12: 3.0,
    },
    "mars": {  # favorable: 3, 6, 11
        1: 3.0,
        2: 3.0,
        3: 7.5,
        4: 3.0,
        5: 3.0,
        6: 8.5,
        7: 2.5,
        8: 2.0,
        9: 4.5,
        10: 4.5,
        11: 9.0,
        12: 2.0,
    },
    "mercury": {  # favorable: 2, 4, 6, 8, 10, 11
        1: 3.5,
        2: 7.0,
        3: 4.5,
        4: 7.0,
        5: 4.5,
        6: 7.5,
        7: 4.5,
        8: 6.5,
        9: 4.5,
        10: 7.5,
        11: 8.5,
        12: 3.0,
    },
    "jupiter": {  # favorable: 2, 5, 7, 9, 11
        1: 4.5,
        2: 7.5,
        3: 4.0,
        4: 4.5,
        5: 8.5,
        6: 3.5,
        7: 7.5,
        8: 2.5,
        9: 9.0,
        10: 4.0,
        11: 9.5,
        12: 3.0,
    },
    "venus": {  # favorable: 1, 2, 3, 4, 5, 8, 9, 11, 12
        1: 7.0,
        2: 7.5,
        3: 7.0,
        4: 7.5,
        5: 8.0,
        6: 3.0,
        7: 4.0,
        8: 6.5,
        9: 7.5,
        10: 3.5,
        11: 8.5,
        12: 6.5,
    },
    "saturn": {  # favorable: 3, 6, 11
        1: 2.0,
        2: 2.5,
        3: 7.0,
        4: 2.5,
        5: 2.5,
        6: 8.0,
        7: 3.0,
        8: 1.5,
        9: 3.0,
        10: 3.5,
        11: 9.0,
        12: 2.0,
    },
    "rahu": {  # favorable: 3, 6, 10, 11
        1: 3.0,
        2: 3.5,
        3: 7.0,
        4: 3.0,
        5: 3.5,
        6: 7.5,
        7: 3.0,
        8: 2.5,
        9: 3.5,
        10: 8.0,
        11: 8.5,
        12: 3.0,
    },
    "ketu": {  # favorable: 3, 6, 10, 11
        1: 3.5,
        2: 3.0,
        3: 7.0,
        4: 3.5,
        5: 3.0,
        6: 7.5,
        7: 3.5,
        8: 3.0,
        9: 4.0,
        10: 7.5,
        11: 8.0,
        12: 3.5,
    },
}

# Planet → exaltation sign (0-based index)
_EXALTATION: dict[str, int] = {
    "sun": 0,
    "moon": 1,
    "mars": 9,
    "mercury": 5,
    "jupiter": 3,
    "venus": 11,
    "saturn": 6,
    "rahu": 1,
    "ketu": 7,
}

# Planet → own signs
_OWN_SIGNS: dict[str, list[int]] = {
    "sun": [4],
    "moon": [3],
    "mars": [0, 7],
    "mercury": [2, 5],
    "jupiter": [8, 11],
    "venus": [1, 6],
    "saturn": [9, 10],
    "rahu": [10],
    "ketu": [7],
}

# Panchanga yoga quality (auspicious/inauspicious)
_YOGA_QUALITY: dict[str, int] = {
    "Vishkumbha": -2,
    "Atiganda": -2,
    "Shoola": -2,
    "Vyatipata": -2,
    "Ganda": -1,
    "Vyaghata": -1,
    "Vajra": -1,
    "Parigha": -1,
    "Priti": 1,
    "Ayushman": 1,
    "Saubhagya": 1,
    "Shobhana": 1,
    "Sukarma": 1,
    "Dhriti": 1,
    "Vriddhi": 1,
    "Dhruva": 1,
    "Harshana": 1,
    "Shiva": 1,
    "Siddha": 2,
    "Siddhi": 2,
    "Brahma": 1,
    "Indra": 1,
    "Vaidhriti": -2,
}

# Vara quality by lord (planet ruling the day)
_VARA_LORD_QUALITY: dict[str, float] = {
    "moon": 0.5,
    "mars": -0.5,
    "mercury": 1.0,
    "jupiter": 1.5,
    "venus": 1.0,
    "saturn": -1.0,
    "sun": 0.5,
}

# Nakshatra lord quality for panchanga scoring
_NAKSHATRA_LORD_QUALITY: dict[str, float] = {
    "jupiter": 1.0,
    "venus": 0.8,
    "mercury": 0.5,
    "moon": 0.3,
    "sun": 0.0,
    "mars": -0.3,
    "saturn": -0.5,
    "rahu": -0.3,
    "ketu": -0.3,
}

# Area display names
_AREA_NAMES: dict[str, str] = {
    "career": "Career",
    "relationships": "Love",
    "health": "Health",
    "finance": "Money",
    "spiritual": "Spirit",
}


# ── Utilities ──


def _rashi_index(name: str) -> int:
    """Convert rashi name (e.g. 'libra') to 0-based index."""
    low = name.lower()
    if low in RASHI_NAMES:
        return RASHI_NAMES.index(low)
    return 0


def _house_from_lagna(planet_rashi: int, lagna_rashi: int) -> int:
    """House number (1-12) from planet's rashi relative to lagna."""
    return ((planet_rashi - lagna_rashi) % 12) + 1


def _clamp(val: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, val))


def _strip_tz(dt: datetime) -> datetime:
    """Strip timezone info for naive comparison."""
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


# ── Factor Scorers ──


def _normalize_panchanga(panchanga: dict[str, Any]) -> tuple[float, str, str]:
    """Convert panchanga output to (score 0-10, dominant_planet, description).

    Uses all 5 panchanga limbs: tithi, nakshatra, yoga, karana, vara.
    Also factors in tithi/yoga progress (how far through the period).
    """
    score = 5.0

    # 1. Tithi quality (20% of panchanga influence)
    tithi = panchanga.get("tithi", {})
    paksha = tithi.get("paksha", "")
    tithi_num = tithi.get("number", 1)
    if isinstance(paksha, str) and paksha.lower() == "shukla":
        score += 0.5
    elif isinstance(paksha, str) and paksha.lower() == "krishna":
        score -= 0.3
    # Auspicious tithis (2=Dwitiya, 3=Tritiya, 5=Panchami, 7=Saptami, 10=Dashami, 11=Ekadashi, 13=Trayodashi)
    if tithi_num in (2, 3, 5, 7, 10, 11, 13):
        score += 0.5
    # Inauspicious tithis (4=Chaturthi, 8=Ashtami, 9=Navami, 14=Chaturdashi, 30=Amavasya)
    if tithi_num in (4, 8, 9, 14, 30):
        score -= 0.7
    # Tithi progress: mid-tithi (0.3-0.7) is strongest, edges are sandhi
    tithi_progress = tithi.get("progress", 0.5)
    if tithi_progress < 0.1 or tithi_progress > 0.9:
        score -= 0.3  # tithi sandhi — junction weakness

    # 2. Yoga quality (20%)
    yoga_data = panchanga.get("yoga", {})
    yoga_name = yoga_data.get("name", "")
    yoga_adj = _YOGA_QUALITY.get(yoga_name, 0)
    score += yoga_adj * 0.5
    # Yoga progress: mid-yoga strongest
    yoga_progress = yoga_data.get("progress", 0.5)
    if yoga_progress < 0.1 or yoga_progress > 0.9:
        score -= 0.2  # yoga sandhi

    # 3. Vara quality (15%) — using lord name, not English day name
    vara = panchanga.get("vara", {})
    vara_name = vara.get("name", "")
    vara_lord = vara.get("lord", "").lower()
    vara_adj = _VARA_LORD_QUALITY.get(vara_lord, 0.0)
    score += vara_adj * 0.5

    # 4. Karana quality (10%)
    karana = panchanga.get("karana", {})
    karana_name = karana.get("name", "")
    karana_type = karana.get("type", "")
    good_karanas = {"Bava", "Balava", "Kaulava", "Taitila", "Gaja", "Vanija"}
    bad_karanas = {"Vishti"}  # Bhadra karana — inauspicious
    if karana_name in good_karanas:
        score += 0.3
    elif karana_name in bad_karanas:
        score -= 0.5
    elif karana_type == "fixed":
        score += 0.1  # fixed karanas (Shakuni, Chatushpada, Naga, Kimstughna) are mild

    # 5. Nakshatra lord quality (15%) — transit Moon's nakshatra influence
    nakshatra = panchanga.get("nakshatra", {})
    nak_name = nakshatra.get("name", "")
    # Map nakshatra number to lord
    nak_num = nakshatra.get("number", 0)
    _nak_lord_cycle = [
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
    nak_lord = _nak_lord_cycle[(nak_num - 1) % 9] if nak_num >= 1 else ""
    nak_adj = _NAKSHATRA_LORD_QUALITY.get(nak_lord, 0.0)
    score += nak_adj * 0.5

    desc = f"Tithi {tithi.get('name', '')}, {vara_name}"
    if yoga_name:
        desc += f", {yoga_name} yoga"
    if nak_name:
        desc += f", {nak_name}"

    return _clamp(score), vara_lord, desc


def _normalize_transit_moon(
    transit_positions: dict[str, int],
    lagna_index: int,
    birth_moon_nak: int = 0,
    raw_planets: dict[str, Any] | None = None,
) -> tuple[float, str, str]:
    """Score Moon's transit position relative to lagna + nakshatra Tarabala.

    Combines house-based score with Tarabala (birth nakshatra to transit
    nakshatra relationship) for a more precise Moon transit assessment.
    """
    moon_rashi = transit_positions.get("moon", 0)
    house = _house_from_lagna(moon_rashi, lagna_index)

    # Moon gochara house scores (per-house from lagna)
    house_scores: dict[int, float] = {
        1: 7.5,
        2: 4.5,
        3: 7.0,
        4: 5.5,
        5: 5.0,
        6: 6.5,
        7: 5.5,
        8: 3.0,
        9: 6.0,
        10: 7.5,
        11: 8.0,
        12: 3.5,
    }
    score = house_scores.get(house, 5.0)

    # Tarabala: 9-fold relationship between birth and transit nakshatras
    # Tara cycle: 1=Janma(mod), 2=Sampat(+), 3=Vipat(-), 4=Kshema(+),
    #             5=Pratyak(-), 6=Sadhana(+), 7=Naidhana(-), 8=Mitra(+), 9=ParamaMitra(+)
    if birth_moon_nak >= 1 and raw_planets:
        moon_lon = raw_planets.get("moon", {}).get("longitude", 0)
        transit_nak = int(moon_lon / 13.333333) + 1  # 1-27
        if transit_nak >= 1:
            tara = ((transit_nak - birth_moon_nak) % 9) + 1
            _TARA_ADJ = {
                1: -0.3,  # Janma — moderate stress
                2: 0.5,  # Sampat — wealth, gain
                3: -0.6,  # Vipat — danger
                4: 0.5,  # Kshema — prosperity
                5: -0.4,  # Pratyak — obstacles
                6: 0.3,  # Sadhana — achievement
                7: -0.7,  # Naidhana — worst (death/loss)
                8: 0.4,  # Mitra — friendly
                9: 0.6,  # Parama Mitra — best friend
            }
            score += _TARA_ADJ.get(tara, 0.0)

    sign_name = RASHI_NAMES[moon_rashi] if 0 <= moon_rashi < 12 else "unknown"
    desc = f"Moon in {sign_name.title()} (house {house})"

    return _clamp(score), "moon", desc


def _normalize_gochara(
    transit_result: dict[str, Any],
    raw_planets: dict[str, Any] | None = None,
    lagna_index: int | None = None,
) -> tuple[float, str, str]:
    """Convert full transit analysis to (score 0-10, dominant_planet, description).

    Uses per-planet per-house graded scoring from classical Jyotish texts.
    Each planet in each house from Moon has a distinct score (not binary).
    Modifiers: sandhi (sign boundary weakness), lordship role, retrograde.
    """
    planet_transits = transit_result.get("planet_transits", {})
    if not planet_transits:
        return 5.0, "", "No transit data"

    # Weight planets by astrological significance (slow > fast)
    _gochara_weight: dict[str, float] = {
        "jupiter": 2.0,
        "saturn": 2.0,
        "rahu": 1.5,
        "ketu": 1.0,
        "mars": 1.2,
        "sun": 1.0,
        "venus": 1.0,
        "mercury": 0.8,
        "moon": 1.5,
    }

    # Pre-compute lordship roles if lagna available
    lordship_roles: dict[str, dict[str, Any]] = {}
    if lagna_index is not None:
        try:
            from packages.self.src.transit_lordship import classify_planet_role

            for planet in planet_transits:
                lordship_roles[planet] = classify_planet_role(planet, lagna_index)
        except Exception:
            pass

    weighted_score = 0.0
    total_weight = 0.0
    dominant = ""
    max_impact = 0.0

    for planet, data in planet_transits.items():
        w = _gochara_weight.get(planet, 1.0)

        # 1. Per-house graded score (replaces binary 8.0/2.0)
        house_from_moon = data.get("house_from_moon", 0)
        if house_from_moon >= 1:
            base = _GOCHARA_HOUSE_SCORES.get(planet, {}).get(house_from_moon, 5.0)
        else:
            # Fallback for data without house_from_moon
            base = 7.5 if data.get("is_favorable") else 3.0

        # 2. Vedha cancellation — pull score toward neutral
        if data.get("has_vedha") and data.get("is_favorable"):
            base = 5.0 + (base - 5.0) * 0.3  # ~70% cancelled

        # 3. Sandhi & retrograde from raw longitude data
        if raw_planets and planet in raw_planets:
            pdata = raw_planets[planet]
            lon = pdata.get("longitude", 0)
            deg_in_sign = lon % 30

            # Sandhi: planet at sign boundary (0° or 30°) is weak
            dist_from_boundary = min(deg_in_sign, 30 - deg_in_sign)
            if dist_from_boundary < 1.0:
                sandhi = 0.7  # significant weakness at exact junction
            elif dist_from_boundary < 3.0:
                sandhi = 0.85  # mild weakness near boundary
            else:
                sandhi = 1.0
            base = 5.0 + (base - 5.0) * sandhi

            # 4. Retrograde: intensifies the effect (good → better, bad → worse)
            if pdata.get("is_retrograde"):
                base = 5.0 + (base - 5.0) * 1.25

        # 5. Lordship modifier: functional nature shapes transit quality
        role = lordship_roles.get(planet)
        if role:
            nature = role.get("functional_nature", "neutral")
            if nature == "yogakaraka":
                base += 0.8
            elif nature == "benefic":
                base += 0.4
            elif nature == "malefic":
                base -= 0.4
            elif nature == "maraka":
                base -= 0.6

        base = _clamp(base)
        weighted_score += base * w
        total_weight += w

        # Track dominant planet (highest absolute impact)
        impact = abs(base - 5.0) * w
        if impact > max_impact:
            max_impact = impact
            dominant = planet

    score = weighted_score / total_weight if total_weight > 0 else 5.0

    # Sade Sati adjustment
    sade_sati = transit_result.get("sade_sati", {})
    if sade_sati.get("active"):
        phase = sade_sati.get("phase", "")
        score -= 2.0 if phase == "peak" else 1.0
        dominant = "saturn"

    summary = transit_result.get("summary", {})
    favorable = summary.get("favorable_count", 0)
    unfavorable = summary.get("unfavorable_count", 0)
    trend = summary.get("overall_trend", "mixed")
    desc = f"{favorable} favorable, {unfavorable} unfavorable transits ({trend})"

    return _clamp(score), dominant, desc


def _dignity_for_planet(lord: str, natal_planets: dict[str, Any]) -> float:
    """Get dignity-based score (0-10) for a planet from its natal placement."""
    planet_data = natal_planets.get(lord, {})
    rashi = planet_data.get("rashi", -1) if isinstance(planet_data, dict) else -1
    if rashi < 0:
        return 5.0 + _PLANET_NATURE.get(lord, 0.0) * 2.0

    # Exaltation
    if _EXALTATION.get(lord) == rashi:
        return 10.0
    # Debilitation (opposite of exaltation)
    exalt = _EXALTATION.get(lord)
    if exalt is not None and ((exalt + 6) % 12) == rashi:
        return 1.0
    # Own sign
    if rashi in _OWN_SIGNS.get(lord, []):
        return 8.0
    # Default: nature-based
    return 5.0 + _PLANET_NATURE.get(lord, 0.0) * 2.0


# MD x AD relationship quality -> score adjustment
_DASHA_RELATIONSHIP_ADJ: dict[str, float] = {
    "friend": 1.0,
    "same": 0.5,
    "neutral": 0.0,
    "enemy": -1.0,
}


def _normalize_dasha(
    dasha_result: dict[str, Any] | None,
    natal_planets: dict[str, Any],
) -> tuple[float, str, str]:
    """Score current dasha based on lord dignity + MD x AD relationship quality.

    Combines natal dignity (how strong each lord is in the chart) with
    the natural relationship between MD and AD lords from the knowledge base.
    """
    if not dasha_result:
        return 5.0, "", "Dasha data unavailable"

    md = dasha_result.get("mahadasha", {})
    ad = dasha_result.get("antardasha", {})
    pd = dasha_result.get("pratyantardasha", {})

    md_lord = md.get("lord", "")
    ad_lord = ad.get("lord", "")
    pd_lord = pd.get("lord", "")

    # 1. Natal dignity scores (static per chart)
    md_score = _dignity_for_planet(md_lord, natal_planets)
    ad_score = _dignity_for_planet(ad_lord, natal_planets)
    pd_score = _dignity_for_planet(pd_lord, natal_planets)

    dignity_score = md_score * 0.5 + ad_score * 0.3 + pd_score * 0.2

    # 2. MD x AD relationship quality from knowledge base
    relationship_adj = 0.0
    ad_effects: dict[str, Any] = {}
    try:
        from packages.core.src.knowledge_loader import get_antardasha_effects

        all_effects = get_antardasha_effects()
        ad_effects = all_effects.get(md_lord, {}).get(ad_lord, {})
        relationship = ad_effects.get("relationship", "neutral")
        relationship_adj = _DASHA_RELATIONSHIP_ADJ.get(relationship, 0.0)
    except Exception:
        pass

    # 3. Blend: dignity (75%) + relationship quality (25%)
    score = dignity_score + relationship_adj * 0.5

    # Build rich description
    desc = f"{md_lord.title()} MD / {ad_lord.title()} AD"
    if pd_lord:
        desc += f" / {pd_lord.title()} PD"
    rel = ad_effects.get("relationship", "")
    if rel:
        desc += f" ({rel})"

    return _clamp(score), md_lord, desc


def _score_yoga_activation(
    transit_positions: dict[str, int],
    lagna_index: int,
    raw_planets: dict[str, Any] | None = None,
) -> tuple[float, str, str]:
    """Yoga activation from benefic/malefic placement in kendra/trikona from lagna.

    Yogas form when benefics (Jupiter, Venus, Mercury) occupy kendra (1,4,7,10)
    or trikona (1,5,9) houses. Malefics in upachaya (3,6,10,11) also help.
    Uses actual transit longitudes for daily variation.
    """
    if not transit_positions:
        return 5.0, "jupiter", "No transit data for yoga"

    kendra = {1, 4, 7, 10}
    trikona = {1, 5, 9}
    upachaya = {3, 6, 10, 11}
    dusthana = {6, 8, 12}

    benefics = {"jupiter", "venus", "mercury"}
    malefics = {"saturn", "mars", "rahu"}

    score = 5.0  # neutral baseline
    dominant = "jupiter"
    max_contrib = 0.0

    for planet, rashi in transit_positions.items():
        house = _house_from_lagna(rashi, lagna_index)
        contrib = 0.0

        if planet in benefics:
            if house in kendra:
                contrib = 0.6
            elif house in trikona:
                contrib = 0.5
            elif house in dusthana:
                contrib = -0.5
        elif planet in malefics:
            if house in upachaya:
                contrib = 0.3
            elif house in kendra:
                contrib = -0.4
            elif house in dusthana:
                contrib = -0.6
        else:
            # Moon, Sun, Ketu — mild effects
            if house in trikona:
                contrib = 0.2
            elif house in dusthana:
                contrib = -0.3

        # Retrograde planets have amplified effects
        if raw_planets and planet in raw_planets and raw_planets[planet].get("is_retrograde"):
            contrib *= 1.3

        score += contrib
        if abs(contrib) > max_contrib:
            max_contrib = abs(contrib)
            dominant = planet

    # Count benefics in good houses for description
    good_count = sum(
        1
        for p in benefics
        if _house_from_lagna(transit_positions.get(p, 0), lagna_index) in (kendra | trikona)
    )
    desc = f"{good_count} benefics in kendra/trikona"

    return _clamp(score), dominant, desc


def _build_birth_chart(
    birth_dt: datetime,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, Any],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    moon_longitude: float = 0.0,
) -> BirthChart:
    """Construct a BirthChart pydantic model from raw state-engine data.

    Used to interface with StrengthCalculator which requires typed models.
    """
    rashi_list = list(Rashi)
    lagna_idx = _rashi_index(lagna_rashi)
    lagna_enum = rashi_list[lagna_idx]

    # Nakshatra lookup table (lord per nakshatra 1-27, Vimshottari cycle)
    _nak_lords = [
        Planet.KETU,
        Planet.VENUS,
        Planet.SUN,
        Planet.MOON,
        Planet.MARS,
        Planet.RAHU,
        Planet.JUPITER,
        Planet.SATURN,
        Planet.MERCURY,
    ]
    _nak_names = [
        "ashwini",
        "bharani",
        "krittika",
        "rohini",
        "mrigashira",
        "ardra",
        "punarvasu",
        "pushya",
        "ashlesha",
        "magha",
        "purva_phalguni",
        "uttara_phalguni",
        "hasta",
        "chitra",
        "swati",
        "vishakha",
        "anuradha",
        "jyeshtha",
        "moola",
        "purva_ashadha",
        "uttara_ashadha",
        "shravana",
        "dhanishta",
        "shatabhisha",
        "purva_bhadrapada",
        "uttara_bhadrapada",
        "revati",
    ]

    def _nak_from_lon(lon: float) -> tuple[str, int, Planet]:
        """Return (nakshatra_name, pada, lord) from longitude."""
        nak_span = 13.333333333
        pada_span = 3.333333333
        idx = int(lon / nak_span) % 27
        deg_in_nak = lon % nak_span
        pada = min(int(deg_in_nak / pada_span) + 1, 4)
        return _nak_names[idx], pada, _nak_lords[idx % 9]

    # Build typed planet dict
    planet_enum_map: dict[str, Planet] = {p.value: p for p in Planet}
    planets: dict[Planet, PlanetPosition] = {}

    for pname, pdata in natal_planets.items():
        if not isinstance(pdata, dict):
            continue
        p_enum = planet_enum_map.get(pname.lower())
        if p_enum is None:
            continue

        lon = float(pdata.get("longitude", 0.0))
        rashi_idx = int(pdata.get("rashi", int(lon / 30)))
        house = int(pdata.get("house", _house_from_lagna(rashi_idx, lagna_idx)))
        rashi_degree = lon % 30
        is_retro = bool(pdata.get("is_retrograde", False))
        speed = float(pdata.get("speed", 0.0))
        latitude = float(pdata.get("latitude", 0.0))

        nak_name, nak_pada, nak_lord = _nak_from_lon(lon)

        planets[p_enum] = PlanetPosition(
            planet=p_enum,
            longitude=lon,
            latitude=latitude,
            speed=speed,
            rashi=rashi_list[rashi_idx % 12],
            rashi_degree=rashi_degree,
            nakshatra=nak_name,
            nakshatra_pada=nak_pada,
            nakshatra_lord=nak_lord,
            is_retrograde=is_retro,
            house=max(1, min(12, house)),
        )

    # Whole-sign house cusps (each sign = 30°)
    cusps = [((lagna_idx + i) % 12) * 30.0 for i in range(12)]
    asc_lon = lagna_idx * 30.0
    mc_lon = ((lagna_idx + 9) % 12) * 30.0

    # Moon info
    moon_nak_name, _, _ = _nak_from_lon(moon_longitude)
    if moon_rashi:
        moon_enum = rashi_list[_rashi_index(moon_rashi)]
    else:
        moon_enum = rashi_list[int(moon_longitude / 30) % 12]

    return BirthChart(
        user_id="state_engine",
        birth_data=BirthData(
            datetime_utc=_strip_tz(birth_dt),
            latitude=birth_lat,
            longitude=birth_lon,
            timezone="UTC",
        ),
        planets=planets,
        houses=HouseCusps(ascendant=asc_lon, mc=mc_lon, cusps=cusps),
        lagna_rashi=lagna_enum,
        moon_rashi=moon_enum,
        moon_nakshatra=moon_nak_name,
        ayanamsa=23.85,  # Lahiri approximate
        calculated_at=birth_dt,
    )


def _virupas_to_score(virupas: float) -> float:
    """Normalize Shadbala virupas to 0-10 scale.

    Classical Shadbala thresholds (BPHS):
    - Required minimum ~180 virupas (varies by planet)
    - 300+ virupas = strong
    - 360+ virupas = very strong
    - Typical max ~450-500 virupas

    Mapping: 0→0, 120→2, 180→3.5, 300→6.5, 400→9, 480+→10
    Uses a piecewise linear scale weighted toward the meaningful range.
    """
    if virupas <= 0:
        return 0.0
    if virupas <= 180:
        # 0-180: maps to 0-3.5  (below minimum strength)
        return virupas / 180 * 3.5
    if virupas <= 300:
        # 180-300: maps to 3.5-6.5  (moderate strength)
        return 3.5 + (virupas - 180) / 120 * 3.0
    if virupas <= 420:
        # 300-420: maps to 6.5-9.0  (strong)
        return 6.5 + (virupas - 300) / 120 * 2.5
    # 420+: maps to 9.0-10.0  (very strong)
    return min(10.0, 9.0 + (virupas - 420) / 80 * 1.0)


def _score_shadbala(
    dasha_result: dict[str, Any] | None,
    natal_planets: dict[str, Any],  # noqa: ARG001 — kept for signature compatibility
    birth_chart: BirthChart | None = None,
) -> tuple[float, str, str]:
    """Real Shadbala using StrengthCalculator (all 6 components).

    Computes full Shadbala for dasha lords (weighted MD/AD/PD) and
    blends with the chart-wide average for a comprehensive strength picture.

    Components computed: Sthana Bala, Dig Bala, Kaala Bala,
    Chesta Bala, Naisargika Bala, Drik Bala.
    """
    if not dasha_result or not birth_chart:
        return 5.0, "", "Shadbala data unavailable"

    md_lord = dasha_result.get("mahadasha", {}).get("lord", "")
    ad_lord = dasha_result.get("antardasha", {}).get("lord", "")
    pd_lord = dasha_result.get("pratyantardasha", {}).get("lord", "")
    dominant = md_lord

    # Compute Shadbala for all planets in chart
    try:
        all_strengths = _strength_calculator.get_all_planet_strengths(birth_chart)
    except Exception as e:
        logger.warning(f"StrengthCalculator failed: {e}")
        return 5.0, "", "Shadbala computation error"

    # Helper to get virupas for a planet name
    def _get_virupas(lord_name: str) -> float:
        if not lord_name:
            return 0.0
        data = all_strengths.get(lord_name, {})
        return float(data.get("total", 0.0))

    # Dasha lord strengths — weighted by period importance
    md_virupas = _get_virupas(md_lord)
    ad_virupas = _get_virupas(ad_lord)
    pd_virupas = _get_virupas(pd_lord)

    # Weighted dasha lord score (MD most important)
    weights = []
    virupas_vals = []
    if md_lord:
        weights.append(0.50)
        virupas_vals.append(md_virupas)
    if ad_lord:
        weights.append(0.30)
        virupas_vals.append(ad_virupas)
    if pd_lord:
        weights.append(0.20)
        virupas_vals.append(pd_virupas)

    if not weights:
        return 5.0, dominant, "No dasha lords for Shadbala"

    # Normalize weights (in case PD is missing, etc.)
    total_w = sum(weights)
    dasha_score = sum(
        _virupas_to_score(v) * (w / total_w) for v, w in zip(virupas_vals, weights, strict=True)
    )

    # Chart-wide average for context
    all_virupas = [float(d.get("total", 0.0)) for d in all_strengths.values()]
    chart_avg = sum(all_virupas) / len(all_virupas) if all_virupas else 0.0
    chart_score = _virupas_to_score(chart_avg)

    # Blend: dasha lords (75%) + chart average (25%)
    score = dasha_score * 0.75 + chart_score * 0.25

    # Determine dominant (strongest dasha lord)
    if ad_virupas > md_virupas and ad_lord:
        dominant = ad_lord
    if pd_virupas > max(md_virupas, ad_virupas) and pd_lord:
        dominant = pd_lord

    # Build description with component breakdown
    lords = md_lord.title()
    if ad_lord:
        lords += f"/{ad_lord.title()}"
    md_rating = all_strengths.get(md_lord, {}).get("strength_rating", "?")
    desc = f"{lords} Shadbala ({md_rating}, {md_virupas:.0f}v)"

    return _clamp(score), dominant, desc


# Empirical SAV house averages — fallback when BirthChart unavailable
_SAV_HOUSE_AVG: dict[int, float] = {
    1: 25,
    2: 22,
    3: 29,
    4: 24,
    5: 25,
    6: 34,
    7: 19,
    8: 26,
    9: 29,
    10: 36,
    11: 54,
    12: 16,
}


def _score_ashtakavarga(
    transit_positions: dict[str, int],
    lagna_index: int,
    birth_chart: BirthChart | None = None,
) -> tuple[float, str, str]:
    """Ashtakavarga from chart-specific SAV/BAV via StrengthCalculator.

    When a BirthChart is available, computes real Sarvashtakavarga (SAV)
    per sign and Bhinnashtakavarga (BAV) per planet per sign from the
    natal chart. Each transiting planet's BAV score in its current sign
    tells us how favorable that transit is for this specific person.

    Falls back to empirical SAV house averages when chart unavailable.
    """
    if not transit_positions:
        return 5.0, "", "No transit data for SAV"

    planet_enum_map: dict[str, Planet] = {p.value: p for p in Planet}

    # Try real chart-specific calculation
    if birth_chart is not None:
        try:
            sav = _strength_calculator.calculate_sarvashtakavarga(birth_chart)

            total_bav = 0.0
            planet_count = 0
            strongest_planet = ""
            strongest_score = 0.0

            for planet_name, rashi in transit_positions.items():
                p_enum = planet_enum_map.get(planet_name)
                if p_enum is None or rashi < 0 or rashi > 11:
                    continue
                # BAV: planet-specific score for this sign (0-8)
                if p_enum in (Planet.RAHU, Planet.KETU):
                    # Shadow planets: use SAV only (no BAV defined)
                    bav_score = sav[rashi] / 7.0  # normalize to ~0-8 range
                else:
                    bav = _strength_calculator.calculate_ashtakavarga(p_enum, birth_chart)
                    bav_score = float(bav[rashi])

                total_bav += bav_score
                planet_count += 1

                if bav_score > strongest_score:
                    strongest_score = bav_score
                    strongest_planet = planet_name

            if planet_count > 0:
                avg_bav = total_bav / planet_count
                # BAV range: 0-8, median ~4. Map to 0-10.
                score = _clamp(avg_bav / 8.0 * 10.0)
                desc = f"Avg BAV {avg_bav:.1f}/8 across {planet_count} transits (chart-specific)"
                return score, strongest_planet, desc
        except Exception as e:
            logger.warning(f"Real Ashtakavarga failed, using fallback: {e}")

    # Fallback: empirical SAV house averages
    total_sav = 0.0
    planet_count = 0
    strongest_planet = ""
    strongest_sav = 0.0

    for planet, rashi in transit_positions.items():
        house = _house_from_lagna(rashi, lagna_index)
        sav = _SAV_HOUSE_AVG.get(house, 25)
        total_sav += sav
        planet_count += 1
        if sav > strongest_sav:
            strongest_sav = sav
            strongest_planet = planet

    if planet_count == 0:
        return 5.0, "", "No transit data for SAV"

    avg_sav = total_sav / planet_count
    score = _clamp((avg_sav - 16) / (54 - 16) * 10.0)

    desc = f"Avg SAV {avg_sav:.0f} across {planet_count} transits"
    return score, strongest_planet, desc


# ── Natal Yoga Detection (lightweight, no BirthChart needed) ──


def _detect_natal_yogas(
    natal_planets: dict[str, Any],  # noqa: ARG001 — kept for fallback signature
    lagna_index: int,  # noqa: ARG001
    birth_chart: BirthChart | None = None,
) -> list[dict[str, Any]]:
    """Detect natal yogas using real YogaDetector (522 rules from knowledge).

    When birth_chart is available, delegates to YogaDetector.detect_all_yogas()
    which evaluates all 522 yoga rules from yoga_master.json.
    Returns list of {name, planets, houses, category, strength}.
    """
    if birth_chart is None:
        return []

    try:
        detected = _yoga_detector.detect_all_yogas(birth_chart)
    except Exception as e:
        logger.warning(f"YogaDetector failed: {e}")
        return []

    yogas: list[dict[str, Any]] = []
    for dy in detected:
        # Extract house numbers from involved planets
        houses = []
        for p_enum in dy.involved_planets:
            pp = birth_chart.planets.get(p_enum)
            if pp and pp.house:
                houses.append(pp.house)

        yogas.append(
            {
                "name": dy.name,
                "planets": [p.value for p in dy.involved_planets],
                "houses": houses,
                "category": dy.category.value,
                "strength": dy.strength,
            }
        )

    return yogas


def _detect_natal_doshas(
    natal_planets: dict[str, Any],  # noqa: ARG001 — kept for fallback signature
    lagna_index: int,  # noqa: ARG001
    birth_chart: BirthChart | None = None,
) -> list[dict[str, Any]]:
    """Detect natal doshas using real DoshaDetector (55 rules from knowledge).

    When birth_chart is available, delegates to DoshaDetector.detect_all()
    which checks Mangal, Kaal Sarp, Pitra, Guru Chandal, and more.
    Returns list of {name, severity, planets, affected_areas, houses}.
    """
    if birth_chart is None:
        return []

    try:
        detected = _dosha_detector.detect_all(birth_chart)
    except Exception as e:
        logger.warning(f"DoshaDetector failed: {e}")
        return []

    # Map dosha names to affected life areas
    _dosha_area_map: dict[str, list[str]] = {
        "mangal": ["relationships", "health"],
        "kaal sarp": ["career", "health", "spiritual"],
        "pitra": ["spiritual", "finance"],
        "guru chandal": ["spiritual", "career"],
        "grahan": ["health", "spiritual"],
        "kemdrum": ["finance", "relationships"],
        "shakat": ["career", "health"],
        "daridra": ["finance", "career"],
    }

    doshas: list[dict[str, Any]] = []
    for dd in detected:
        # Find affected areas by matching dosha name keywords
        areas: list[str] = []
        name_lower = dd.name.lower()
        for key, area_list in _dosha_area_map.items():
            if key in name_lower:
                areas = area_list
                break
        if not areas:
            areas = ["health", "career"]  # Default areas

        # Extract houses from planet positions
        houses = []
        for p_enum in dd.involved_planets:
            pp = birth_chart.planets.get(p_enum)
            if pp and pp.house:
                houses.append(pp.house)

        doshas.append(
            {
                "name": dd.name,
                "severity": dd.severity,
                "planets": [p.value for p in dd.involved_planets],
                "affected_areas": areas,
                "houses": houses,
            }
        )

    return doshas


def _score_yoga_with_natal(
    natal_yogas: list[dict[str, Any]],
    transit_positions: dict[str, int],
    lagna_index: int,
    raw_planets: dict[str, Any] | None = None,
) -> tuple[float, str, str]:
    """Score yoga activation using actual natal yogas + transit activation.

    Combines generic transit quality with natal yoga activation check.
    """
    if not transit_positions:
        return 5.0, "jupiter", "No transit data for yoga"

    # Start with generic transit-based yoga score
    base_score, dominant, _ = _score_yoga_activation(transit_positions, lagna_index, raw_planets)

    if not natal_yogas:
        return base_score, dominant, "No natal yogas detected"

    # Check which natal yogas are activated by current transits
    active_count = 0
    active_names: list[str] = []

    for yoga in natal_yogas:
        yoga_houses = yoga.get("houses", [])
        yoga_planets = yoga.get("planets", [])
        activated = False

        # Check if transit planets are in yoga-related houses
        for _planet, rashi in transit_positions.items():
            t_house = _house_from_lagna(rashi, lagna_index)
            if t_house in yoga_houses:
                activated = True
                break

        # Check if yoga's own planets are well-placed in transit
        if not activated:
            for yp in yoga_planets:
                if yp in transit_positions:
                    t_rashi = transit_positions[yp]
                    # Planet in own sign or exalted = activation
                    if _EXALTATION.get(yp) == t_rashi or t_rashi in _OWN_SIGNS.get(yp, []):
                        activated = True
                        break

        if activated:
            active_count += 1
            active_names.append(yoga["name"])
            # Boost score based on yoga strength
            base_score += yoga.get("strength", 0.5) * 0.5

    total = len(natal_yogas)
    desc = f"{active_count}/{total} yogas active" + (
        f" ({', '.join(active_names[:3])})" if active_names else ""
    )

    # Dominant planet from most impactful active yoga
    if active_names and natal_yogas:
        for y in natal_yogas:
            if y["name"] in active_names and y.get("planets"):
                dominant = y["planets"][0]
                break

    return _clamp(base_score), dominant, desc


def _score_dosha_impact(
    natal_doshas: list[dict[str, Any]],
    transit_positions: dict[str, int],
    lagna_index: int,
    sade_sati: dict[str, Any] | None = None,
) -> dict[str, float]:
    """Compute per-area dosha impact penalties (0.0 to -3.0 range).

    Returns dict keyed by area id with negative penalty values.
    Active doshas amplified by unfavorable transits create area-specific drags.
    """
    penalties: dict[str, float] = {
        "career": 0.0,
        "relationships": 0.0,
        "health": 0.0,
        "finance": 0.0,
        "spiritual": 0.0,
    }

    for dosha in natal_doshas:
        severity_mult = {"severe": 1.0, "moderate": 0.6, "mild": 0.3}.get(
            dosha.get("severity", "moderate"), 0.5
        )

        # Check if transit amplifies the dosha
        amplified = False
        for planet in dosha.get("planets", []):
            if planet in transit_positions:
                t_house = _house_from_lagna(transit_positions[planet], lagna_index)
                # Dosha planet transiting dosha houses = amplification
                if t_house in dosha.get("houses", []):
                    amplified = True
                # Dosha planet in dusthana = also bad
                if t_house in (6, 8, 12):
                    amplified = True

        penalty = -0.8 * severity_mult
        if amplified:
            penalty *= 1.5  # 50% worse when transit amplifies

        for area in dosha.get("affected_areas", []):
            if area in penalties:
                penalties[area] += penalty

    # Sade Sati area-specific impact
    if sade_sati and sade_sati.get("active"):
        phase = sade_sati.get("phase", "")
        if phase == "peak":
            # Peak: broad impact across all areas
            for area in penalties:
                penalties[area] -= 0.8
        elif phase == "rising":
            # Rising: mental stress, hidden issues
            penalties["health"] -= 0.6
            penalties["spiritual"] -= 0.4
        elif phase == "setting":
            # Setting: family/money concerns
            penalties["finance"] -= 0.6
            penalties["relationships"] -= 0.4

    # Dhaiya (small panoti): Saturn in 4th or 8th from Moon
    if sade_sati and not sade_sati.get("active"):
        house_from_moon = sade_sati.get("house_from_moon", 0)
        if house_from_moon in (4, 8):
            penalties["health"] -= 0.3
            penalties["career"] -= 0.3

    # Clamp penalties
    return {k: max(v, -3.0) for k, v in penalties.items()}


# ── Hora Lord ──


def get_hora_lord(query_dt: datetime, lat: float, lon: float) -> str:
    """Calculate the current hora (planetary hour) lord.

    Uses sunrise/sunset from Swiss Ephemeris. Day horas start at sunrise,
    night horas at sunset. Each day has 24 horas (12 day + 12 night).
    """
    try:
        from packages.cosmos.src import get_sunrise_sunset

        sunrise_data = get_sunrise_sunset(query_dt, lat, lon)
        sunrise = _strip_tz(sunrise_data["sunrise"])
        sunset = _strip_tz(sunrise_data["sunset"])

        # Approximate local time offset from longitude
        offset = timedelta(hours=lon / 15)
        sunrise_local = sunrise + offset
        sunset_local = sunset + offset

        query_local = _strip_tz(query_dt)
        weekday = query_local.weekday()
        start_idx = _DAY_LORD_INDEX[weekday]

        if sunrise_local <= query_local < sunset_local:
            # Day hora
            day_secs = (sunset_local - sunrise_local).total_seconds()
            hora_dur = day_secs / 12
            elapsed = (query_local - sunrise_local).total_seconds()
            hora_number = int(elapsed / hora_dur) if hora_dur > 0 else 0
        elif query_local >= sunset_local:
            # Night hora (after sunset, same day)
            next_sunrise = sunrise_local + timedelta(days=1)
            night_secs = (next_sunrise - sunset_local).total_seconds()
            hora_dur = night_secs / 12
            elapsed = (query_local - sunset_local).total_seconds()
            hora_number = 12 + (int(elapsed / hora_dur) if hora_dur > 0 else 0)
        else:
            # Before sunrise — use previous day's sunset
            prev_data = get_sunrise_sunset(query_dt - timedelta(days=1), lat, lon)
            prev_sunset = _strip_tz(prev_data["sunset"]) + offset
            night_secs = (sunrise_local - prev_sunset).total_seconds()
            hora_dur = night_secs / 12
            elapsed = (query_local - prev_sunset).total_seconds()
            hora_number = 12 + (int(elapsed / hora_dur) if hora_dur > 0 else 0)
            # Previous day's lord
            start_idx = _DAY_LORD_INDEX[(weekday - 1) % 7]

        lord_idx = (start_idx + hora_number) % 7
        return _HORA_SEQUENCE[lord_idx]

    except Exception as e:
        logger.warning(f"Hora lord computation failed: {e}")
        return _VARA_LORD.get(query_dt.weekday(), "sun")


# ── Area Scores ──


def _compute_area_scores(
    factor_scores: list[dict[str, Any]],
    transit_positions: dict[str, int],
    lagna_index: int,
    transit_result: dict[str, Any] | None = None,
    natal_planets: dict[str, Any] | None = None,
    dosha_penalties: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Compute 5 life area scores from per-house transit analysis.

    Each area maps to specific houses. We score each area by checking
    which planets are transiting those houses and whether those transits
    are favorable or unfavorable — giving each area a distinct score.
    Dosha penalties are applied per-area from natal dosha + transit amplification.
    """
    # Planet transits keyed by planet name, each has house_from_moon + is_favorable
    planet_transits = (transit_result or {}).get("planet_transits", {})

    # Build house → list of (planet, favorable?) from lagna perspective
    house_transits: dict[int, list[tuple[str, bool]]] = {h: [] for h in range(1, 13)}
    for planet_name, rashi_idx in transit_positions.items():
        house = _house_from_lagna(rashi_idx, lagna_index)
        # Check favorability from gochara data
        pt = planet_transits.get(planet_name, {})
        favorable = pt.get("is_favorable", True)  # default favorable if unknown
        house_transits[house].append((planet_name, favorable))

    # Planet strength weights — benefics/malefics matter differently
    _planet_weight = {
        "jupiter": 1.5,
        "venus": 1.2,
        "mercury": 1.0,
        "moon": 1.0,
        "sun": 1.0,
        "mars": 1.2,
        "saturn": 1.5,
        "rahu": 1.3,
        "ketu": 1.0,
    }

    # Natal planet house map — planets sitting in the house natally
    natal_house_map: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    if natal_planets:
        for pname, pdata in natal_planets.items():
            if isinstance(pdata, dict):
                h = int(pdata.get("house", 0))
                if 1 <= h <= 12:
                    natal_house_map[h].append(pname)

    factor_map = {f["id"]: f["score"] for f in factor_scores}
    areas: list[dict[str, Any]] = []

    # House importance weights: primary house matters most
    _house_weights = [0.50, 0.30, 0.20]  # for houses[0], houses[1], houses[2]

    for area_id, houses in AREA_HOUSES.items():
        # 1. Per-house transit scores (weighted by house importance)
        house_scores: list[float] = []
        dominant = AREA_PLANETS.get(area_id, "")
        max_impact = 0.0

        for _i, house in enumerate(houses):
            occupants = house_transits.get(house, [])
            if occupants:
                h_fav = 0.0
                h_total = 0.0
                for planet_name, favorable in occupants:
                    w = _planet_weight.get(planet_name, 1.0)
                    h_total += w
                    h_fav += w if favorable else 0.0
                    if w > max_impact:
                        max_impact = w
                        dominant = planet_name
                house_scores.append((h_fav / h_total * 10.0) if h_total > 0 else 5.0)
            else:
                house_scores.append(5.0)  # empty house = neutral

        # Weighted house score
        house_score = sum(s * _house_weights[i] for i, s in enumerate(house_scores[:3]))

        # 2. Karaka planet's transit quality — area-specific differentiator
        karaka = AREA_PLANETS.get(area_id, "")
        karaka_data = planet_transits.get(karaka, {})
        karaka_house = _house_from_lagna(transit_positions.get(karaka, 0), lagna_index)
        # Karaka in good house from lagna = boost, bad house = drag
        _good_houses = {1, 2, 4, 5, 7, 9, 10, 11}
        karaka_score = 7.0 if karaka_house in _good_houses else 3.0
        if karaka_data.get("is_favorable"):
            karaka_score += 1.0
        else:
            karaka_score -= 1.0

        # 3. Natal strength modifier
        natal_bonus = 0.0
        for house in houses:
            for pname in natal_house_map.get(house, []):
                if pname in ("jupiter", "venus", "mercury"):
                    natal_bonus += 0.5
                elif pname in ("saturn", "mars", "rahu", "ketu"):
                    natal_bonus -= 0.2

        # 4. Blend: house transits (40%) + karaka (20%) + dasha (20%) + panchanga (10%) + natal (10%)
        dasha_score = factor_map.get("dasha", 5.0)
        pan_score = factor_map.get("panchanga", 5.0)
        area_score = (
            house_score * 0.40
            + _clamp(karaka_score) * 0.20
            + dasha_score * 0.20
            + pan_score * 0.10
            + _clamp(5.0 + natal_bonus, 0.0, 10.0) * 0.10
        )

        # 5. Apply dosha & sade sati penalties (per-area)
        if dosha_penalties:
            area_score += dosha_penalties.get(area_id, 0.0)

        area_score = _clamp(area_score)

        # Insight — include dosha/sade sati context
        dosha_drag = dosha_penalties.get(area_id, 0.0) if dosha_penalties else 0.0
        if dosha_drag < -1.0:
            insight = f"Dosha pressure on {area_id} — take extra care"
        elif area_score >= 7.5:
            insight = f"Strong energy for {area_id} today"
        elif area_score >= 5.5:
            insight = f"Moderate support for {area_id}"
        elif area_score >= 3.5:
            insight = f"Be cautious with {area_id} matters"
        else:
            insight = f"Challenging period for {area_id}"

        areas.append(
            {
                "id": area_id,
                "name": _AREA_NAMES.get(area_id, area_id.title()),
                "score": round(area_score, 1),
                "houses": houses,
                "insight": insight,
                "dominant_planet": dominant,
            }
        )

    return areas


# ── Mental State ──


def _mental_state_label(composite: float) -> str:
    """Map composite score to human-readable mental state."""
    if composite >= 8:
        return "Thriving"
    if composite >= 6.5:
        return "Flowing"
    if composite >= 5:
        return "Steady"
    if composite >= 3.5:
        return "Challenged"
    if composite >= 2:
        return "Struggling"
    return "Turbulent"


# ── Public API ──


def compute_state_vector(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, Any],
    moon_longitude: float,
    lagna_rashi: str,
    moon_rashi: str | None = None,
    query_datetime: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """Compute a full state vector for a single datetime.

    Calls existing 108-core functions and normalizes outputs to 0-10.

    Args:
        birth_datetime: Birth date/time ISO string
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        natal_planets: Dict of natal planet positions {name: {longitude, rashi, house}}
        moon_longitude: Moon's longitude at birth (0-360)
        lagna_rashi: Ascendant rashi name (e.g. "libra")
        moon_rashi: Moon rashi name (optional, computed from longitude if missing)
        query_datetime: ISO string for the moment to evaluate (default: now)
        location_lat: Current location latitude (default: birth lat)
        location_lon: Current location longitude (default: birth lon)

    Returns:
        State vector dict with factors, areas, composite, mental_state,
        confluence, and hora_lord.
    """
    # Parse datetimes
    birth_dt = datetime.fromisoformat(birth_datetime)
    query_dt = datetime.fromisoformat(query_datetime) if query_datetime else datetime.now()

    # Location (default to birth location)
    lat = location_lat if location_lat is not None else birth_lat
    lon = location_lon if location_lon is not None else birth_lon
    lagna_index = _rashi_index(lagna_rashi)

    # ── 1. Panchanga ──
    try:
        from packages.cosmos.src import get_panchanga

        panchanga = get_panchanga(query_dt, lat, lon)
    except Exception as e:
        logger.warning(f"Panchanga computation failed: {e}")
        panchanga = {}
    pan_score, pan_planet, pan_desc = _normalize_panchanga(panchanga)

    # ── 2. Transit positions ──
    raw_planets: dict[str, Any] = {}
    try:
        from packages.cosmos.src import get_all_planets, get_julian_day

        jd = get_julian_day(query_dt)
        raw_planets = get_all_planets(jd)
        transit_positions: dict[str, int] = {
            name: int(data.get("longitude", 0) / 30) for name, data in raw_planets.items()
        }
    except Exception as e:
        logger.warning(f"Transit positions failed: {e}")
        transit_positions = {}

    # ── 3. Transit Moon ──
    birth_moon_nak = int(moon_longitude / 13.333333) + 1  # 1-27
    moon_score, moon_planet, moon_desc = _normalize_transit_moon(
        transit_positions,
        lagna_index,
        birth_moon_nak,
        raw_planets if transit_positions else None,
    )

    # ── 4. Gochara ──
    moon_rashi_idx = _rashi_index(moon_rashi) if moon_rashi else int(moon_longitude / 30)
    try:
        from packages.context.src.transits import get_full_transit_analysis

        transit_result = get_full_transit_analysis(moon_rashi_idx, transit_positions)
    except Exception as e:
        logger.warning(f"Gochara computation failed: {e}")
        transit_result = {}
    goc_score, goc_planet, goc_desc = _normalize_gochara(
        transit_result,
        raw_planets if transit_positions else None,
        lagna_index=lagna_index,
    )

    # ── 5. Dasha ──
    try:
        from packages.context.src.dasha import get_current_dasha

        # Strip tzinfo for consistent comparison
        birth_naive = _strip_tz(birth_dt)
        query_naive = _strip_tz(query_dt)
        dasha_result = get_current_dasha(birth_naive, moon_longitude, query_naive)
    except Exception as e:
        logger.warning(f"Dasha computation failed: {e}")
        dasha_result = None
    dsh_score, dsh_planet, dsh_desc = _normalize_dasha(dasha_result, natal_planets)

    # ── 6. Build BirthChart (shared by yogas, doshas, shadbala, ashtakavarga) ──
    try:
        birth_chart = _build_birth_chart(
            birth_dt,
            birth_lat,
            birth_lon,
            natal_planets,
            lagna_rashi,
            moon_rashi,
            moon_longitude,
        )
    except Exception as e:
        logger.warning(f"BirthChart construction failed: {e}")
        birth_chart = None

    # ── 6a. Natal Yogas & Doshas (real detectors: 522 yogas, 55 doshas) ──
    natal_yogas = _detect_natal_yogas(natal_planets, lagna_index, birth_chart)
    natal_doshas = _detect_natal_doshas(natal_planets, lagna_index, birth_chart)

    # Sade Sati detail (already in transit_result, extract for dosha scoring)
    sade_sati_detail = transit_result.get("sade_sati", {})

    # Yoga activation with real natal yoga data
    yog_score, yog_planet, yog_desc = _score_yoga_with_natal(
        natal_yogas,
        transit_positions,
        lagna_index,
        raw_planets if transit_positions else None,
    )

    # Dosha area penalties
    dosha_penalties = _score_dosha_impact(
        natal_doshas, transit_positions, lagna_index, sade_sati_detail
    )

    # ── 7. Shadbala (real 6-component via StrengthCalculator) ──
    shd_score, shd_planet, shd_desc = _score_shadbala(dasha_result, natal_planets, birth_chart)

    # ── 8. Ashtakavarga ──
    ash_score, ash_planet, ash_desc = _score_ashtakavarga(
        transit_positions, lagna_index, birth_chart
    )

    # ── Build factor list ──
    factors = [
        {
            "id": "panchanga",
            "name": "Panchanga",
            "short_name": "PAN",
            "score": round(pan_score, 1),
            "dominant_planet": pan_planet,
            "description": pan_desc,
        },
        {
            "id": "transit_moon",
            "name": "Transit Moon",
            "short_name": "MON",
            "score": round(moon_score, 1),
            "dominant_planet": moon_planet,
            "description": moon_desc,
        },
        {
            "id": "gochara",
            "name": "Gochara",
            "short_name": "GOC",
            "score": round(goc_score, 1),
            "dominant_planet": goc_planet,
            "description": goc_desc,
        },
        {
            "id": "dasha",
            "name": "Dasha",
            "short_name": "DSH",
            "score": round(dsh_score, 1),
            "dominant_planet": dsh_planet,
            "description": dsh_desc,
        },
        {
            "id": "yoga_activation",
            "name": "Yoga",
            "short_name": "YOG",
            "score": round(yog_score, 1),
            "dominant_planet": yog_planet,
            "description": yog_desc,
        },
        {
            "id": "shadbala",
            "name": "Shadbala",
            "short_name": "SHD",
            "score": round(shd_score, 1),
            "dominant_planet": shd_planet,
            "description": shd_desc,
        },
        {
            "id": "ashtakavarga",
            "name": "Ashtakavarga",
            "short_name": "ASH",
            "score": round(ash_score, 1),
            "dominant_planet": ash_planet,
            "description": ash_desc,
        },
    ]

    # ── Composite ──
    composite = sum(f["score"] * FACTOR_WEIGHTS[f["id"]] for f in factors)
    composite = round(composite, 1)

    # ── Mental State ──
    mental_state = _mental_state_label(composite)

    # ── Confluence (0-6): how many factors agree ──
    above_5 = sum(1 for f in factors if f["score"] > 5.0)
    below_5 = sum(1 for f in factors if f["score"] < 5.0)
    agreement = max(above_5, below_5)
    confluence = round(agreement / 7 * 6, 1)

    # ── Hora Lord ──
    hora_lord = get_hora_lord(query_dt, lat, lon)

    # ── Area Scores ──
    areas = _compute_area_scores(
        factors,
        transit_positions,
        lagna_index,
        transit_result=transit_result,
        natal_planets=natal_planets,
        dosha_penalties=dosha_penalties,
    )

    return {
        "date": query_dt.date().isoformat(),
        "factors": factors,
        "areas": areas,
        "composite": composite,
        "mental_state": mental_state,
        "confluence": confluence,
        "hora_lord": hora_lord,
        "natal_yogas": [y["name"] for y in natal_yogas],
        "natal_doshas": [d["name"] for d in natal_doshas],
        "sade_sati": {
            "active": sade_sati_detail.get("active", False),
            "phase": sade_sati_detail.get("phase"),
        },
    }


def compute_state_range(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, Any],
    moon_longitude: float,
    lagna_rashi: str,
    moon_rashi: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    resolution: str = "daily",
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """Compute state vectors for a date range.

    Args:
        resolution: "hourly" | "daily" | "weekly" | "monthly" | "yearly"

    Returns:
        {
            "vectors": [... list of state vectors ...],
            "resolution": "daily",
            "events": []  # populated from DB if available
        }
    """
    now = datetime.now()

    start = (
        datetime.strptime(start_date, "%Y-%m-%d")
        if start_date
        else now.replace(hour=0, minute=0, second=0, microsecond=0)
    )
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else start + timedelta(days=30)

    # Determine step size
    if resolution == "hourly":
        step = timedelta(hours=1)
        # Limit hourly to 48 hours
        if (end - start).days > 2:
            end = start + timedelta(days=2)
    elif resolution == "weekly":
        step = timedelta(days=7)
    elif resolution == "monthly":
        step = timedelta(days=30)
    elif resolution == "yearly":
        step = timedelta(days=365)
    else:  # daily
        step = timedelta(days=1)

    max_vectors = 400
    vectors: list[dict[str, Any]] = []
    current = start

    while current <= end and len(vectors) < max_vectors:
        try:
            vec = compute_state_vector(
                birth_datetime=birth_datetime,
                birth_lat=birth_lat,
                birth_lon=birth_lon,
                natal_planets=natal_planets,
                moon_longitude=moon_longitude,
                lagna_rashi=lagna_rashi,
                moon_rashi=moon_rashi,
                query_datetime=current.isoformat(),
                location_lat=location_lat,
                location_lon=location_lon,
            )
            vectors.append(vec)
        except Exception as e:
            logger.warning(f"Failed to compute state for {current}: {e}")

        current += step

    return {
        "vectors": vectors,
        "resolution": resolution,
        "events": [],
    }
