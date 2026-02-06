"""Remedies recommendation engine for 108 Vedic Astrology.

Recommends remedies based on chart conditions using knowledge/rules/remedies_rules.json.
Prioritizes remedies into urgent, recommended, and optional categories based on
current dasha, active doshas, weak planets, and transits.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_remedies

_remedies_cache: dict[str, Any] | None = None

# Planets considered for remedies
PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

# Dosha severity mapping
_DOSHA_SEVERITY: dict[str, str] = {
    "mangal_dosha": "high",
    "kaal_sarp_dosha": "high",
    "pitra_dosha": "high",
    "sade_sati": "high",
    "ashtama_shani": "high",
    "grahan_dosha": "medium",
    "guru_chandal_dosha": "medium",
    "kemdrum_dosha": "medium",
    "shrapit_dosha": "medium",
    "daridra_dosha": "medium",
    "angarak_dosha": "medium",
}

# Planets associated with each dosha
_DOSHA_PLANETS: dict[str, list[str]] = {
    "mangal_dosha": ["mars"],
    "kaal_sarp_dosha": ["rahu", "ketu"],
    "pitra_dosha": ["sun", "saturn", "rahu"],
    "sade_sati": ["saturn"],
    "ashtama_shani": ["saturn"],
    "grahan_dosha": ["rahu", "ketu"],
    "guru_chandal_dosha": ["jupiter", "rahu"],
    "kemdrum_dosha": ["moon"],
    "shrapit_dosha": ["saturn", "rahu"],
    "daridra_dosha": ["jupiter"],
    "angarak_dosha": ["mars", "rahu"],
}


def _get_remedies_data() -> dict[str, Any]:
    """Get cached remedies data."""
    global _remedies_cache
    if _remedies_cache is None:
        _remedies_cache = get_remedies()
    return _remedies_cache


def get_planet_remedies(planet: str) -> dict[str, Any]:
    """Get all remedies for a specific planet from rules file.

    Args:
        planet: Planet name (lowercase)

    Returns:
        Dictionary with gemstone, mantra, charity, fasting, worship, yantra,
        rudraksha, and general remedies for the planet.
    """
    p = planet.lower()
    if p not in PLANETS:
        return {"planet": p, "found": False, "remedies": {}}

    data = _get_remedies_data()

    result: dict[str, Any] = {"planet": p, "found": True, "remedies": {}}

    # Gemstone
    gemstone = data.get("gemstones", {}).get(p)
    if gemstone:
        result["remedies"]["gemstone"] = gemstone

    # Mantra
    mantra = data.get("mantras", {}).get(p)
    if mantra:
        result["remedies"]["mantra"] = mantra

    # Charity
    charity = data.get("charities", {}).get(p)
    if charity:
        result["remedies"]["charity"] = charity

    # Fasting
    fasting = data.get("fasting_days", {}).get(p)
    if fasting:
        result["remedies"]["fasting"] = fasting

    # Worship deity
    worship = data.get("worship_deities", {}).get(p)
    if worship:
        result["remedies"]["worship"] = worship

    # Yantra
    yantra = data.get("yantras", {}).get(p)
    if yantra:
        result["remedies"]["yantra"] = yantra

    # Rudraksha
    rudraksha = data.get("rudraksha", {}).get(p)
    if rudraksha:
        result["remedies"]["rudraksha"] = rudraksha

    # General remedies
    general = data.get("general_remedies", {})
    gen_remedies: dict[str, Any] = {}
    for category in [
        "yoga_asanas",
        "color_therapy",
        "aromatherapy",
        "mudras",
        "breathing_exercises",
        "dietary_remedies",
    ]:
        cat_data = general.get(category, {}).get(p)
        if cat_data:
            gen_remedies[category] = cat_data
    if gen_remedies:
        result["remedies"]["general"] = gen_remedies

    return result


def prioritize_remedies(
    all_remedies: list[dict[str, Any]],
    current_conditions: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Sort remedies into urgent/recommended/optional based on conditions.

    Args:
        all_remedies: List of remedy dicts, each with "planet", "reason", and remedy data
        current_conditions: Dict with keys like "active_doshas", "dasha_lords",
                          "weak_planets", "transit_afflictions"

    Returns:
        Dictionary with "urgent", "recommended", "optional" lists of remedies.
    """
    urgent: list[dict[str, Any]] = []
    recommended: list[dict[str, Any]] = []
    optional: list[dict[str, Any]] = []

    dasha_lords = set(current_conditions.get("dasha_lords", []))
    dosha_planets = set(current_conditions.get("dosha_planets", []))
    weak_planet_names = set(current_conditions.get("weak_planets", []))
    transit_afflicted = set(current_conditions.get("transit_afflictions", []))

    for remedy in all_remedies:
        planet = remedy.get("planet", "")

        # Urgent: planet is both in active dasha AND has a dosha or is very weak
        if (planet in dasha_lords and (planet in dosha_planets or planet in weak_planet_names)) or (
            planet in dosha_planets and remedy.get("severity") == "high"
        ):
            urgent.append(remedy)
        # Recommended: planet is in active dasha period
        elif (
            planet in dasha_lords
            or planet in weak_planet_names
            or planet in transit_afflicted
            or planet in dosha_planets
        ):
            recommended.append(remedy)
        # Optional: everything else
        else:
            optional.append(remedy)

    return {
        "urgent": urgent,
        "recommended": recommended,
        "optional": optional,
    }


def recommend_remedies(
    current_dasha: dict[str, Any],
    active_doshas: list[dict[str, Any]],
    weak_planets: list[dict[str, Any]],
    current_transits: dict[str, Any] | None = None,
    lagna_rashi: str = "",
) -> dict[str, Any]:
    """Returns prioritized remedy recommendations based on chart conditions.

    Args:
        current_dasha: Active MD/AD/PD with keys like "mahadasha_lord", "antardasha_lord",
                      "pratyantardasha_lord"
        active_doshas: List of detected doshas, each with "name" and optional "severity"
        weak_planets: List of weak planets, each with "planet" and optional "shadbala"
        current_transits: Optional transit data for transit-based remedies
        lagna_rashi: Ascendant sign name (lowercase)

    Returns:
        Dictionary with "urgent", "recommended", "optional" remedy lists,
        plus "summary" with counts and "planets_needing_remedies".
    """
    # Collect dasha lords
    dasha_lords: list[str] = []
    for key in ["mahadasha_lord", "antardasha_lord", "pratyantardasha_lord"]:
        lord = current_dasha.get(key, "")
        if lord and lord.lower() in PLANETS:
            dasha_lords.append(lord.lower())

    # Collect dosha-related planets and their severity
    dosha_planets: set[str] = set()
    dosha_severity_map: dict[str, str] = {}
    for dosha in active_doshas:
        dosha_name = dosha.get("name", "").lower().replace(" ", "_")
        severity = dosha.get("severity", _DOSHA_SEVERITY.get(dosha_name, "low"))
        associated = _DOSHA_PLANETS.get(dosha_name, [])
        for p in associated:
            dosha_planets.add(p)
            # Keep highest severity
            current = dosha_severity_map.get(p, "low")
            if _severity_rank(severity) > _severity_rank(current):
                dosha_severity_map[p] = severity

    # Collect weak planet names
    weak_planet_names: set[str] = set()
    for wp in weak_planets:
        p = wp.get("planet", "").lower()
        if p in PLANETS:
            weak_planet_names.add(p)

    # Collect transit afflictions
    transit_afflicted: set[str] = set()
    if current_transits:
        for p, tdata in current_transits.items():
            if isinstance(tdata, dict) and tdata.get("afflicted", False):
                transit_afflicted.add(p.lower())

    # Build unique set of planets needing remedies
    planets_needing_remedies = (
        set(dasha_lords) | dosha_planets | weak_planet_names | transit_afflicted
    )

    # Generate remedy entries
    all_remedies: list[dict[str, Any]] = []
    for planet in planets_needing_remedies:
        planet_data = get_planet_remedies(planet)
        if not planet_data.get("found"):
            continue

        # Build reason string
        reasons: list[str] = []
        if planet in dasha_lords:
            reasons.append(f"Active dasha lord ({planet.title()})")
        if planet in dosha_planets:
            reasons.append("Dosha-afflicted planet")
        if planet in weak_planet_names:
            reasons.append("Weak planet (low Shadbala)")
        if planet in transit_afflicted:
            reasons.append("Transit-afflicted")

        severity = dosha_severity_map.get(planet, "low")

        # Build simplified remedy entry
        remedies = planet_data.get("remedies", {})
        entry: dict[str, Any] = {
            "planet": planet,
            "reason": "; ".join(reasons),
            "severity": severity,
        }

        # Add mantra (always recommended)
        mantra = remedies.get("mantra", {})
        if mantra:
            entry["remedy_type"] = "mantra"
            entry["remedy"] = mantra.get("beej_mantra", "")
            entry[
                "frequency"
            ] = f"{mantra.get('repetitions', {}).get('minimum', 108)} times on {mantra.get('best_time', 'appropriate day')}"

        # Add gemstone info
        gemstone = remedies.get("gemstone", {})
        if gemstone:
            entry["gemstone"] = {
                "primary": gemstone.get("primary", ""),
                "finger": gemstone.get("finger", ""),
                "metal": gemstone.get("metal", ""),
                "day": gemstone.get("day", ""),
            }

        # Add charity info
        charity = remedies.get("charity", {})
        if charity:
            entry["charity"] = {
                "items": charity.get("items", []),
                "day": charity.get("day", ""),
            }

        # Add worship info
        worship = remedies.get("worship", {})
        if worship:
            entry["worship"] = {
                "deity": worship.get("primary", ""),
                "temple": worship.get("temple", ""),
            }

        all_remedies.append(entry)

    # Prioritize
    conditions = {
        "dasha_lords": dasha_lords,
        "dosha_planets": list(dosha_planets),
        "weak_planets": list(weak_planet_names),
        "transit_afflictions": list(transit_afflicted),
    }
    prioritized = prioritize_remedies(all_remedies, conditions)

    return {
        "urgent": prioritized["urgent"],
        "recommended": prioritized["recommended"],
        "optional": prioritized["optional"],
        "summary": {
            "total_remedies": len(all_remedies),
            "urgent_count": len(prioritized["urgent"]),
            "recommended_count": len(prioritized["recommended"]),
            "optional_count": len(prioritized["optional"]),
        },
        "planets_needing_remedies": sorted(planets_needing_remedies),
        "lagna_rashi": lagna_rashi,
    }


def _severity_rank(severity: str) -> int:
    """Convert severity string to numeric rank for comparison."""
    return {"high": 3, "medium": 2, "low": 1}.get(severity.lower(), 0)
