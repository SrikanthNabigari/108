"""Knowledge base loader for 108 Vedic Astrology.

Provides centralized loading and caching of JSON knowledge files.
All packages should use this module to access knowledge data.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Knowledge base root directory
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"
DEFINITIONS_DIR = KNOWLEDGE_DIR / "definitions"
RULES_DIR = KNOWLEDGE_DIR / "rules"
INTERPRETATIONS_DIR = KNOWLEDGE_DIR / "interpretations"


@lru_cache(maxsize=32)
def _load_json_file(filepath: str) -> dict[str, Any]:
    """Load and cache a JSON file.

    Args:
        filepath: Path to the JSON file (as string for lru_cache)

    Returns:
        Parsed JSON content as dictionary
    """
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Knowledge file not found: {filepath}")
        return {}

    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Error loading knowledge file {filepath}: {e}")
        return {}


def load_definition(name: str) -> dict[str, Any]:
    """Load a definition file from knowledge/definitions/.

    Args:
        name: Definition name (without .json extension)
              e.g., "planets", "rashis", "nakshatras", "houses", "dignities"

    Returns:
        Definition data dictionary
    """
    filepath = DEFINITIONS_DIR / f"{name}.json"
    return _load_json_file(str(filepath))


def load_rules(name: str) -> dict[str, Any]:
    """Load a rules file from knowledge/rules/.

    Args:
        name: Rules name (without .json extension)
              e.g., "shadbala_rules", "yoga_master", "dosha_master",
                    "dasha_rules", "transit_rules", "muhurta_rules"

    Returns:
        Rules data dictionary
    """
    filepath = RULES_DIR / f"{name}.json"
    return _load_json_file(str(filepath))


# =============================================================================
# Convenience accessors for commonly used knowledge
# =============================================================================


def get_shadbala_rules() -> dict[str, Any]:
    """Get Shadbala calculation rules."""
    return load_rules("shadbala_rules").get("shadbala_rules", {})


def get_ashtakavarga_rules() -> dict[str, Any]:
    """Get Ashtakavarga calculation rules."""
    return load_rules("ashtakavarga_rules").get("ashtakavarga_rules", {})


def get_yoga_rules() -> dict[str, Any]:
    """Get yoga detection rules (522 yogas)."""
    return load_rules("yoga_master").get("yoga_rules", {})


def get_dosha_rules() -> dict[str, Any]:
    """Get dosha detection rules (55 doshas)."""
    return load_rules("dosha_master").get("dosha_rules", {})


def get_dasha_rules() -> dict[str, Any]:
    """Get dasha calculation rules."""
    return load_rules("dasha_rules").get("dasha_rules", {})


def get_transit_rules() -> dict[str, Any]:
    """Get transit/gochara rules."""
    return load_rules("transit_rules").get("transit_rules", {})


def get_muhurta_rules() -> dict[str, Any]:
    """Get muhurta (electional) rules."""
    return load_rules("muhurta_rules").get("muhurta_rules", {})


def get_compatibility_rules() -> dict[str, Any]:
    """Get compatibility/matching rules (no wrapper key in JSON)."""
    return load_rules("compatibility_rules")


def get_remedies() -> dict[str, Any]:
    """Get remedies data."""
    return load_rules("remedies_rules").get("remedies", {})


def get_planets() -> dict[str, Any]:
    """Get planet definitions."""
    return load_definition("planets").get("planets", {})


def get_rashis() -> dict[str, Any]:
    """Get rashi (zodiac sign) definitions."""
    return load_definition("rashis").get("rashis", {})


def get_nakshatras() -> list[dict[str, Any]]:
    """Get nakshatra definitions."""
    return load_definition("nakshatras").get("nakshatras", [])


def get_houses() -> dict[str, Any]:
    """Get house definitions."""
    return load_definition("houses").get("houses", {})


def get_dignities() -> dict[str, Any]:
    """Get planetary dignity definitions."""
    return load_definition("dignities").get("dignities", {})


def get_relationships() -> dict[str, Any]:
    """Get planetary relationship definitions."""
    return load_definition("relationships").get("relationships", {})


def get_aspects() -> dict[str, Any]:
    """Get aspect/drishti definitions."""
    return load_definition("aspects").get("aspects", {})


def get_antardasha_effects() -> dict[str, Any]:
    """Get Antardasha effects (81 combinations: 9x9).

    Structure: effects[mahadasha_lord][antardasha_lord] -> effect details
    """
    return load_rules("antardasha_effects").get("antardasha_effects", {})


def get_pratyantardasha_effects() -> dict[str, Any]:
    """Get Pratyantardasha effects (729 combinations: 9x9x9).

    Structure: effects[mahadasha_lord][antardasha_lord][pratyantardasha_lord] -> effect details
    """
    return load_rules("pratyantardasha_master").get("pratyantardasha_effects", {})


def get_combustion_rules() -> dict[str, Any]:
    """Get combustion (Asta) rules for 6 planets."""
    return load_rules("combustion_rules").get("combustion_rules", {})


def get_retrograde_rules() -> dict[str, Any]:
    """Get retrograde (Vakri) effects for 5 planets."""
    return load_rules("retrograde_rules").get("retrograde_rules", {})


def get_nakshatra_transit_rules() -> dict[str, Any]:
    """Get nakshatra transit effects (243 combinations: 9 planets x 27 nakshatras)."""
    return load_rules("nakshatra_transit_rules").get("nakshatra_transit_rules", {})


def get_transit_aspect_effects() -> dict[str, Any]:
    """Get transit aspect effect interpretations (405 entries: 9x9x5)."""
    return load_rules("transit_aspect_effects").get("transit_aspect_effects", {})


def get_varshaphal_rules() -> dict[str, Any]:
    """Get Varshaphal (Solar Return / Tajika) rules."""
    return load_rules("varshaphal_rules").get("varshaphal_rules", {})


def get_divisional_interpretation() -> dict[str, Any]:
    """Get D9/D10 divisional chart interpretation rules."""
    return load_rules("divisional_interpretation").get("divisional_interpretation", {})


def load_interpretation(name: str) -> dict[str, Any]:
    """Load an interpretation file from knowledge/interpretations/.

    Args:
        name: Interpretation name (without .json extension)
              e.g., "planet_in_house", "planet_in_sign", "dasha_guide"

    Returns:
        Interpretation data dictionary
    """
    filepath = INTERPRETATIONS_DIR / f"{name}.json"
    return _load_json_file(str(filepath))


# =============================================================================
# Panchanga definition accessors
# =============================================================================


def get_tithi_definitions() -> dict[str, Any]:
    """Get tithi (lunar day) definitions - 30 tithis."""
    return load_definition("tithis")


def get_karana_definitions() -> dict[str, Any]:
    """Get karana (half-tithi) definitions - 11 karanas."""
    return load_definition("karanas")


def get_nitya_yoga_definitions() -> dict[str, Any]:
    """Get nitya yoga definitions - 27 yogas."""
    return load_definition("nitya_yogas")


def get_vara_definitions() -> dict[str, Any]:
    """Get vara (weekday) definitions - 7 days."""
    return load_definition("varas")


def get_avastha_definitions() -> dict[str, Any]:
    """Get avastha (planetary state) definitions."""
    return load_definition("avasthas")


# =============================================================================
# Interpretation accessors
# =============================================================================


def get_planet_in_house_interpretations() -> dict[str, Any]:
    """Get planet-in-house interpretations (108 combinations: 9 planets x 12 houses)."""
    return load_interpretation("planet_in_house")


def get_planet_in_sign_interpretations() -> dict[str, Any]:
    """Get planet-in-sign interpretations (108 combinations: 9 planets x 12 signs)."""
    return load_interpretation("planet_in_sign")


def get_planet_in_nakshatra_interpretations() -> dict[str, Any]:
    """Get planet-in-nakshatra interpretations (243 combinations: 9 planets x 27 nakshatras)."""
    return load_interpretation("planet_in_nakshatra")


def get_house_lord_in_house_interpretations() -> dict[str, Any]:
    """Get house-lord-in-house interpretations (144 combinations: 12 lords x 12 houses)."""
    return load_interpretation("house_lord_in_house")


def get_dasha_guide() -> dict[str, Any]:
    """Get dasha practical guidance for each Mahadasha period."""
    return load_interpretation("dasha_guide")


def get_sookshma_dasha_guide() -> dict[str, Any]:
    """Get Sookshma Dasha (Level 4) practical guidance for each planet's micro-period."""
    return load_interpretation("sookshma_dasha_guide")


def get_prana_dasha_guide() -> dict[str, Any]:
    """Get Prana Dasha (Level 5) ultra-brief guidance for each planet's life-breath period."""
    return load_interpretation("prana_dasha_guide")


def get_deha_dasha_guide() -> dict[str, Any]:
    """Get Deha Dasha (Level 6) brief somatic guidance for each planet's body-level period."""
    return load_interpretation("deha_dasha_guide")


def get_planet_relationship(planet_a: str, planet_b: str) -> str:
    """Get natural relationship between two planets from planets.json.

    Returns one of: "same", "friend", "enemy", "neutral".
    """
    if planet_a == planet_b:
        return "same"
    planets_data = load_definition("planets").get("planets", {})
    planet_info = planets_data.get(planet_a.lower(), {})
    b_title = planet_b.capitalize()
    if b_title in planet_info.get("friends", []):
        return "friend"
    if b_title in planet_info.get("enemies", []):
        return "enemy"
    return "neutral"


def get_sookshma_dasha_effects() -> dict[str, Any]:
    """Get Sookshma Dasha combination effects (81 combos: PD lord x SD lord)."""
    return load_rules("sookshma_dasha_effects").get("sookshma_dasha_effects", {})


def get_prana_dasha_effects() -> dict[str, Any]:
    """Get Prana Dasha combination effects (81 combos: SD lord x Prana lord)."""
    return load_rules("prana_dasha_effects").get("prana_dasha_effects", {})


def get_deha_dasha_effects() -> dict[str, Any]:
    """Get Deha Dasha combination effects (81 combos: Prana lord x Deha lord)."""
    return load_rules("deha_dasha_effects").get("deha_dasha_effects", {})


def get_bphs_cross_reference() -> dict[str, Any]:
    """Get BPHS cross-reference mapping (tools → chapters).

    Returns the deterministic mapping from MCP tool names to BPHS chapters
    and verse ranges. Used by bphs_enricher.py for automatic citation.
    """
    return _load_json_file(str(KNOWLEDGE_DIR / "bphs_cross_reference.json"))


def get_bphs_chapters_for_tool(tool_name: str) -> list[int]:
    """Get BPHS chapter numbers relevant to a specific MCP tool.

    Args:
        tool_name: MCP tool function name (e.g., "detect_yogas", "current_dasha")

    Returns:
        List of BPHS chapter numbers (1-100)
    """
    xref = get_bphs_cross_reference()
    mapping = xref.get("tool_mappings", {}).get(tool_name, {})
    return list(mapping.get("chapters", []))


def clear_cache() -> None:
    """Clear the knowledge cache (useful for testing)."""
    _load_json_file.cache_clear()
