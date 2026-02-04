"""
108 Knowledge MCP Server

Provides lookup tools for Jyotish knowledge base - planets, nakshatras, yogas, etc.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add packages to path
SERVICES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERVICES_ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402

# Initialize MCP server
mcp = FastMCP("108-knowledge")

# Knowledge base paths
KNOWLEDGE_DIR = SERVICES_ROOT / "knowledge"
DEFINITIONS_DIR = KNOWLEDGE_DIR / "definitions"
RULES_DIR = KNOWLEDGE_DIR / "rules"

# Cache for loaded JSON files
_cache: dict[str, Any] = {}


def _load_json(filepath: Path) -> dict:
    """Load JSON file with caching."""
    key = str(filepath)
    if key not in _cache:
        if filepath.exists():
            with filepath.open(encoding="utf-8") as f:
                _cache[key] = json.load(f)
        else:
            _cache[key] = {}
    return _cache[key]


def _get_planets() -> dict:
    return _load_json(DEFINITIONS_DIR / "planets.json").get("planets", {})


def _get_rashis() -> dict:
    return _load_json(DEFINITIONS_DIR / "rashis.json").get("rashis", {})


def _get_nakshatras() -> list:
    return _load_json(DEFINITIONS_DIR / "nakshatras.json").get("nakshatras", [])


def _get_houses() -> dict:
    return _load_json(DEFINITIONS_DIR / "houses.json").get("houses", {})


def _get_yoga_rules() -> dict:
    # Use master file with 522 yogas (consolidated from all parts)
    return _load_json(RULES_DIR / "yoga_master.json").get("yoga_rules", {})


def _get_dosha_rules() -> dict:
    # Use master file with 55 doshas (expanded from classical texts)
    return _load_json(RULES_DIR / "dosha_master.json").get("dosha_rules", {})


@mcp.tool()
def lookup_planet(planet_id: str) -> dict[str, Any]:
    """
    Get complete planet definition.

    Args:
        planet_id: Planet identifier (sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu)

    Returns:
        Complete planet data including nature, signs owned, exaltation,
        friends/enemies, karakas, remedies, etc.
    """
    try:
        planets = _get_planets()
        planet_key = planet_id.lower()

        if planet_key in planets:
            data = planets[planet_key]
            return {
                "found": True,
                "planet": data,
                "summary": f"{data['name']} ({data['sanskrit']}) is a {data['nature']} planet ruling {', '.join(data['owns_signs'])}.",
            }
        else:
            return {
                "found": False,
                "error": f"Planet '{planet_id}' not found",
                "available": list(planets.keys()),
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_rashi(rashi_id: str) -> dict[str, Any]:
    """
    Get complete rashi (zodiac sign) definition.

    Args:
        rashi_id: Sign identifier (aries, taurus, etc.)

    Returns:
        Complete sign data including element, quality, ruler, body parts, etc.
    """
    try:
        rashis = _get_rashis()
        rashi_key = rashi_id.lower()

        if rashi_key in rashis:
            data = rashis[rashi_key]
            return {
                "found": True,
                "rashi": data,
                "summary": f"{data['name']} ({data['sanskrit']}) is a {data['element']} {data['quality']} sign ruled by {data['ruler']}.",
            }
        else:
            return {
                "found": False,
                "error": f"Rashi '{rashi_id}' not found",
                "available": list(rashis.keys()),
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_nakshatra(nakshatra_name: str) -> dict[str, Any]:
    """
    Get complete nakshatra definition.

    Args:
        nakshatra_name: Nakshatra name (Ashwini, Bharani, etc.)

    Returns:
        Complete nakshatra data including ruler, deity, symbol, padas, etc.
    """
    try:
        nakshatras = _get_nakshatras()
        search_name = nakshatra_name.lower().replace(" ", "").replace("_", "")

        for nak in nakshatras:
            nak_name = nak["name"].lower().replace(" ", "")
            if nak_name == search_name or search_name in nak_name:
                return {
                    "found": True,
                    "nakshatra": nak,
                    "summary": f"{nak['name']} ({nak.get('sanskrit', '')}) is ruled by {nak['ruler']}, deity: {nak['deity']}, symbol: {nak['symbol']}.",
                }

        return {
            "found": False,
            "error": f"Nakshatra '{nakshatra_name}' not found",
            "available": [n["name"] for n in nakshatras],
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_house(house_number: int) -> dict[str, Any]:
    """
    Get complete house (bhava) definition.

    Args:
        house_number: House number (1-12)

    Returns:
        Complete house data including significations, karaka, category, etc.
    """
    try:
        houses = _get_houses()
        house_key = str(house_number)

        if house_key in houses:
            data = houses[house_key]
            return {
                "found": True,
                "house": data,
                "summary": f"House {house_number} ({data['name']}/{data['sanskrit']}) signifies: {', '.join(data['significations'][:5])}...",
            }
        else:
            return {
                "found": False,
                "error": f"House {house_number} not found (must be 1-12)",
                "available": list(houses.keys()),
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_yoga(yoga_id: str) -> dict[str, Any]:
    """
    Get yoga definition and interpretation.

    Args:
        yoga_id: Yoga identifier (shasha_yoga, gajakesari_yoga, etc.)

    Returns:
        Yoga definition, detection rules, effects, and cancellation conditions
    """
    try:
        yogas = _get_yoga_rules()
        yoga_key = yoga_id.lower().replace(" ", "_")

        # Try exact match first
        if yoga_key in yogas:
            data = yogas[yoga_key]
            return {
                "found": True,
                "yoga": data,
                "summary": f"{data['name']}: {data.get('description', 'No description')}",
            }

        # Try partial match
        for key, data in yogas.items():
            if yoga_key in key or yoga_key in data.get("name", "").lower():
                return {
                    "found": True,
                    "yoga": data,
                    "matched_id": key,
                    "summary": f"{data['name']}: {data.get('description', 'No description')}",
                }

        return {
            "found": False,
            "error": f"Yoga '{yoga_id}' not found",
            "available": list(yogas.keys()),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_dosha(dosha_id: str) -> dict[str, Any]:
    """
    Get dosha definition, effects, and remedies.

    Args:
        dosha_id: Dosha identifier (mangal_dosha, kaal_sarp_dosha, etc.)

    Returns:
        Dosha definition, detection rules, effects, remedies, and cancellation
    """
    try:
        doshas = _get_dosha_rules()
        dosha_key = dosha_id.lower().replace(" ", "_")

        if dosha_key in doshas:
            data = doshas[dosha_key]
            return {
                "found": True,
                "dosha": data,
                "summary": f"{data['name']}: {data.get('description', 'No description')}",
            }

        # Try partial match
        for key, data in doshas.items():
            if dosha_key in key or dosha_key in data.get("name", "").lower():
                return {
                    "found": True,
                    "dosha": data,
                    "matched_id": key,
                    "summary": f"{data['name']}: {data.get('description', 'No description')}",
                }

        return {
            "found": False,
            "error": f"Dosha '{dosha_id}' not found",
            "available": list(doshas.keys()),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_antardasha_effects(mahadasha_lord: str, antardasha_lord: str) -> dict[str, Any]:
    """
    Lookup Antardasha effects from knowledge base.

    Provides detailed interpretation for any of the 81 Mahadasha-Antardasha combinations.

    Args:
        mahadasha_lord: Mahadasha planet (sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu)
        antardasha_lord: Antardasha planet

    Returns:
        Effects including general themes, positive/negative outcomes, health, career, relationships
    """
    try:
        data = _load_json(RULES_DIR / "antardasha_effects.json")
        effects = data.get("antardasha_effects", {})

        md_key = mahadasha_lord.lower()
        ad_key = antardasha_lord.lower()

        md_effects = effects.get(md_key, {})
        ad_effects = md_effects.get(ad_key)

        if ad_effects:
            return {
                "found": True,
                "mahadasha": md_key,
                "antardasha": ad_key,
                "effects": ad_effects,
                "summary": (
                    f"{mahadasha_lord.capitalize()}-{antardasha_lord.capitalize()} Antardasha: "
                    + (
                        ad_effects.get("general_effects", ["No summary available"])[0]
                        if ad_effects.get("general_effects")
                        else "Effects data available"
                    )
                ),
            }
        else:
            return {
                "found": False,
                "mahadasha": md_key,
                "antardasha": ad_key,
                "error": f"No effects found for {mahadasha_lord}-{antardasha_lord} combination",
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_pratyantardasha_effects(
    mahadasha_lord: str, antardasha_lord: str, pratyantardasha_lord: str
) -> dict[str, Any]:
    """
    Lookup Pratyantardasha effects from knowledge base (729 combinations).

    Provides detailed interpretation for any of the 729 MD-AD-PD combinations.

    Args:
        mahadasha_lord: Mahadasha planet
        antardasha_lord: Antardasha planet
        pratyantardasha_lord: Pratyantardasha planet

    Returns:
        Effects including theme, health, career, relationships, finances, timing
    """
    try:
        data = _load_json(RULES_DIR / "pratyantardasha_master.json")
        effects = data.get("pratyantardasha_effects", {})

        md_key = mahadasha_lord.lower()
        ad_key = antardasha_lord.lower()
        pd_key = pratyantardasha_lord.lower()

        pd_effects = effects.get(md_key, {}).get(ad_key, {}).get(pd_key)

        if pd_effects:
            return {
                "found": True,
                "mahadasha": md_key,
                "antardasha": ad_key,
                "pratyantardasha": pd_key,
                "effects": pd_effects,
                "summary": (
                    f"{md_key.capitalize()}-{ad_key.capitalize()}-{pd_key.capitalize()} "
                    f"Pratyantardasha: {pd_effects.get('theme', 'Effects data available')}"
                ),
            }
        else:
            return {
                "found": False,
                "mahadasha": md_key,
                "antardasha": ad_key,
                "pratyantardasha": pd_key,
                "error": (
                    f"No effects found for {mahadasha_lord}-{antardasha_lord}-"
                    f"{pratyantardasha_lord} combination"
                ),
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def search_knowledge(query: str, category: str | None = None) -> dict[str, Any]:
    """
    Search across knowledge base.

    Args:
        query: Search term
        category: Optional category filter (planet, rashi, nakshatra, house, yoga, dosha)

    Returns:
        Matching results from knowledge base
    """
    try:
        results = []
        query_lower = query.lower()

        # Search planets
        if not category or category == "planet":
            for key, data in _get_planets().items():
                if _matches(query_lower, [key, data.get("name", ""), data.get("sanskrit", "")]):
                    results.append(
                        {"type": "planet", "id": key, "name": data["name"], "data": data}
                    )

        # Search rashis
        if not category or category == "rashi":
            for key, data in _get_rashis().items():
                if _matches(query_lower, [key, data.get("name", ""), data.get("sanskrit", "")]):
                    results.append({"type": "rashi", "id": key, "name": data["name"], "data": data})

        # Search nakshatras
        if not category or category == "nakshatra":
            for data in _get_nakshatras():
                if _matches(
                    query_lower,
                    [data.get("name", ""), data.get("sanskrit", ""), data.get("ruler", "")],
                ):
                    results.append(
                        {
                            "type": "nakshatra",
                            "id": data["name"],
                            "name": data["name"],
                            "data": data,
                        }
                    )

        # Search houses
        if not category or category == "house":
            for key, data in _get_houses().items():
                significations = " ".join(data.get("significations", []))
                if _matches(
                    query_lower, [data.get("name", ""), data.get("sanskrit", ""), significations]
                ):
                    results.append({"type": "house", "id": key, "name": data["name"], "data": data})

        # Search yogas
        if not category or category == "yoga":
            for key, data in _get_yoga_rules().items():
                if _matches(query_lower, [key, data.get("name", ""), data.get("description", "")]):
                    results.append({"type": "yoga", "id": key, "name": data["name"], "data": data})

        # Search doshas
        if not category or category == "dosha":
            for key, data in _get_dosha_rules().items():
                if _matches(query_lower, [key, data.get("name", ""), data.get("description", "")]):
                    results.append({"type": "dosha", "id": key, "name": data["name"], "data": data})

        return {
            "query": query,
            "category": category,
            "total_results": len(results),
            "results": results[:20],  # Limit to 20 results
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def list_all(category: str) -> dict[str, Any]:
    """
    List all items in a category.

    Args:
        category: Category to list (planets, rashis, nakshatras, houses, yogas, doshas)

    Returns:
        List of all items in the category
    """
    try:
        if category == "planets":
            data = _get_planets()
            return {"category": category, "count": len(data), "items": list(data.keys())}

        elif category == "rashis":
            data = _get_rashis()
            return {"category": category, "count": len(data), "items": list(data.keys())}

        elif category == "nakshatras":
            data = _get_nakshatras()
            return {"category": category, "count": len(data), "items": [n["name"] for n in data]}

        elif category == "houses":
            data = _get_houses()
            return {
                "category": category,
                "count": len(data),
                "items": [f"{k}: {v['name']}" for k, v in data.items()],
            }

        elif category == "yogas":
            data = _get_yoga_rules()
            return {"category": category, "count": len(data), "items": list(data.keys())}

        elif category == "doshas":
            data = _get_dosha_rules()
            return {"category": category, "count": len(data), "items": list(data.keys())}

        else:
            return {
                "error": f"Unknown category: {category}",
                "available": ["planets", "rashis", "nakshatras", "houses", "yogas", "doshas"],
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def _matches(query: str, fields: list[str]) -> bool:
    """Check if query matches any field."""
    return any(field and query in field.lower() for field in fields)


if __name__ == "__main__":
    mcp.run()
