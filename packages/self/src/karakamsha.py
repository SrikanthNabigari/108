"""
Karakamsha Lagna — Jaimini soul-level analysis from BPHS Chapter 35.

The Atmakaraka's navamsha sign = Karakamsha Lagna (KL).
Houses from KL reveal soul-level karma for each life theme.
This is different from natal lagna — it shows WHY the soul is here
and what deep karmic patterns are operating.
"""
from __future__ import annotations

from typing import Any

SIGNS = [
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
SIGN_TO_INDEX = {s.lower(): i for i, s in enumerate(SIGNS)}

SIGN_LORDS = {
    "Aries": "mars",
    "Taurus": "venus",
    "Gemini": "mercury",
    "Cancer": "moon",
    "Leo": "sun",
    "Virgo": "mercury",
    "Libra": "venus",
    "Scorpio": "mars",
    "Sagittarius": "jupiter",
    "Capricorn": "saturn",
    "Aquarius": "saturn",
    "Pisces": "jupiter",
}

# Navamsha calculation
_ELEMENT_START = {0: 0, 3: 3, 6: 6, 9: 9}  # fire→Aries, water→Cancer, air→Libra, earth→Capricorn


def _get_navamsha_sign(longitude: float) -> str:
    lon = longitude % 360
    sign_idx = int(lon / 30)
    degree = lon % 30
    nav_num = int(degree / (30 / 9))
    nav_num = min(nav_num, 8)
    element = sign_idx % 4  # 0=fire,1=earth,2=air,3=water
    start = [0, 9, 6, 3][element]
    result_idx = (start + nav_num) % 12
    return SIGNS[result_idx]


def get_atmakaraka(natal_planets: dict[str, dict[str, Any]]) -> tuple[str, float]:
    """Find Atmakaraka — planet with highest degree in its sign (excl. Rahu/Ketu)."""
    exclude = {"rahu", "ketu"}
    max_deg = -1.0
    atmakaraka = "sun"
    for planet, data in natal_planets.items():
        if planet.lower() in exclude:
            continue
        lon = float(data.get("longitude", 0))
        deg_in_sign = lon % 30
        if deg_in_sign > max_deg:
            max_deg = deg_in_sign
            atmakaraka = planet.lower()
    return atmakaraka, max_deg


def get_karakamsha_lagna(
    natal_planets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate Karakamsha Lagna from Atmakaraka's D-9 position.

    Args:
        natal_planets: {planet: {longitude, rashi, house}}

    Returns:
        Karakamsha Lagna sign, lord, and Atmakaraka details
    """
    ak_planet, ak_degree = get_atmakaraka(natal_planets)
    ak_data = natal_planets.get(ak_planet, {})
    ak_lon = float(ak_data.get("longitude", 0))
    kl_sign = _get_navamsha_sign(ak_lon)
    kl_lord = SIGN_LORDS[kl_sign]

    return {
        "atmakaraka": ak_planet,
        "atmakaraka_degree_in_sign": round(ak_degree, 4),
        "atmakaraka_natal_sign": ak_data.get("rashi", SIGNS[int(ak_lon / 30) % 12]),
        "atmakaraka_navamsha_sign": kl_sign,
        "karakamsha_lagna": kl_sign,
        "karakamsha_lagna_lord": kl_lord,
    }


# BPHS Ch.35 house results from Karakamsha
_KL_HOUSE_RESULTS = {
    1: {
        "theme": "Soul nature, fundamental self, body of the soul",
        "sun": "Royal soul — seeks authority and recognition. Past life: ruler or administrator.",
        "moon": "Nurturing soul — seeks emotional fulfillment. Past life: caretaker or healer.",
        "mars": "Warrior soul — seeks conquest and action. Past life: soldier or athlete.",
        "mercury": "Intellectual soul — seeks knowledge and communication. Past life: scholar or merchant.",
        "jupiter": "Dharmic soul — seeks wisdom and teaching. Past life: guru or priest.",
        "venus": "Aesthetic soul — seeks beauty and love. Past life: artist or lover.",
        "saturn": "Karma-completing soul — seeks discipline and service. Past life: servant or ascetic.",
        "rahu": "Obsessive seeker — seeks foreign/unconventional experiences. Past life: foreigner or rebel.",
        "ketu": "Liberation-seeking soul — seeks moksha. Past life: ascetic or spiritual seeker.",
    },
    2: {
        "theme": "Speech, family values, wealth at soul level",
        "sun": "Authoritative speech. Wealth through government or authority.",
        "moon": "Nurturing speech. Wealth through public or maternal connections.",
        "mars": "Direct, forceful speech. Wealth through action and property.",
        "mercury": "Eloquent speech. Wealth through trade, intellect, writing.",
        "jupiter": "Wise, dharmic speech. Wealth through wisdom and teaching.",
        "venus": "Beautiful, pleasing speech. Wealth through arts and beauty.",
        "saturn": "Slow, deliberate speech. Wealth through discipline and hard work.",
        "rahu": "Unusual speech. Wealth through foreign or unconventional sources.",
        "ketu": "Detached speech. Wealth through spiritual or research work.",
    },
    3: {
        "theme": "Courage, siblings, communication at soul level",
        "sun": "Leadership courage. Commands siblings with authority.",
        "moon": "Emotional courage. Nurturing relationship with siblings.",
        "mars": "Physical courage. Competitive with siblings.",
        "mercury": "Intellectual courage. Communicates skillfully with siblings.",
        "jupiter": "Dharmic courage. Guides siblings with wisdom.",
        "venus": "Gentle courage. Harmonious sibling relationships.",
        "saturn": "Patient courage. Takes responsibility for siblings.",
        "rahu": "Unconventional courage. Foreign or unusual sibling dynamics.",
        "ketu": "Detached courage. Spiritual relationship with siblings.",
    },
    4: {
        "theme": "Mother, home, emotional foundation at soul level",
        "sun": "Authoritative mother. Home is royal or government-connected.",
        "moon": "Nurturing mother. Home is emotionally fulfilling.",
        "mars": "Energetic mother. Home involves action and property.",
        "mercury": "Intellectual mother. Home is educational or business-oriented.",
        "jupiter": "Wise mother. Home is dharmic and spiritually elevated.",
        "venus": "Beautiful mother. Home is artistic and luxurious.",
        "saturn": "Disciplined mother. Home involves service or limitation.",
        "rahu": "Foreign or unconventional mother. Home is unusual or abroad.",
        "ketu": "Detached mother. Home is spiritually oriented or ascetic.",
    },
    5: {
        "theme": "Poorvapunya — past life merit, children, intelligence",
        "sun": "High past life merit from serving authority. Intelligent, authoritative children.",
        "moon": "Past life merit from nurturing. Emotionally intelligent children.",
        "mars": "Past life merit from courage/sacrifice. Active, athletic children.",
        "mercury": "Past life merit from knowledge. Intelligent, communicative children.",
        "jupiter": "High past life dharmic merit. Wise, spiritually inclined children.",
        "venus": "Past life merit from beauty/arts. Beautiful, artistic children.",
        "saturn": "Past life merit from service/discipline. Few but disciplined children.",
        "rahu": "Unusual past life karma. Children with foreign or unconventional qualities.",
        "ketu": "Spiritual past life karma. Children with spiritual inclinations or few children.",
    },
    6: {
        "theme": "Enemies, disease, service at soul level",
        "sun": "Enemies are authorities or government. Diseases of ego or heart.",
        "moon": "Enemies are emotional manipulators. Diseases of mind or chest.",
        "mars": "Enemies are warriors or competitors. Diseases from heat or blood.",
        "mercury": "Enemies are intellectuals or merchants. Diseases of nervous system.",
        "jupiter": "Few enemies due to dharma. Diseases from overindulgence.",
        "venus": "Enemies through relationships. Diseases of reproductive system.",
        "saturn": "Enemies are workers or lower class. Chronic diseases.",
        "rahu": "Foreign enemies or poison. Unusual or hard-to-diagnose diseases.",
        "ketu": "Enemies dissolve through detachment. Diseases lead to spirituality.",
    },
    7: {
        "theme": "Soul-level partnership, marriage karaka at deepest level",
        "sun": "Spouse of royal/authoritative nature. Marriage involves ego themes.",
        "moon": "Spouse of nurturing/emotional nature. Emotionally deep marriage.",
        "mars": "Spouse of energetic/courageous nature. Passionate marriage.",
        "mercury": "Spouse of intellectual nature. Communication-based marriage.",
        "jupiter": "Spouse of wise/dharmic nature. Marriage through dharmic channels.",
        "venus": "Spouse of beautiful/artistic nature. Romantic, harmonious marriage.",
        "saturn": "Spouse of disciplined/older nature. Late or karmic marriage.",
        "rahu": "Spouse of foreign/unconventional nature. Unusual marriage circumstances.",
        "ketu": "Detached marriage or spiritually evolved spouse. Past life connection.",
    },
    8: {
        "theme": "Transformation, occult, longevity at soul level",
        "sun": "Transformation through authority loss/gain. Interest in political occult.",
        "moon": "Transformation through emotional crises. Psychic abilities.",
        "mars": "Transformation through conflicts. Interest in tantric practices.",
        "mercury": "Transformation through knowledge. Interest in occult sciences.",
        "jupiter": "Transformation through wisdom. Interest in vedic occult.",
        "venus": "Transformation through relationships. Interest in love magic.",
        "saturn": "Transformation through hardship. Interest in practical occult.",
        "rahu": "Transformation through foreign/unusual means. Powerful occult abilities.",
        "ketu": "Transformation through detachment. Natural moksha path.",
    },
    9: {
        "theme": "Dharma at soul level, relationship with the divine",
        "sun": "Dharma through authority and solar worship. Father as spiritual guide.",
        "moon": "Dharma through devotion and lunar worship. Mother as spiritual guide.",
        "mars": "Dharma through action and martial practices. Warrior's dharma.",
        "mercury": "Dharma through knowledge and study. Scholar's dharma.",
        "jupiter": "Highest dharmic soul — born to teach and spread wisdom.",
        "venus": "Dharma through beauty, arts, and devotional practices.",
        "saturn": "Dharma through service, austerity, and karmic completion.",
        "rahu": "Dharma through unconventional paths. Foreign or unusual spiritual practice.",
        "ketu": "Dharma through moksha path. Born to achieve liberation.",
    },
    10: {
        "theme": "Karma, profession, authority at soul level",
        "sun": "Born to hold authority. Professional karma with government.",
        "moon": "Born to serve the public. Professional karma with masses.",
        "mars": "Born to take action. Professional karma with military/police.",
        "mercury": "Born to communicate. Professional karma with education/trade.",
        "jupiter": "Born to guide. Professional karma with teaching/counseling.",
        "venus": "Born to create beauty. Professional karma with arts/luxury.",
        "saturn": "Born to serve and discipline. Professional karma with labor/industry.",
        "rahu": "Born for unconventional career. Foreign or unusual professional karma.",
        "ketu": "Born for spiritual profession. Professional karma with research/spirituality.",
    },
    11: {
        "theme": "Gains, aspirations, networks at soul level",
        "sun": "Gains through authority. Network of powerful people.",
        "moon": "Gains through public. Network of nurturing people.",
        "mars": "Gains through action. Network of competitive people.",
        "mercury": "Gains through intellect. Network of educated people.",
        "jupiter": "Gains through wisdom. Network of dharmic people.",
        "venus": "Gains through beauty. Network of artistic people.",
        "saturn": "Gains through service. Network of hardworking people.",
        "rahu": "Gains through foreign sources. Network of unusual people.",
        "ketu": "Detached from gains. Network dissolves or is spiritual.",
    },
    12: {
        "theme": "Moksha potential, spiritual liberation, foreign/hidden realms",
        "sun": "Liberation through surrender of ego. Potential for moksha through service to divine authority.",
        "moon": "Liberation through emotional surrender and devotion.",
        "mars": "Liberation through action and energy channeled to the divine.",
        "mercury": "Liberation through jnana yoga — knowledge and discrimination.",
        "jupiter": "Highest moksha potential — liberation through wisdom and dharma.",
        "venus": "Liberation through bhakti — love and devotion.",
        "saturn": "Liberation through karma yoga — selfless discipline and service.",
        "rahu": "Unusual moksha path — liberation through facing and transcending obsession.",
        "ketu": "Natural moksha karaka — liberation is the primary soul purpose.",
    },
}


def analyze_karakamsha(
    natal_planets: dict[str, dict[str, Any]],
    d9_planets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Complete Karakamsha Lagna analysis from BPHS Chapter 35.

    Args:
        natal_planets: D-1 birth chart planets
        d9_planets: D-9 navamsha chart planets (optional, computed if not provided)

    Returns:
        Full Karakamsha analysis with house-by-house soul-level interpretation
    """
    kl_data = get_karakamsha_lagna(natal_planets)
    kl_sign = kl_data["karakamsha_lagna"]
    kl_idx = SIGN_TO_INDEX[kl_sign.lower()]

    # Compute D-9 positions if not provided
    if d9_planets is None:
        d9_planets = {}
        for planet, data in natal_planets.items():
            lon = float(data.get("longitude", 0))
            d9_sign = _get_navamsha_sign(lon)
            d9_planets[planet] = {"rashi": d9_sign}

    # Analyze each key house from Karakamsha
    house_analyses = {}
    key_houses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    for house in key_houses:
        house_sign = SIGNS[(kl_idx + house - 1) % 12]
        planets_here = [
            p for p, d in d9_planets.items() if d.get("rashi", "").lower() == house_sign.lower()
        ]
        house_results = _KL_HOUSE_RESULTS.get(house, {})
        planet_interpretations = []
        for p in planets_here:
            interp = house_results.get(p.lower(), f"{p.title()} in house {house} from Karakamsha")
            planet_interpretations.append(
                {
                    "planet": p,
                    "interpretation": interp,
                }
            )

        house_analyses[house] = {
            "house": house,
            "sign": house_sign,
            "theme": house_results.get("theme", SIGN_LORDS.get(house_sign, "")),
            "planets": planets_here,
            "interpretations": planet_interpretations,
        }

    # Special focus: 1st, 5th, 9th, 12th from KL (most important for soul analysis)
    soul_summary = {
        "soul_nature": house_analyses[1],
        "past_life_merit": house_analyses[5],
        "dharma": house_analyses[9],
        "moksha_potential": house_analyses[12],
    }

    return {
        "success": True,
        "system": "Karakamsha Lagna — BPHS Chapter 35",
        "karakamsha_lagna": kl_sign,
        "karakamsha_lagna_lord": kl_data["karakamsha_lagna_lord"],
        "atmakaraka": kl_data["atmakaraka"],
        "atmakaraka_degree": kl_data["atmakaraka_degree_in_sign"],
        "atmakaraka_natal_sign": kl_data["atmakaraka_natal_sign"],
        "house_analyses": house_analyses,
        "soul_summary": soul_summary,
        "note": "Karakamsha shows soul-level karma — what the soul seeks and why it incarnated",
    }
