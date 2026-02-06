"""Gem Recommendation Engine for 108 Vedic Astrology.

Prescribes gemstones based on Lagna (ascendant), functional planet roles,
current Dasha, Shadbala strength, and contraindications.

Key Jyotish Rules:
- Gems STRENGTHEN a planet -- only wear gems for BENEFIC planets for your Lagna.
- NEVER wear gems for functional malefics (6th, 8th, 12th lords).
- Yoga Karaka planet's gem is ALWAYS beneficial.
- Dasha lord's gem amplifies current period (if the planet is benefic).
- Lagna lord's gem is universally beneficial.
- Enemy gems should not be worn together.
"""

from typing import Any

from packages.core.src.knowledge_loader import load_rules

# Planet to gemstone mapping (from remedies_rules.json and standard Jyotish)
PLANET_GEMS: dict[str, dict[str, Any]] = {
    "sun": {
        "primary": "ruby",
        "secondary": ["garnet", "red_spinel"],
        "finger": "ring",
        "metal": "gold",
        "day": "sunday",
        "min_carat": 3,
    },
    "moon": {
        "primary": "pearl",
        "secondary": ["moonstone"],
        "finger": "little",
        "metal": "silver",
        "day": "monday",
        "min_carat": 4,
    },
    "mars": {
        "primary": "red_coral",
        "secondary": ["carnelian"],
        "finger": "ring",
        "metal": "gold/copper",
        "day": "tuesday",
        "min_carat": 5,
    },
    "mercury": {
        "primary": "emerald",
        "secondary": ["peridot", "green_tourmaline"],
        "finger": "little",
        "metal": "gold",
        "day": "wednesday",
        "min_carat": 3,
    },
    "jupiter": {
        "primary": "yellow_sapphire",
        "secondary": ["citrine", "yellow_topaz"],
        "finger": "index",
        "metal": "gold",
        "day": "thursday",
        "min_carat": 4,
    },
    "venus": {
        "primary": "diamond",
        "secondary": ["white_sapphire", "zircon"],
        "finger": "little",
        "metal": "platinum/gold",
        "day": "friday",
        "min_carat": 1,
    },
    "saturn": {
        "primary": "blue_sapphire",
        "secondary": ["amethyst", "iolite"],
        "finger": "middle",
        "metal": "gold/iron",
        "day": "saturday",
        "min_carat": 4,
    },
    "rahu": {
        "primary": "hessonite",
        "secondary": ["orange_zircon"],
        "finger": "middle",
        "metal": "silver",
        "day": "saturday",
        "min_carat": 5,
    },
    "ketu": {
        "primary": "cats_eye",
        "secondary": ["chrysoberyl"],
        "finger": "little",
        "metal": "gold",
        "day": "tuesday",
        "min_carat": 5,
    },
}

# Enemy gem pairs -- these should NOT be worn together
ENEMY_GEM_PAIRS: list[tuple[str, str]] = [
    ("ruby", "blue_sapphire"),
    ("ruby", "hessonite"),
    ("pearl", "hessonite"),
    ("red_coral", "emerald"),
    ("red_coral", "diamond"),
    ("yellow_sapphire", "diamond"),
    ("yellow_sapphire", "emerald"),
]

# Sign lordships for determining functional benefics/malefics
SIGN_LORDS: dict[str, str] = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

# Houses ruled by each sign from each Lagna (1-indexed)
# For Lagna X, sign Y rules house = ((sign_index - lagna_index) % 12) + 1
SIGN_INDEX: dict[str, int] = {
    "aries": 0,
    "taurus": 1,
    "gemini": 2,
    "cancer": 3,
    "leo": 4,
    "virgo": 5,
    "libra": 6,
    "scorpio": 7,
    "sagittarius": 8,
    "capricorn": 9,
    "aquarius": 10,
    "pisces": 11,
}

# Lagna-wise functional classifications (comprehensive Jyotish rules)
# yoga_karaka: planet that owns both a kendra and a trikona
# primary_benefic: best planets for the Lagna
# functional_malefic: 6/8/12 lords
LAGNA_CLASSIFICATIONS: dict[str, dict[str, Any]] = {
    "aries": {
        "yoga_karaka": None,
        "primary_benefic": ["sun", "jupiter", "mars"],
        "secondary_benefic": [],
        "functional_malefic": ["mercury", "saturn"],
        "neutral": ["moon", "venus"],
        "maraka": ["venus", "mercury"],  # 2nd (venus=taurus) and 7th (venus=libra) lords
    },
    "taurus": {
        "yoga_karaka": "saturn",  # 9th+10th
        "primary_benefic": ["saturn", "mercury", "venus"],
        "secondary_benefic": ["sun"],
        "functional_malefic": ["jupiter", "mars"],
        "neutral": ["moon"],
        "maraka": ["mercury", "mars"],
    },
    "gemini": {
        "yoga_karaka": None,
        "primary_benefic": ["venus", "mercury"],
        "secondary_benefic": [],
        "functional_malefic": ["mars", "jupiter"],
        "neutral": ["sun", "moon", "saturn"],
        "maraka": ["moon", "jupiter"],
    },
    "cancer": {
        "yoga_karaka": "mars",  # 5th+10th
        "primary_benefic": ["mars", "jupiter", "moon"],
        "secondary_benefic": [],
        "functional_malefic": ["saturn", "venus", "mercury"],
        "neutral": ["sun"],
        "maraka": ["sun", "saturn"],
    },
    "leo": {
        "yoga_karaka": "mars",  # 4th+9th
        "primary_benefic": ["mars", "sun", "jupiter"],
        "secondary_benefic": [],
        "functional_malefic": ["saturn", "venus"],
        "neutral": ["moon", "mercury"],
        "maraka": ["mercury", "saturn"],
    },
    "virgo": {
        "yoga_karaka": None,
        "primary_benefic": ["venus", "mercury"],
        "secondary_benefic": [],
        "functional_malefic": ["mars", "moon", "jupiter"],
        "neutral": ["sun", "saturn"],
        "maraka": ["venus", "mars"],
    },
    "libra": {
        "yoga_karaka": "saturn",  # 4th+5th
        "primary_benefic": ["saturn", "venus", "mercury"],
        "secondary_benefic": [],
        "functional_malefic": ["jupiter", "sun"],
        "neutral": ["moon"],
        "maraka": ["mars", "jupiter"],
    },
    "scorpio": {
        "yoga_karaka": None,
        "primary_benefic": ["jupiter", "moon", "sun"],
        "secondary_benefic": ["mars"],
        "functional_malefic": ["mercury", "venus"],
        "neutral": ["saturn"],
        "maraka": ["jupiter", "venus"],
    },
    "sagittarius": {
        "yoga_karaka": None,
        "primary_benefic": ["sun", "mars", "jupiter"],
        "secondary_benefic": [],
        "functional_malefic": ["venus", "saturn"],
        "neutral": ["moon", "mercury"],
        "maraka": ["saturn", "mercury"],
    },
    "capricorn": {
        "yoga_karaka": "venus",  # 5th+10th
        "primary_benefic": ["venus", "saturn", "mercury"],
        "secondary_benefic": [],
        "functional_malefic": ["mars", "jupiter"],
        "neutral": ["sun", "moon"],
        "maraka": ["saturn", "moon"],
    },
    "aquarius": {
        "yoga_karaka": "venus",  # 4th+9th
        "primary_benefic": ["venus", "saturn"],
        "secondary_benefic": ["mars"],
        "functional_malefic": ["jupiter", "moon"],
        "neutral": ["sun", "mercury"],
        "maraka": ["jupiter", "sun"],
    },
    "pisces": {
        "yoga_karaka": None,
        "primary_benefic": ["moon", "mars", "jupiter"],
        "secondary_benefic": [],
        "functional_malefic": ["saturn", "sun", "venus", "mercury"],
        "neutral": [],
        "maraka": ["mars", "saturn"],
    },
}

# Caution notes for specific planet gems
CAUTION_NOTES: dict[str, str] = {
    "saturn": "Try for 3 days first before committing (Saturn gems can be intense)",
    "rahu": "Try for 3 days first (Rahu gems need compatibility testing)",
    "ketu": "Try for 3 days first (Ketu gems need compatibility testing)",
    "mars": "Ensure Mars is not heavily afflicted before wearing",
}

# Natural malefics -- need extra consideration
NATURAL_MALEFICS = {"sun", "mars", "saturn", "rahu", "ketu"}


def _load_gem_prescription_rules() -> dict[str, Any]:
    """Load gem prescription rules from knowledge base.

    Returns empty dict if the file doesn't exist yet.
    """
    data = load_rules("gem_prescription_rules")
    return data.get("gem_prescription_rules", {})


def _get_planet_role(planet: str, lagna_rashi: str) -> str:
    """Determine a planet's functional role for a given Lagna.

    Args:
        planet: Planet name (lowercase).
        lagna_rashi: Ascendant sign (lowercase).

    Returns:
        One of: 'yoga_karaka', 'primary_benefic', 'secondary_benefic',
        'functional_malefic', 'maraka', 'neutral'.
    """
    lagna = lagna_rashi.lower()
    classification = LAGNA_CLASSIFICATIONS.get(lagna, {})

    if classification.get("yoga_karaka") == planet:
        return "yoga_karaka"
    if planet in classification.get("primary_benefic", []):
        return "primary_benefic"
    if planet in classification.get("secondary_benefic", []):
        return "secondary_benefic"
    if planet in classification.get("functional_malefic", []):
        return "functional_malefic"
    if planet in classification.get("maraka", []):
        return "maraka"
    return "neutral"


def _get_gem_info(planet: str) -> dict[str, Any]:
    """Get gemstone info for a planet, merging knowledge data with defaults.

    Args:
        planet: Planet name (lowercase).

    Returns:
        Gem info dict with primary, secondary, finger, metal, day, min_carat.
    """
    default = PLANET_GEMS.get(planet, {})
    if not default:
        return {}

    # Try loading from remedies_rules.json
    try:
        remedies_data = load_rules("remedies_rules").get("remedies", {})
        gemstone_data = remedies_data.get("gemstones", {}).get(planet, {})
        if gemstone_data:
            return {
                "primary": gemstone_data.get("primary", default["primary"]),
                "secondary": gemstone_data.get("secondary", default.get("secondary", [])),
                "finger": gemstone_data.get("finger", default["finger"]),
                "metal": gemstone_data.get("metal", default["metal"]),
                "day": gemstone_data.get("day", default["day"]),
                "min_carat": gemstone_data.get("minimum_carat", default.get("min_carat", 3)),
            }
    except Exception:
        pass

    return dict(default)


def _build_gem_entry(planet: str, reason: str, caution: str = "") -> dict[str, Any]:
    """Build a complete gem recommendation entry.

    Args:
        planet: Planet name (lowercase).
        reason: Why this gem is recommended.
        caution: Optional caution note.

    Returns:
        Gem entry dict.
    """
    info = _get_gem_info(planet)
    if not info:
        return {
            "planet": planet,
            "gem": "unknown",
            "reason": reason,
        }

    entry: dict[str, Any] = {
        "planet": planet,
        "gem": info["primary"],
        "secondary_gems": info.get("secondary", []),
        "reason": reason,
        "finger": info.get("finger", ""),
        "metal": info.get("metal", ""),
        "minimum_carat": info.get("min_carat", 3),
        "wearing_day": info.get("day", ""),
    }

    if caution or planet in CAUTION_NOTES:
        entry["caution"] = caution or CAUTION_NOTES.get(planet, "")

    return entry


def _check_enemy_gems(gem_list: list[str]) -> list[tuple[str, str]]:
    """Check if any gems in the list are enemies of each other.

    Args:
        gem_list: List of gem names to check.

    Returns:
        List of conflicting gem pairs.
    """
    conflicts: list[tuple[str, str]] = []
    for g1, g2 in ENEMY_GEM_PAIRS:
        if g1 in gem_list and g2 in gem_list:
            conflicts.append((g1, g2))
    return conflicts


def get_lagna_gem_map(lagna_rashi: str) -> dict[str, Any]:
    """Get beneficial/neutral/harmful gem classification for a specific Lagna.

    Args:
        lagna_rashi: Ascendant sign name (lowercase).

    Returns:
        Dict with benefic_gems, neutral_gems, harmful_gems lists plus the
        yoga_karaka gem if applicable.
    """
    lagna = lagna_rashi.lower()
    classification = LAGNA_CLASSIFICATIONS.get(lagna)
    if not classification:
        return {
            "lagna": lagna,
            "error": f"Unknown Lagna: {lagna}",
            "benefic_gems": [],
            "neutral_gems": [],
            "harmful_gems": [],
        }

    benefic_gems: list[dict[str, Any]] = []
    neutral_gems: list[dict[str, Any]] = []
    harmful_gems: list[dict[str, Any]] = []

    yk = classification.get("yoga_karaka")
    all_planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

    for planet in all_planets:
        role = _get_planet_role(planet, lagna)
        gem_info = _get_gem_info(planet)
        if not gem_info:
            continue

        gem_entry = {
            "planet": planet,
            "gem": gem_info["primary"],
            "role": role,
        }

        if role in ("yoga_karaka", "primary_benefic", "secondary_benefic"):
            benefic_gems.append(gem_entry)
        elif role in ("functional_malefic", "maraka"):
            harmful_gems.append(gem_entry)
        else:
            neutral_gems.append(gem_entry)

    result: dict[str, Any] = {
        "lagna": lagna,
        "benefic_gems": benefic_gems,
        "neutral_gems": neutral_gems,
        "harmful_gems": harmful_gems,
    }

    if yk:
        yk_info = _get_gem_info(yk)
        result["yoga_karaka_gem"] = {
            "planet": yk,
            "gem": yk_info.get("primary", "unknown"),
            "role": "yoga_karaka",
        }

    return result


def check_gem_compatibility(
    gem_planet: str,
    lagna_rashi: str,
    planets: dict[str, Any],
) -> dict[str, Any]:
    """Check if a specific gem is safe to wear for this chart.

    Args:
        gem_planet: Planet whose gem the user wants to check (lowercase).
        lagna_rashi: Ascendant sign (lowercase).
        planets: Birth chart planets with positions and house data.

    Returns:
        Dict with safe (bool), role, warnings, and recommendation.
    """
    planet = gem_planet.lower()
    lagna = lagna_rashi.lower()

    role = _get_planet_role(planet, lagna)
    gem_info = _get_gem_info(planet)

    warnings: list[str] = []
    safe = True

    # Check functional role
    if role == "functional_malefic":
        safe = False
        warnings.append(
            f"{planet.title()} is a functional malefic for {lagna.title()} Lagna -- "
            "wearing its gem may increase problems"
        )
    elif role == "maraka":
        safe = False
        warnings.append(
            f"{planet.title()} is a Maraka (death-inflicting) planet for {lagna.title()} Lagna -- "
            "gem may intensify health risks"
        )

    # Check if planet is debilitated in birth chart
    debilitation_signs = {
        "sun": "libra",
        "moon": "scorpio",
        "mars": "cancer",
        "mercury": "pisces",
        "jupiter": "capricorn",
        "venus": "virgo",
        "saturn": "aries",
    }
    if planet in planets:
        p_data = planets[planet]
        p_sign = (
            p_data.get("rashi", "").lower()
            if isinstance(p_data, dict)
            else getattr(p_data, "rashi", "").lower()
            if hasattr(p_data, "rashi")
            else ""
        )
        if p_sign and p_sign == debilitation_signs.get(planet, ""):
            if role in ("yoga_karaka", "primary_benefic"):
                warnings.append(
                    f"{planet.title()} is debilitated -- gem is especially recommended to strengthen it"
                )
            else:
                warnings.append(
                    f"{planet.title()} is debilitated -- wearing gem for a weak malefic is risky"
                )
                if role not in ("neutral",):
                    safe = False

    # Natural malefic caution
    if planet in NATURAL_MALEFICS and role == "neutral":
        warnings.append(
            f"{planet.title()} is a natural malefic -- wear with caution even if neutral functionally"
        )

    recommendation = (
        "Recommended"
        if safe and role in ("yoga_karaka", "primary_benefic", "secondary_benefic")
        else ("Safe with caution" if safe else "Not recommended")
    )

    return {
        "planet": planet,
        "gem": gem_info.get("primary", "unknown"),
        "role": role,
        "safe": safe,
        "warnings": warnings,
        "recommendation": recommendation,
    }


def recommend_gems(
    lagna_rashi: str,
    planets: dict[str, Any],  # noqa: ARG001
    shadbala: dict[str, Any] | None = None,
    current_dasha: dict[str, Any] | None = None,
    active_doshas: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Full gem prescription based on chart analysis.

    Args:
        lagna_rashi: Ascendant sign name (lowercase).
        planets: Birth chart planet data (dict keyed by planet name).
        shadbala: Optional Shadbala strength scores per planet.
        current_dasha: Optional current dasha info with 'mahadasha_lord',
            'antardasha_lord', 'pratyantardasha_lord' keys.
        active_doshas: Optional list of active doshas, each with 'name' key.

    Returns:
        Complete gem recommendation with primary_gem, secondary_gems,
        dasha_gem, contraindicated, enemy_conflicts, and general_advice.
    """
    lagna = lagna_rashi.lower()
    classification = LAGNA_CLASSIFICATIONS.get(lagna)
    if not classification:
        return {
            "error": f"Unknown Lagna: {lagna}",
            "primary_gem": None,
            "secondary_gems": [],
            "contraindicated": [],
        }

    yk = classification.get("yoga_karaka")
    primary_benefics = classification.get("primary_benefic", [])
    malefics = classification.get("functional_malefic", [])
    marakas = classification.get("maraka", [])

    # Lagna lord
    lagna_lord = SIGN_LORDS.get(lagna, "")

    # --- Primary gem (Yoga Karaka > Lagna Lord > strongest benefic) ---
    primary_gem = None
    if yk:
        reason = _yoga_karaka_reason(yk, lagna)
        primary_gem = _build_gem_entry(yk, reason)
    elif lagna_lord and lagna_lord in primary_benefics:
        reason = f"Lagna lord ({lagna_lord.title()}) for {lagna.title()} Lagna -- strengthens self and health"
        primary_gem = _build_gem_entry(lagna_lord, reason)
    elif primary_benefics:
        first_benefic = primary_benefics[0]
        reason = f"Primary benefic ({first_benefic.title()}) for {lagna.title()} Lagna"
        primary_gem = _build_gem_entry(first_benefic, reason)

    # --- Secondary gems (other benefics, possibly weak planets) ---
    secondary_gems: list[dict[str, Any]] = []
    recommended_planets: set[str] = set()
    if primary_gem:
        recommended_planets.add(primary_gem["planet"])

    for planet in primary_benefics:
        if planet in recommended_planets:
            continue
        role = _get_planet_role(planet, lagna)
        reason = f"{role.replace('_', ' ').title()} for {lagna.title()} Lagna"
        # Boost reason if planet is weak in Shadbala
        if shadbala and planet in shadbala:
            sb = shadbala[planet]
            strength = sb.get("total", sb) if isinstance(sb, dict) else sb
            if isinstance(strength, int | float) and strength < 1.0:
                reason += f" (weak Shadbala: {strength:.2f} -- gem especially recommended)"
        secondary_gems.append(_build_gem_entry(planet, reason))
        recommended_planets.add(planet)

    # --- Dasha gem ---
    dasha_gem = None
    if current_dasha:
        md_lord = current_dasha.get("mahadasha_lord", "").lower()
        if md_lord and md_lord not in malefics and md_lord not in marakas:
            reason = f"Current Mahadasha lord ({md_lord.title()}) -- amplifies the current period"
            dasha_gem = _build_gem_entry(md_lord, reason)

    # --- Contraindicated gems ---
    contraindicated: list[dict[str, Any]] = []
    for planet in malefics + marakas:
        gem_info = _get_gem_info(planet)
        if gem_info:
            role = _get_planet_role(planet, lagna)
            if role == "maraka":
                reason = f"{planet.title()} is a Maraka for {lagna.title()} Lagna -- gem may intensify health risks"
            else:
                reason = f"{planet.title()} is a functional malefic for {lagna.title()} Lagna -- gem would strengthen problems"
            contraindicated.append(
                {
                    "planet": planet,
                    "gem": gem_info["primary"],
                    "reason": reason,
                }
            )

    # --- Enemy gem conflicts ---
    all_recommended_gems: list[str] = []
    if primary_gem:
        all_recommended_gems.append(primary_gem["gem"])
    for sg in secondary_gems:
        all_recommended_gems.append(sg["gem"])
    if dasha_gem:
        all_recommended_gems.append(dasha_gem["gem"])

    conflicts = _check_enemy_gems(all_recommended_gems)
    enemy_warnings: list[str] = []
    for g1, g2 in conflicts:
        enemy_warnings.append(f"{g1} and {g2} should not be worn together")

    # --- General advice ---
    advice_parts: list[str] = []
    if yk:
        yk_info = _get_gem_info(yk)
        advice_parts.append(
            f"For {lagna.title()} Lagna, {yk.title()} ({yk_info.get('primary', '').replace('_', ' ').title()}) "
            f"is the Yoga Karaka gem -- always the #1 choice."
        )
    if lagna_lord:
        ll_info = _get_gem_info(lagna_lord)
        advice_parts.append(
            f"Lagna lord {lagna_lord.title()}'s gem ({ll_info.get('primary', '').replace('_', ' ').title()}) "
            f"is universally beneficial for health and vitality."
        )
    if active_doshas:
        dosha_names = [d.get("name", "unknown") for d in active_doshas]
        advice_parts.append(
            f"Active doshas ({', '.join(dosha_names)}) -- consider corresponding planet remedies alongside gems."
        )

    return {
        "lagna": lagna,
        "primary_gem": primary_gem,
        "secondary_gems": secondary_gems,
        "dasha_gem": dasha_gem,
        "contraindicated": contraindicated,
        "enemy_conflicts": enemy_warnings,
        "general_advice": " ".join(advice_parts)
        if advice_parts
        else f"Consult with a Jyotish practitioner for {lagna.title()} Lagna gem guidance.",
    }


def _yoga_karaka_reason(planet: str, lagna: str) -> str:
    """Generate reason string for Yoga Karaka planet.

    Args:
        planet: Planet name.
        lagna: Lagna name.

    Returns:
        Descriptive reason string.
    """
    yk_descriptions: dict[str, dict[str, str]] = {
        "taurus": {"saturn": "9th+10th lord (fortune + career)"},
        "cancer": {"mars": "5th+10th lord (intelligence + career)"},
        "leo": {"mars": "4th+9th lord (happiness + fortune)"},
        "libra": {"saturn": "4th+5th lord (happiness + intelligence)"},
        "capricorn": {"venus": "5th+10th lord (intelligence + career)"},
        "aquarius": {"venus": "4th+9th lord (happiness + fortune)"},
    }

    desc = yk_descriptions.get(lagna, {}).get(planet, "kendra + trikona lord")
    return f"Yoga Karaka for {lagna.title()} Lagna -- {desc}"
