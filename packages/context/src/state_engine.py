"""State Vector Engine — normalizes 108-core outputs into 0-10 scores.

Computes a StateVector for any given datetime by calling existing
108-core functions (panchanga, gochara, dasha, etc.) and normalizing
all outputs to a unified 0-10 scale.

Each vector contains:
- 7 factor scores (panchanga, transit_moon, gochara, dasha, yoga, shadbala, ashtakavarga)
- 8 area scores (career, relationships, health, finance, spiritual, family, education, travel)
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
    "panchanga": 0.05,  # Muhurta timing quality (background, not predictive)
    "transit_moon": 0.10,  # Chandrashtama + Tarabala (evaluated from natal Moon)
    "gochara": 0.20,  # BAV-modulated planet transits from Moon (BPHS Ch.65-66)
    "dasha": 0.30,  # "Dasha is king" (BPHS Ch.46) + functional nature + Shadbala
    "yoga_activation": 0.15,  # Natal yogas triggered by current transits
    "shadbala": 0.10,  # Natal chart strength context (dasha lord weighted)
    "ashtakavarga": 0.10,  # Chart-specific transit BAV strength
}

# ── Area → House mapping ──

AREA_HOUSES: dict[str, list[int]] = {
    "career": [10, 6, 2],
    "relationships": [7, 5, 11],
    "health": [1, 6, 8],
    "finance": [2, 11, 5],
    "spiritual": [9, 12, 5],
    "family": [4, 2, 1],
    "education": [4, 5, 9],
    "travel": [3, 9, 12],
}

AREA_PLANETS: dict[str, str] = {
    "career": "saturn",
    "relationships": "venus",
    "health": "sun",
    "finance": "jupiter",
    "spiritual": "ketu",
    "family": "moon",
    "education": "mercury",
    "travel": "rahu",
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
    "family": "Family",
    "education": "Education",
    "travel": "Travel",
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
    lagna_index: int,  # noqa: ARG001 — kept for signature compatibility
    birth_moon_nak: int = 0,
    raw_planets: dict[str, Any] | None = None,
    moon_rashi_idx: int = 0,
) -> tuple[float, str, str]:
    """Score Moon's transit from natal Moon sign (BPHS Ch.65) + Tarabala.

    Classical evaluation: Transit Moon judged from natal Moon, NOT lagna.
    Includes Chandrashtama (8th from Moon) — severe 2.5-day penalty.
    Tarabala effects strengthened per Phaladeepika.
    """
    moon_rashi = transit_positions.get("moon", 0)
    # BPHS: evaluate from natal Moon sign (not lagna)
    house_from_moon = ((moon_rashi - moon_rashi_idx) % 12) + 1

    # Moon gochara house scores (from natal Moon per BPHS)
    # Favorable: 1, 3, 6, 7, 10, 11
    house_scores: dict[int, float] = {
        1: 6.5,  # Janma rashi — depends on Tarabala
        2: 4.0,  # Expenses, food concerns
        3: 7.5,  # Courage, success
        4: 4.0,  # Emotional turbulence
        5: 5.0,  # Neutral, mild challenges
        6: 7.0,  # Victory over enemies
        7: 6.5,  # Good for relationships
        8: 2.0,  # CHANDRASHTAMA — worst position
        9: 4.5,  # Mild challenges, travel issues
        10: 8.0,  # Success, authority, respect
        11: 8.5,  # Gains, best position
        12: 3.0,  # Expenses, isolation, loss
    }
    score = house_scores.get(house_from_moon, 5.0)

    # Chandrashtama: 8th from natal Moon (Phaladeepika: no auspicious activity)
    chandrashtama = house_from_moon == 8
    if chandrashtama:
        score -= 1.0  # Additional penalty beyond low house score

    # Tarabala: 9-fold nakshatra relationship (strengthened per classical texts)
    # Tara cycle: 1=Janma, 2=Sampat, 3=Vipat, 4=Kshema,
    #             5=Pratyak, 6=Sadhana, 7=Naidhana, 8=Mitra, 9=ParamaMitra
    tara_name = ""
    if birth_moon_nak >= 1 and raw_planets:
        moon_lon = raw_planets.get("moon", {}).get("longitude", 0)
        transit_nak = int(moon_lon / 13.333333) + 1  # 1-27
        if transit_nak >= 1:
            tara = ((transit_nak - birth_moon_nak) % 9) + 1
            _TARA_ADJ = {
                1: -0.8,  # Janma — stress on mind/body
                2: 1.0,  # Sampat — wealth, gain
                3: -1.5,  # Vipat — danger, sudden obstacles
                4: 1.0,  # Kshema — prosperity, comfort
                5: -1.0,  # Pratyak — obstacles, reversals
                6: 0.8,  # Sadhana — achievement through effort
                7: -2.0,  # Naidhana — worst: severe loss (BPHS)
                8: 0.8,  # Mitra — friendship, support
                9: 1.2,  # Parama Mitra — supreme friendship
            }
            _TARA_NAMES = {
                1: "Janma",
                2: "Sampat",
                3: "Vipat",
                4: "Kshema",
                5: "Pratyak",
                6: "Sadhana",
                7: "Naidhana",
                8: "Mitra",
                9: "Parama Mitra",
            }
            score += _TARA_ADJ.get(tara, 0.0)
            tara_name = _TARA_NAMES.get(tara, "")

    sign_name = RASHI_NAMES[moon_rashi] if 0 <= moon_rashi < 12 else "unknown"
    desc = f"Moon in {sign_name.title()} (H{house_from_moon} from Moon)"
    if tara_name:
        desc += f", {tara_name} tara"
    if chandrashtama:
        desc += " — CHANDRASHTAMA"

    return _clamp(score), "moon", desc


def _normalize_gochara(
    transit_result: dict[str, Any],
    raw_planets: dict[str, Any] | None = None,
    lagna_index: int | None = None,
    birth_chart: BirthChart | None = None,
) -> tuple[float, str, str]:
    """Convert full transit analysis to (score 0-10, dominant_planet, description).

    BPHS Ch.65-66: Per-planet per-house graded scoring from natal Moon.
    Moon excluded (has dedicated transit_moon factor).
    BAV modulation: gochara effects qualified by Ashtakavarga bindus (BPHS Ch.66).
    Vedha: 100% cancellation per classical texts.
    Sade Sati NOT applied here (handled in dosha penalties to avoid triple-count).
    """
    planet_transits = transit_result.get("planet_transits", {})
    if not planet_transits:
        return 5.0, "", "No transit data"

    # Weight planets by astrological significance (slow > fast)
    # Moon excluded — scored separately in transit_moon factor
    _gochara_weight: dict[str, float] = {
        "jupiter": 2.0,
        "saturn": 2.0,
        "rahu": 1.5,
        "ketu": 1.0,
        "mars": 1.2,
        "sun": 1.0,
        "venus": 1.0,
        "mercury": 0.8,
    }

    # Pre-compute lordship roles if lagna available
    lordship_roles: dict[str, dict[str, Any]] = {}
    if lagna_index is not None:
        try:
            from packages.self.src.transit_lordship import classify_planet_role

            for planet in planet_transits:
                if planet != "moon":
                    lordship_roles[planet] = classify_planet_role(planet, lagna_index)
        except Exception:
            pass

    weighted_score = 0.0
    total_weight = 0.0
    dominant = ""
    max_impact = 0.0

    for planet, data in planet_transits.items():
        # Moon scored in dedicated transit_moon factor — skip here
        if planet == "moon":
            continue

        w = _gochara_weight.get(planet, 1.0)

        # 1. Per-house graded score from classical tables
        house_from_moon = data.get("house_from_moon", 0)
        if house_from_moon >= 1:
            base = _GOCHARA_HOUSE_SCORES.get(planet, {}).get(house_from_moon, 5.0)
        else:
            base = 7.5 if data.get("is_favorable") else 3.0

        # 2. Vedha — FULL cancellation per BPHS (not partial)
        if data.get("has_vedha") and data.get("is_favorable"):
            base = 5.0  # 100% cancelled to neutral

        # 3. Sandhi & retrograde from raw longitude data
        if raw_planets and planet in raw_planets:
            pdata = raw_planets[planet]
            lon = pdata.get("longitude", 0)
            deg_in_sign = lon % 30

            # Sandhi: planet at sign boundary is weak
            dist_from_boundary = min(deg_in_sign, 30 - deg_in_sign)
            if dist_from_boundary < 1.0:
                sandhi = 0.7
            elif dist_from_boundary < 3.0:
                sandhi = 0.85
            else:
                sandhi = 1.0
            base = 5.0 + (base - 5.0) * sandhi

            # 4. Retrograde: intensifies the effect (good better, bad worse)
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

        # 6. BAV modulation (BPHS Ch.66: transit qualified by Ashtakavarga)
        # BAV 4/8 = neutral (1.0x), 0/8 = 0.3x effect, 8/8 = 1.7x effect
        if (
            birth_chart is not None
            and planet not in ("rahu", "ketu")
            and raw_planets
            and planet in raw_planets
        ):
            rashi_idx = int(raw_planets[planet].get("longitude", 0) / 30)
            try:
                p_enum = Planet(planet)
                bav = _strength_calculator.calculate_ashtakavarga(p_enum, birth_chart)
                bav_score = float(bav[rashi_idx])
                bav_mult = 0.3 + (bav_score / 8.0) * 1.4  # 0.3x to 1.7x
                base = 5.0 + (base - 5.0) * bav_mult
            except Exception:
                pass

        base = _clamp(base)
        weighted_score += base * w
        total_weight += w

        # Track dominant planet (highest absolute impact)
        impact = abs(base - 5.0) * w
        if impact > max_impact:
            max_impact = impact
            dominant = planet

    score = weighted_score / total_weight if total_weight > 0 else 5.0

    # NOTE: Sade Sati NOT applied here — Saturn's house scores already reflect
    # difficulty in houses 1/2/12 from Moon. Area-specific Sade Sati impact
    # is handled in _score_dosha_impact to avoid triple-counting.

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


# Classical Parashari aspects: planet -> list of houses (from itself) it aspects
_PARASHARI_ASPECTS: dict[str, list[int]] = {
    "sun": [7],
    "moon": [7],
    "mercury": [7],
    "venus": [7],
    "jupiter": [5, 7, 9],
    "mars": [4, 7, 8],
    "saturn": [3, 7, 10],
    "rahu": [5, 7, 9],  # treated like Jupiter
    "ketu": [5, 7, 9],
}

# Slow planet weight for ashtakavarga-transit scoring
_PLANET_TRANSIT_WEIGHT: dict[str, float] = {
    "jupiter": 2.0,
    "saturn": 2.0,
    "mars": 1.2,
    "sun": 0.8,
    "mercury": 0.8,
    "venus": 0.8,
    "moon": 0.6,
    "rahu": 1.5,
    "ketu": 1.0,
}


def _compute_dasha_area_score(
    area_houses: list[int],
    dasha_result: dict[str, Any] | None,
    natal_planets: dict[str, Any],
    lagna_index: int,
) -> float:
    """Multi-signal dasha-area scorer (BPHS classical hierarchy).

    Combines:
    - Lordship (40%): Does MD/AD lord rule any area house?
    - Natal placement (25%): Is MD/AD lord sitting in an area house natally?
    - Natal aspects (10%): Does MD/AD lord aspect any area house?
    - Dignity (15%): MD lord's dignity via _dignity_for_planet()
    - MD x AD relationship (10%): friend/enemy quality

    Returns 0-10 score.
    """
    if not dasha_result:
        return 5.0

    md = dasha_result.get("mahadasha", {})
    ad = dasha_result.get("antardasha", {})
    md_lord = md.get("lord", "")
    ad_lord = ad.get("lord", "")

    if not md_lord:
        return 5.0

    houses_set = set(area_houses)

    # 1. Lordship (40%): does MD/AD lord rule any area house?
    lordship_score = 0.0
    try:
        from packages.self.src.transit_lordship import get_planet_lordships

        md_houses = set(get_planet_lordships(md_lord, lagna_index)) if md_lord else set()
        ad_houses = set(get_planet_lordships(ad_lord, lagna_index)) if ad_lord else set()

        md_overlap = len(md_houses & houses_set)
        ad_overlap = len(ad_houses & houses_set)

        if md_overlap > 0:
            lordship_score += 7.0 + md_overlap  # 8-9 for 1-2 house overlap
        if ad_overlap > 0:
            lordship_score += 3.0 + ad_overlap * 0.5  # 3.5-4 boost
        if md_overlap == 0 and ad_overlap == 0:
            lordship_score = 3.0  # no connection
    except Exception:
        lordship_score = 5.0

    lordship_score = _clamp(lordship_score)

    # 2. Natal placement (25%): is MD/AD lord sitting in an area house natally?
    placement_score = 3.0  # default: not in area house
    for lord in [md_lord, ad_lord]:
        if lord and natal_planets:
            p_data = natal_planets.get(lord, {})
            if isinstance(p_data, dict):
                natal_house = int(p_data.get("house", 0))
                if natal_house in houses_set:
                    placement_score = 8.0 if lord == md_lord else max(placement_score, 6.5)

    # 3. Natal aspects (10%): does MD/AD lord aspect any area house?
    aspect_score = 3.0
    for lord in [md_lord, ad_lord]:
        if lord and natal_planets:
            p_data = natal_planets.get(lord, {})
            if isinstance(p_data, dict):
                natal_house = int(p_data.get("house", 0))
                if natal_house > 0:
                    aspect_houses_from = _PARASHARI_ASPECTS.get(lord, [7])
                    aspected_houses = {
                        ((natal_house - 1 + off) % 12) + 1 for off in aspect_houses_from
                    }
                    if aspected_houses & houses_set:
                        mult = 1.0 if lord == md_lord else 0.6
                        aspect_score = max(aspect_score, 3.0 + 5.0 * mult)

    # 4. Dignity (15%): MD lord's dignity
    dignity_score = _dignity_for_planet(md_lord, natal_planets)

    # 5. MD x AD relationship (10%)
    relationship_score = 5.0
    try:
        from packages.core.src.knowledge_loader import get_antardasha_effects

        all_effects = get_antardasha_effects()
        ad_effects = all_effects.get(md_lord, {}).get(ad_lord, {})
        relationship = ad_effects.get("relationship", "neutral")
        rel_map = {"friend": 8.0, "same": 6.5, "neutral": 5.0, "enemy": 2.0}
        relationship_score = rel_map.get(relationship, 5.0)
    except Exception:
        pass

    # Blend
    score = (
        lordship_score * 0.40
        + placement_score * 0.25
        + aspect_score * 0.10
        + dignity_score * 0.15
        + relationship_score * 0.10
    )
    return _clamp(score)


def _compute_ashtakavarga_transit_score(
    area_houses: list[int],
    transit_positions: dict[str, int],
    lagna_index: int,
    birth_chart: Any | None,
) -> float:
    """Score transits through area houses weighted by Ashtakavarga bindus.

    For each planet transiting an area house, multiply gochara house quality
    by BAV bindus (0-8 -> multiplier 0.25-1.75). Weight slow planets more.

    Returns 0-10 score.
    """
    houses_set = set(area_houses)

    planet_enum_map = {
        "sun": Planet.SUN,
        "moon": Planet.MOON,
        "mars": Planet.MARS,
        "mercury": Planet.MERCURY,
        "jupiter": Planet.JUPITER,
        "venus": Planet.VENUS,
        "saturn": Planet.SATURN,
    }

    weighted_scores: list[float] = []
    total_weight = 0.0

    for planet_name, rashi_idx in transit_positions.items():
        house = _house_from_lagna(rashi_idx, lagna_index)
        if house not in houses_set:
            continue

        # Base quality from gochara house scores
        gochara_scores = _GOCHARA_HOUSE_SCORES.get(planet_name, {})
        base_quality = gochara_scores.get(house, 5.0)

        # BAV multiplier
        bav_multiplier = 1.0
        if birth_chart is not None:
            p_enum = planet_enum_map.get(planet_name)
            if p_enum is not None:
                try:
                    bav = _strength_calculator.calculate_ashtakavarga(p_enum, birth_chart)
                    bav_score = float(bav[rashi_idx])
                    bav_multiplier = 0.25 + (bav_score / 8.0) * 1.5  # 0.25-1.75
                except Exception:
                    pass

        # Planet weight (slow planets matter more)
        p_weight = _PLANET_TRANSIT_WEIGHT.get(planet_name, 1.0)

        weighted_scores.append(base_quality * bav_multiplier * p_weight)
        total_weight += p_weight

    if total_weight > 0:
        return _clamp(sum(weighted_scores) / total_weight)

    # Fallback: SAV of area house signs
    if birth_chart is not None:
        try:
            sav = _strength_calculator.calculate_sarvashtakavarga(birth_chart)
            sav_scores = []
            for house in area_houses:
                sign = (lagna_index + house - 1) % 12
                sav_scores.append(float(sav[sign]))
            avg_sav = sum(sav_scores) / len(sav_scores)
            return _clamp(avg_sav / 337 * 12 * 10)  # SAV total ~337, per sign ~28, scale 0-10
        except Exception:
            pass

    return 5.0  # neutral fallback


def _compute_double_transit_area_score(
    area_houses: list[int],
    house_activations: list[dict[str, Any]] | None,
) -> tuple[float, bool]:
    """Score double transit activation for area houses.

    Returns (score, has_double_transit_bool).
    - Primary house has DT -> 10.0
    - Secondary house has DT -> 7.0
    - No DT -> 3.0
    """
    if not house_activations:
        return 3.0, False

    ha_map = {ha.get("house", 0): ha for ha in house_activations}

    primary = area_houses[0] if area_houses else 0
    secondary = area_houses[1] if len(area_houses) > 1 else 0

    if ha_map.get(primary, {}).get("double_transit"):
        return 10.0, True
    if ha_map.get(secondary, {}).get("double_transit"):
        return 7.0, True

    # Check tertiary
    for h in area_houses[2:]:
        if ha_map.get(h, {}).get("double_transit"):
            return 5.5, True

    return 3.0, False


def _normalize_dasha(
    dasha_result: dict[str, Any] | None,
    natal_planets: dict[str, Any],
    lagna_index: int = 0,
    birth_chart: BirthChart | None = None,
) -> tuple[float, str, str]:
    """Score current dasha using BPHS classical hierarchy.

    BPHS Ch.46: "Dasha is the king of all predictive methods."

    Components:
    - Functional nature per lagna (35%): yogakaraka vs malefic vs maraka
    - Natal dignity (25%): exaltation/debilitation/own sign
    - House lordship quality (15%): trine lord vs dusthana lord
    - MD x AD relationship (15%): friend/enemy quality
    - Shadbala modifier (10%): natal strength of dasha lords
    """
    if not dasha_result:
        return 5.0, "", "Dasha data unavailable"

    md = dasha_result.get("mahadasha", {})
    ad = dasha_result.get("antardasha", {})
    pd = dasha_result.get("pratyantardasha", {})

    md_lord = md.get("lord", "")
    ad_lord = ad.get("lord", "")
    pd_lord = pd.get("lord", "")

    if not md_lord:
        return 5.0, "", "Dasha lord unknown"

    # 1. Functional nature per lagna (35%) — THE most critical dasha factor
    # Saturn for Libra lagna (yogakaraka) vs Saturn for Leo lagna (malefic+maraka)
    functional_score = 5.0
    md_nature_label = ""
    try:
        from packages.self.src.transit_lordship import classify_planet_role

        md_role = classify_planet_role(md_lord, lagna_index)
        md_nature = md_role.get("functional_nature", "neutral")
        md_nature_label = md_nature
        functional_score = _NATURE_SCORE.get(md_nature, 5.0)

        if ad_lord:
            ad_role = classify_planet_role(ad_lord, lagna_index)
            ad_nature = ad_role.get("functional_nature", "neutral")
            ad_func = _NATURE_SCORE.get(ad_nature, 5.0)
            # MD dominates (60/40 blend)
            functional_score = functional_score * 0.6 + ad_func * 0.4
    except Exception:
        pass

    # 2. Natal dignity (25%): how strong is the lord in the birth chart
    md_dig = _dignity_for_planet(md_lord, natal_planets)
    ad_dig = _dignity_for_planet(ad_lord, natal_planets) if ad_lord else 5.0
    dignity_score = md_dig * 0.6 + ad_dig * 0.4

    # 3. House lordship quality (15%): trine lord (1,5,9) > kendra (4,7,10) > dusthana (6,8,12)
    lordship_score = 5.0
    try:
        from packages.self.src.transit_lordship import get_planet_lordships

        md_houses = set(get_planet_lordships(md_lord, lagna_index)) if md_lord else set()
        trine = {1, 5, 9}
        kendra = {4, 7, 10}
        dusthana = {6, 8, 12}

        if md_houses & trine:
            lordship_score = 8.5
        elif md_houses & kendra:
            lordship_score = 6.5
        elif md_houses & dusthana:
            lordship_score = 2.5
        # Upachaya (3,6,11): moderate — natural malefics do well, benefics less so
        elif md_houses & {3, 11}:
            lordship_score = 5.5
    except Exception:
        pass

    # 4. MD x AD relationship quality (15%)
    relationship_score = 5.0
    ad_effects: dict[str, Any] = {}
    try:
        from packages.core.src.knowledge_loader import get_antardasha_effects

        all_effects = get_antardasha_effects()
        ad_effects = all_effects.get(md_lord, {}).get(ad_lord, {})
        relationship = ad_effects.get("relationship", "neutral")
        rel_map = {"friend": 8.0, "same": 6.5, "neutral": 5.0, "enemy": 2.0}
        relationship_score = rel_map.get(relationship, 5.0)
    except Exception:
        pass

    # 5. Shadbala modifier (10%): natal strength of dasha lords
    shadbala_score = 5.0
    if birth_chart:
        try:
            all_strengths = _strength_calculator.get_all_planet_strengths(birth_chart)
            md_virupas = float(all_strengths.get(md_lord, {}).get("total", 0.0))
            shadbala_score = _virupas_to_score(md_virupas)
        except Exception:
            pass

    # Blend per BPHS hierarchy
    score = (
        functional_score * 0.35
        + dignity_score * 0.25
        + lordship_score * 0.15
        + relationship_score * 0.15
        + shadbala_score * 0.10
    )

    # Build rich description
    desc = f"{md_lord.title()} MD"
    if md_nature_label:
        desc += f" ({md_nature_label})"
    if ad_lord:
        desc += f" / {ad_lord.title()} AD"
    rel = ad_effects.get("relationship", "")
    if rel:
        desc += f" ({rel})"
    if pd_lord:
        desc += f" / {pd_lord.title()} PD"

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
) -> tuple[list[dict[str, Any]], list[Any]]:
    """Detect natal yogas using real YogaDetector (522 rules from knowledge).

    When birth_chart is available, delegates to YogaDetector.detect_all_yogas()
    which evaluates all 522 yoga rules from yoga_master.json.
    Returns tuple of (list of yoga dicts, list of raw DetectedYoga objects).
    """
    if birth_chart is None:
        return [], []

    try:
        detected = _yoga_detector.detect_all_yogas(birth_chart)
    except Exception as e:
        logger.warning(f"YogaDetector failed: {e}")
        return [], []

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

    return yogas, detected


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
        "kaal sarp": ["career", "health", "spiritual", "travel"],
        "pitra": ["spiritual", "finance"],
        "guru chandal": ["spiritual", "career"],
        "grahan": ["health", "spiritual"],
        "kemdrum": ["finance", "relationships", "family"],
        "shakat": ["career", "health", "education"],
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
    vry_yogas: list[dict[str, Any]] | None = None,
    dasha_lords: tuple[str, str] | None = None,
) -> tuple[float, str, str]:
    """Score yoga activation using actual natal yogas + transit activation.

    Combines generic transit quality with natal yoga activation check, plus
    Vipreet Raja Yoga activation when a VRY lord runs as MD/AD.
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

    # ── Vipreet Raja Yoga activation (BPHS) ──
    # When MD or AD lord = natal VRY lord, the yoga manifests as success
    # arising from defeated enemies / overcome obstacles / dissolved losses.
    vry_active: list[str] = []
    if vry_yogas and dasha_lords:
        md_lord, ad_lord = dasha_lords
        for vry in vry_yogas:
            lord = vry.get("lord_planet", "")
            if lord and lord == md_lord:
                base_score += 1.2  # MD activation = strong
                vry_active.append(f"{vry['name']} (MD)")
                dominant = lord
            elif lord and lord == ad_lord:
                base_score += 0.6  # AD activation = moderate
                vry_active.append(f"{vry['name']} (AD)")

    total = len(natal_yogas)
    desc = f"{active_count}/{total} yogas active" + (
        f" ({', '.join(active_names[:3])})" if active_names else ""
    )
    if vry_active:
        desc += f" + VRY active: {', '.join(vry_active)}"

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
        "family": 0.0,
        "education": 0.0,
        "travel": 0.0,
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

    # Sade Sati area-specific impact (single calculation point — not in gochara)
    # Saturn's gochara house scores already reflect general difficulty in H1/2/12.
    # These area penalties capture the nuanced per-area Sade Sati effects.
    if sade_sati and sade_sati.get("active"):
        phase = sade_sati.get("phase", "")
        if phase == "peak":
            penalties["health"] -= 0.6
            penalties["career"] -= 0.5
            penalties["relationships"] -= 0.4
            penalties["family"] -= 0.5
            penalties["finance"] -= 0.3
            penalties["spiritual"] -= 0.2
        elif phase == "rising":
            penalties["health"] -= 0.4
            penalties["spiritual"] -= 0.3
        elif phase == "setting":
            penalties["finance"] -= 0.4
            penalties["relationships"] -= 0.3
            penalties["family"] -= 0.4

    # Dhaiya (small panoti): Saturn in 4th or 8th from Moon
    if sade_sati and not sade_sati.get("active"):
        house_from_moon = sade_sati.get("house_from_moon", 0)
        if house_from_moon in (4, 8):
            penalties["health"] -= 0.2
            penalties["career"] -= 0.2

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


_NATURE_SCORE: dict[str, float] = {
    "yogakaraka": 9.0,
    "benefic": 7.5,
    "neutral": 5.0,
    "malefic": 3.0,
    "maraka": 2.0,
}

_NATURE_ASPECT_SCORE: dict[str, float] = {
    "harmonious": 8.0,
    "intense": 7.0,
    "neutral": 5.0,
    "tense": 3.5,
    "challenging": 2.5,
}


def _compute_natal_support_score(
    area_id: str,
    area_houses: list[int],
    natal_planets: dict[str, Any],
    lagna_index: int,
    birth_chart: BirthChart | None,
) -> tuple[float, dict[str, Any]]:
    """Score the natal "structural support" for a life area.

    BPHS principle: a house's results depend on (1) its lord, (2) its karaka,
    (3) the dispositor of its karaka, (4) Jaimini argala on the house. The
    other area components score current/transit conditions; this one scores
    the FIXED natal support that conditions everything else.

    Two sub-signals (each 0-10):
    1. Karaka dispositor (60%): for the area's natural karaka, find its natal
       sign-lord (dispositor). Score by the dispositor's house placement,
       dignity, and functional role for the lagna. A dispositor in
       kendra/trikona = strong long-term support; in dusthana = persistent drag.
    2. Argala on primary house (40%): Jaimini intervention from the 2nd, 4th,
       5th, 11th from the area's primary house, net of obstruction.

    Returns (score 0-10, debug_info dict).
    """
    karaka = AREA_PLANETS.get(area_id, "")
    primary_house = area_houses[0] if area_houses else 1

    info: dict[str, Any] = {
        "karaka": karaka,
        "primary_house": primary_house,
    }

    # ── 1. Karaka dispositor sub-score ──
    dispositor_score = 5.0
    dispositor_planet: str | None = None
    karaka_data = natal_planets.get(karaka, {}) if karaka else {}
    if isinstance(karaka_data, dict):
        karaka_lon = float(karaka_data.get("longitude", 0.0))
        karaka_rashi_idx = (
            int(karaka_lon // 30) % 12 if karaka_lon else int(karaka_data.get("rashi", -1))
        )
        if 0 <= karaka_rashi_idx < 12:
            # Sign lord = dispositor
            from packages.cosmos.src.houses import SIGN_RULERS

            dispositor_planet = SIGN_RULERS.get(karaka_rashi_idx)
            if dispositor_planet:
                disp_data = natal_planets.get(dispositor_planet, {})
                if isinstance(disp_data, dict):
                    disp_lon = float(disp_data.get("longitude", 0.0))
                    disp_rashi_idx = (
                        int(disp_lon // 30) % 12 if disp_lon else int(disp_data.get("rashi", -1))
                    )
                    disp_house = int(disp_data.get("house", 0))
                    if disp_house <= 0 and 0 <= disp_rashi_idx < 12:
                        disp_house = _house_from_lagna(disp_rashi_idx, lagna_index)

                    # House quality (Kendra/Trikona vs Dusthana)
                    if disp_house in (1, 5, 9):
                        dispositor_score = 8.5
                    elif disp_house in (4, 7, 10):
                        dispositor_score = 7.5
                    elif disp_house in (2, 11):
                        dispositor_score = 6.5
                    elif disp_house in (3,):
                        dispositor_score = 5.5
                    elif disp_house in (6, 8, 12):
                        dispositor_score = 3.0
                    else:
                        dispositor_score = 5.0

                    # Dignity adjustment
                    dispositor_score += (
                        _dignity_for_planet(dispositor_planet, natal_planets) - 5.0
                    ) * 0.3

                    # Functional nature for the lagna
                    try:
                        from packages.self.src.transit_lordship import classify_planet_role

                        role = classify_planet_role(dispositor_planet, lagna_index)
                        nature = role.get("functional_nature", "neutral")
                        nature_adj = {
                            "yogakaraka": 1.5,
                            "benefic": 0.8,
                            "neutral": 0.0,
                            "malefic": -0.8,
                            "maraka": -0.5,
                        }.get(nature, 0.0)
                        dispositor_score += nature_adj
                        info["dispositor_nature"] = nature
                    except Exception:
                        pass

                    info["dispositor"] = dispositor_planet
                    info["dispositor_house"] = disp_house

    dispositor_score = _clamp(dispositor_score)

    # ── 2. Argala on primary house ──
    argala_score = 5.0
    argala_active = 0
    if birth_chart is not None:
        try:
            from packages.self.src.jaimini import calculate_argala

            arg = calculate_argala(birth_chart)
            primary = arg.get(primary_house, {})
            argala_active = int(primary.get("active_argala_count", 0))
            # 0 active = no support (3.0); 4 active = full Dhana+Sukha+Labha+Putra (9.0)
            argala_score = 3.0 + 1.5 * argala_active
            argala_score = _clamp(argala_score)
            info["argala_active_count"] = argala_active
        except Exception as e:  # pragma: no cover
            logger.debug(f"Argala calculation failed for {area_id}: {e}")

    # Blend: dispositor 60%, argala 40%
    score = dispositor_score * 0.60 + argala_score * 0.40
    info["dispositor_score"] = round(dispositor_score, 2)
    info["argala_score"] = round(argala_score, 2)
    return _clamp(score), info


def _detect_vipreet_raja_yogas(
    natal_planets: dict[str, Any],
    lagna_index: int,
) -> list[dict[str, Any]]:
    """Detect Harsha (6L), Sarala (8L), Vimala (12L) Vipreet Raja Yogas.

    Per BPHS: dusthana lords (6/8/12) lose dignity in normal terms, but when
    they sit in another dusthana house, the "negative + negative = positive"
    yoga forms — the planet's affliction-causing potential gets neutralized
    and turns into raja yoga. These are the Vipreet ("reversed") Raja Yogas.

    Returns list of {name, lord_planet, lord_of_house, sits_in_house}.
    Activation = when this lord runs as MD/AD or transits a kendra/trikona.
    """
    yogas: list[dict[str, Any]] = []
    try:
        from packages.self.src.transit_lordship import get_planet_lordships
    except Exception:
        return yogas

    dusthanas = {6, 8, 12}
    yoga_names = {6: "Harsha Yoga", 8: "Sarala Yoga", 12: "Vimala Yoga"}

    for planet, pdata in natal_planets.items():
        if not isinstance(pdata, dict):
            continue
        ruled = get_planet_lordships(planet.lower(), lagna_index)
        if not any(h in dusthanas for h in ruled):
            continue
        # Use natal house if provided, else derive from longitude
        natal_house = int(pdata.get("house", 0))
        if natal_house <= 0:
            lon = float(pdata.get("longitude", 0.0))
            natal_house = _house_from_lagna(int(lon // 30) % 12, lagna_index)
        if natal_house not in dusthanas:
            continue
        # Find the dusthana house this planet rules (the one creating the yoga)
        for h in ruled:
            if h in dusthanas:
                yogas.append(
                    {
                        "name": yoga_names[h],
                        "lord_planet": planet.lower(),
                        "lord_of_house": h,
                        "sits_in_house": natal_house,
                    }
                )
    return yogas


def _compute_area_scores(
    factor_scores: list[dict[str, Any]],
    transit_positions: dict[str, int],
    lagna_index: int,
    transit_result: dict[str, Any] | None = None,  # noqa: ARG001
    natal_planets: dict[str, Any] | None = None,
    dosha_penalties: dict[str, float] | None = None,
    house_activations: list[dict[str, Any]] | None = None,
    transit_lordships: list[dict[str, Any]] | None = None,
    transit_aspects: list[dict[str, Any]] | None = None,  # noqa: ARG001
    active_yogas: list[dict[str, Any]] | None = None,
    dasha_result: dict[str, Any] | None = None,
    birth_chart: Any | None = None,
) -> list[dict[str, Any]]:
    """Compute 8 life area scores using BPHS-aligned 6-component model.

    Classical hierarchy (Brihat Parashara Hora Shastra + Jaimini):
    1. Dasha Analysis (35%) — lordship, natal placement, aspects, dignity, MD x AD
    2. Ashtakavarga-Weighted Transits (25%) — BAV bindus filter transit strength
    3. Double Transit (15%) — Jupiter + Saturn activation
    4. Natal Support (10%) — karaka dispositor placement + Jaimini argala
    5. Yoga/Dosha Status (10%) — active yogas boost, doshas penalize
    6. Panchanga Baseline (5%) — daily timing quality (muhurta, not predictive)

    Falls back to simplified model when birth_chart unavailable.
    """
    factor_map = {f["id"]: f["score"] for f in factor_scores}

    # Determine lordship quality from transit lordships for output
    def _best_lordship_nature(houses_set: set[int]) -> str:
        best = "neutral"
        for tl in transit_lordships or []:
            ruled = set(tl.get("houses_ruled", []))
            if ruled & houses_set:
                nature = tl.get("functional_nature", "neutral")
                if _NATURE_SCORE.get(nature, 5.0) > _NATURE_SCORE.get(best, 5.0):
                    best = nature
        return best

    areas: list[dict[str, Any]] = []

    for area_id, houses in AREA_HOUSES.items():
        houses_set = set(houses)
        dominant = AREA_PLANETS.get(area_id, "")

        # ── Component 1: Dasha Analysis (40%) — BPHS: "Dasha is king" ──
        dasha_area = _compute_dasha_area_score(
            houses, dasha_result, natal_planets or {}, lagna_index
        )

        # ── Component 2: Ashtakavarga-Weighted Transits (25%) ──
        ashta_transit = _compute_ashtakavarga_transit_score(
            houses, transit_positions, lagna_index, birth_chart
        )

        # ── Component 3: Double Transit (15%) ──
        dt_score, has_double_transit = _compute_double_transit_area_score(houses, house_activations)

        # ── Component 4: Natal Support (karaka dispositor + Jaimini argala) ──
        natal_support, natal_support_info = _compute_natal_support_score(
            area_id, houses, natal_planets or {}, lagna_index, birth_chart
        )

        # ── Component 5: Yoga/Dosha Status (10%) ──
        yoga_dosha = 5.0  # neutral base
        area_active_yogas: list[str] = []
        for ay in active_yogas or []:
            activated = set(ay.get("activated_houses", []))
            involved = set(ay.get("involved_houses", []))
            if ay.get("is_active_now") and (activated | involved) & houses_set:
                yoga_dosha += ay.get("strength", 0.5) * 2.0
                area_active_yogas.append(ay.get("yoga_name", ""))

        # ── Component 6: Panchanga Baseline (5%) ──
        pan_score = factor_map.get("panchanga", 5.0)

        # ── Final BPHS + Jaimini blend ──
        area_score = (
            _clamp(dasha_area) * 0.35
            + _clamp(ashta_transit) * 0.25
            + _clamp(dt_score) * 0.15
            + _clamp(natal_support) * 0.10
            + _clamp(yoga_dosha) * 0.10
            + _clamp(pan_score) * 0.05
        )

        # Track dominant planet from house activation or transit
        if house_activations:
            ha_map_local = {ha.get("house", 0): ha for ha in house_activations}
            for h in houses:
                ha_data = ha_map_local.get(h, {})
                present = ha_data.get("planets_present", [])
                if present:
                    dominant = present[0] if isinstance(present[0], str) else dominant

        # Lordship quality for output
        best_nature = _best_lordship_nature(houses_set)

        # ── Apply dosha & sade sati penalties (per-area) ──
        if dosha_penalties:
            area_score += dosha_penalties.get(area_id, 0.0)

        area_score = _clamp(area_score)

        # Insight
        dosha_drag = dosha_penalties.get(area_id, 0.0) if dosha_penalties else 0.0
        if dosha_drag < -1.0:
            insight = f"Dosha pressure on {area_id} — take extra care"
        elif has_double_transit and area_score >= 6.0:
            insight = f"Strong double transit activating {area_id}"
        elif area_score >= 7.5:
            insight = f"Strong energy for {area_id} today"
        elif area_score >= 5.5:
            insight = f"Moderate support for {area_id}"
        elif area_score >= 3.5:
            insight = f"Be cautious with {area_id} matters"
        else:
            insight = f"Challenging period for {area_id}"

        area_dict: dict[str, Any] = {
            "id": area_id,
            "name": _AREA_NAMES.get(area_id, area_id.title()),
            "score": round(area_score, 1),
            "houses": houses,
            "insight": insight,
            "dominant_planet": dominant,
            "double_transit": has_double_transit,
            "active_yogas": area_active_yogas,
            "lordship_quality": best_nature,
            "natal_support": {
                "score": round(natal_support, 1),
                **natal_support_info,
            },
        }
        areas.append(area_dict)

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

    # Rich transit positions for house_activation + transit_lordship
    transit_positions_rich: dict[str, dict[str, Any]] = {}
    for name, data in raw_planets.items():
        lng = float(data.get("longitude", 0))
        transit_positions_rich[name] = {
            "longitude": lng,
            "rashi_num": int(lng / 30),
            "speed": data.get("speed", 0),
        }

    # ── 3. Build BirthChart early (shared by gochara BAV, dasha, yogas, etc.) ──
    moon_rashi_idx = _rashi_index(moon_rashi) if moon_rashi else int(moon_longitude / 30)
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

    # ── 4. Transit Moon (from natal Moon per BPHS Ch.65, not lagna) ──
    birth_moon_nak = int(moon_longitude / 13.333333) + 1  # 1-27
    moon_score, moon_planet, moon_desc = _normalize_transit_moon(
        transit_positions,
        lagna_index,
        birth_moon_nak,
        raw_planets if transit_positions else None,
        moon_rashi_idx=moon_rashi_idx,
    )

    # ── 5. Gochara (BAV-modulated, Moon excluded, 100% Vedha) ──
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
        birth_chart=birth_chart,
    )

    # ── 6. Dasha (functional nature + lordship + shadbala per BPHS) ──
    try:
        from packages.context.src.dasha import get_current_dasha

        # Strip tzinfo for consistent comparison
        birth_naive = _strip_tz(birth_dt)
        query_naive = _strip_tz(query_dt)
        dasha_result = get_current_dasha(birth_naive, moon_longitude, query_naive)
    except Exception as e:
        logger.warning(f"Dasha computation failed: {e}")
        dasha_result = None
    dsh_score, dsh_planet, dsh_desc = _normalize_dasha(
        dasha_result, natal_planets, lagna_index=lagna_index, birth_chart=birth_chart
    )

    # ── 7a. Natal Yogas & Doshas (real detectors: 522 yogas, 55 doshas) ──
    natal_yogas, natal_yogas_raw = _detect_natal_yogas(natal_planets, lagna_index, birth_chart)
    natal_doshas = _detect_natal_doshas(natal_planets, lagna_index, birth_chart)
    natal_vry = _detect_vipreet_raja_yogas(natal_planets, lagna_index)

    # Sade Sati detail (already in transit_result, extract for dosha scoring)
    sade_sati_detail = transit_result.get("sade_sati", {})

    # Pull current MD/AD lords for VRY activation check
    _md_lord = (dasha_result or {}).get("mahadasha", {}).get("lord", "") if dasha_result else ""
    _ad_lord = (dasha_result or {}).get("antardasha", {}).get("lord", "") if dasha_result else ""

    # Yoga activation with real natal yoga data + VRY activation by current dasha
    yog_score, yog_planet, yog_desc = _score_yoga_with_natal(
        natal_yogas,
        transit_positions,
        lagna_index,
        raw_planets if transit_positions else None,
        vry_yogas=natal_vry,
        dasha_lords=(_md_lord, _ad_lord) if _md_lord else None,
    )

    # Dosha area penalties
    dosha_penalties = _score_dosha_impact(
        natal_doshas, transit_positions, lagna_index, sade_sati_detail
    )

    # ── 7b. House Activations, Transit Lordships, Transit Aspects, Yoga Activation ──
    house_activations: list[dict[str, Any]] = []
    if transit_positions_rich:
        try:
            from packages.context.src.house_activation import get_house_activations

            house_activations = get_house_activations(
                transit_positions_rich, lagna_index, moon_rashi_idx, birth_chart
            )
        except Exception as e:
            logger.warning(f"House activation failed: {e}")

    transit_lordships: list[dict[str, Any]] = []
    if transit_positions_rich:
        try:
            from packages.self.src.transit_lordship import analyze_transit_lordships

            transit_lordships = analyze_transit_lordships(transit_positions_rich, lagna_index)
        except Exception as e:
            logger.warning(f"Transit lordship failed: {e}")

    transit_aspects: list[dict[str, Any]] = []
    if transit_positions_rich and natal_planets:
        try:
            from packages.context.src.transit_aspects import get_transit_natal_aspects

            natal_for_aspects = {
                name: {"longitude": float(d.get("longitude", 0))}
                for name, d in natal_planets.items()
                if isinstance(d, dict)
            }
            transit_aspects = get_transit_natal_aspects(natal_for_aspects, transit_positions_rich)
        except Exception as e:
            logger.warning(f"Transit aspects failed: {e}")

    active_yogas: list[dict[str, Any]] = []
    if natal_yogas_raw and house_activations:
        try:
            from packages.self.src.yoga_activation import get_active_yogas

            active_yogas = get_active_yogas(natal_yogas_raw, house_activations)
        except Exception as e:
            logger.warning(f"Yoga activation failed: {e}")

    # ── 8. Shadbala (real 6-component via StrengthCalculator) ──
    shd_score, shd_planet, shd_desc = _score_shadbala(dasha_result, natal_planets, birth_chart)

    # ── 9. Ashtakavarga ──
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
        house_activations=house_activations,
        transit_lordships=transit_lordships,
        transit_aspects=transit_aspects,
        active_yogas=active_yogas,
        dasha_result=dasha_result,
        birth_chart=birth_chart,
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
        "natal_vipreet_raja_yogas": natal_vry,
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


def compute_area_trend(
    current_areas: list[dict[str, Any]],
    previous_areas: list[dict[str, Any]],
    threshold: float = 0.5,
) -> dict[str, str]:
    """Compare current vs previous area scores to determine trends.

    Args:
        current_areas: Current area score dicts (from compute_state_vector).
        previous_areas: Previous period area score dicts.
        threshold: Minimum score difference to register as up/down.

    Returns:
        Dict mapping area_id -> "up" | "down" | "neutral".
    """
    prev_map = {a["id"]: a["score"] for a in previous_areas}
    trends: dict[str, str] = {}
    for area in current_areas:
        area_id = area["id"]
        current_score = area["score"]
        prev_score = prev_map.get(area_id, current_score)
        diff = current_score - prev_score
        if diff > threshold:
            trends[area_id] = "up"
        elif diff < -threshold:
            trends[area_id] = "down"
        else:
            trends[area_id] = "neutral"
    return trends
