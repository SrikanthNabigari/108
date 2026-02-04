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
    """Get compatibility/matching rules."""
    return load_rules("compatibility_rules").get("compatibility_rules", {})


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


def clear_cache() -> None:
    """Clear the knowledge cache (useful for testing)."""
    _load_json_file.cache_clear()
