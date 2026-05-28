"""
108 Knowledge MCP Server

Provides lookup tools for Jyotish knowledge base - planets, nakshatras, yogas, etc.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Add packages to path
SERVICES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERVICES_ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from packages.core.src.bphs_enricher import enrich_response  # noqa: E402
from packages.core.src.knowledge_loader import (  # noqa: E402
    get_avastha_definitions,
    get_karana_definitions,
    get_nitya_yoga_definitions,
    get_tithi_definitions,
    get_vara_definitions,
)

# Initialize MCP server
mcp = FastMCP("108-knowledge")

# Knowledge base paths
KNOWLEDGE_DIR = SERVICES_ROOT / "knowledge"
DEFINITIONS_DIR = KNOWLEDGE_DIR / "definitions"
RULES_DIR = KNOWLEDGE_DIR / "rules"

# BPHS knowledge base paths (extracted BPHS text + ChromaDB vector DB)
BPHS_ROOT = Path(
    os.environ.get("BPHS_KNOWLEDGE_PATH", str(SERVICES_ROOT.parent / "108" / "knowledge"))
)
BPHS_JSON_DIR = BPHS_ROOT / "04_JSON"
BPHS_VECTOR_DB_DIR = BPHS_ROOT / "05_VectorDB"

# Cache for loaded JSON files
_cache: dict[str, Any] = {}

# Lazy-initialized ChromaDB collection
_bphs_collection = None


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
            result = {
                "found": True,
                "planet": data,
                "summary": f"{data['name']} ({data['sanskrit']}) is a {data['nature']} planet ruling {', '.join(data['owns_signs'])}.",
            }
            return enrich_response("lookup_planet", result, {"planet": planet_key})
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
            result = {
                "found": True,
                "rashi": data,
                "summary": f"{data['name']} ({data['sanskrit']}) is a {data['element']} {data['quality']} sign ruled by {data['ruler']}.",
            }
            return enrich_response("lookup_rashi", result)
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
                result = {
                    "found": True,
                    "nakshatra": nak,
                    "summary": f"{nak['name']} ({nak.get('sanskrit', '')}) is ruled by {nak['ruler']}, deity: {nak['deity']}, symbol: {nak['symbol']}.",
                }
                return enrich_response("lookup_nakshatra", result)

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
            result = {
                "found": True,
                "house": data,
                "summary": f"House {house_number} ({data['name']}/{data['sanskrit']}) signifies: {', '.join(data['significations'][:5])}...",
            }
            return enrich_response("lookup_house", result, {"house": house_number})
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
            result = {
                "found": True,
                "yoga": data,
                "summary": f"{data['name']}: {data.get('description', 'No description')}",
            }
            return enrich_response("lookup_yoga", result, {"yogas": [yoga_key]})

        # Try partial match
        for key, data in yogas.items():
            if yoga_key in key or yoga_key in data.get("name", "").lower():
                result = {
                    "found": True,
                    "yoga": data,
                    "matched_id": key,
                    "summary": f"{data['name']}: {data.get('description', 'No description')}",
                }
                return enrich_response("lookup_yoga", result, {"yogas": [key]})

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
            result = {
                "found": True,
                "dosha": data,
                "summary": f"{data['name']}: {data.get('description', 'No description')}",
            }
            return enrich_response("lookup_dosha", result, {"doshas": [dosha_key]})

        # Try partial match
        for key, data in doshas.items():
            if dosha_key in key or dosha_key in data.get("name", "").lower():
                result = {
                    "found": True,
                    "dosha": data,
                    "matched_id": key,
                    "summary": f"{data['name']}: {data.get('description', 'No description')}",
                }
                return enrich_response("lookup_dosha", result, {"doshas": [key]})

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
            result = {
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
            return enrich_response(
                "lookup_antardasha_effects",
                result,
                {"mahadasha_lord": md_key, "antardasha_lord": ad_key},
            )
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
            result = {
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
            return enrich_response(
                "lookup_pratyantardasha_effects", result, {"mahadasha_lord": md_key}
            )
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


@mcp.tool()
def lookup_tithi(tithi_number: int) -> dict[str, Any]:
    """
    Get tithi (lunar day) definition.

    There are 30 tithis in a lunar month (15 in Shukla Paksha, 15 in Krishna Paksha).
    Each tithi has specific qualities for muhurta and activity planning.

    Args:
        tithi_number: Tithi number (1-30, where 1-15 = Shukla, 16-30 = Krishna)

    Returns:
        Tithi details including name, deity, nature, and auspicious activities

    Example:
        lookup_tithi(1)  # Pratipada
    """
    try:
        data = get_tithi_definitions()
        tithis = data.get("tithis", data)

        # Search by number
        tithi_key = str(tithi_number)
        if isinstance(tithis, dict):
            if tithi_key in tithis:
                return {"found": True, "tithi": tithis[tithi_key]}
            # Try searching in list format
            for _key, val in tithis.items():
                if isinstance(val, dict) and val.get("number") == tithi_number:
                    return {"found": True, "tithi": val}
        elif isinstance(tithis, list):
            for t in tithis:
                if isinstance(t, dict) and t.get("number") == tithi_number:
                    return {"found": True, "tithi": t}

        return {"found": False, "error": f"Tithi {tithi_number} not found"}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_karana(karana_name: str) -> dict[str, Any]:
    """
    Get karana (half-tithi) definition.

    There are 11 karanas, each covering half a tithi. 4 are fixed (Shakuni,
    Chatushpada, Naga, Kimstughna) and 7 are repeating.

    Args:
        karana_name: Karana name (e.g., "bava", "balava", "shakuni")

    Returns:
        Karana details including nature and effects

    Example:
        lookup_karana("bava")
    """
    try:
        data = get_karana_definitions()
        karanas = data.get("karanas", data)

        search = karana_name.lower().replace(" ", "_")
        if isinstance(karanas, dict):
            if search in karanas:
                return {"found": True, "karana": karanas[search]}
            for key, val in karanas.items():
                if search in key.lower() or (
                    isinstance(val, dict) and search in val.get("name", "").lower()
                ):
                    return {"found": True, "karana": val, "matched_key": key}
        elif isinstance(karanas, list):
            for k in karanas:
                if isinstance(k, dict) and search in k.get("name", "").lower():
                    return {"found": True, "karana": k}

        return {"found": False, "error": f"Karana '{karana_name}' not found"}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_vara(day_name: str) -> dict[str, Any]:
    """
    Get vara (weekday) definition.

    Each day of the week has a ruling planet and specific qualities that
    affect muhurta and activity planning.

    Args:
        day_name: Day name in English or Sanskrit (e.g., "monday", "somavara", "sunday")

    Returns:
        Vara details including ruling planet, nature, and auspicious activities

    Example:
        lookup_vara("thursday")
    """
    try:
        data = get_vara_definitions()
        varas = data.get("varas", data)

        search = day_name.lower().replace(" ", "_")
        if isinstance(varas, dict):
            if search in varas:
                return {"found": True, "vara": varas[search]}
            for key, val in varas.items():
                if search in key.lower() or (
                    isinstance(val, dict)
                    and (
                        search in val.get("name", "").lower()
                        or search in val.get("english_name", "").lower()
                    )
                ):
                    return {"found": True, "vara": val, "matched_key": key}
        elif isinstance(varas, list):
            for v in varas:
                if isinstance(v, dict) and (
                    search in v.get("name", "").lower()
                    or search in v.get("english_name", "").lower()
                ):
                    return {"found": True, "vara": v}

        return {"found": False, "error": f"Vara '{day_name}' not found"}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_avastha(planet: str, longitude: float = 0.0) -> dict[str, Any]:
    """
    Get avastha (planetary state) definitions for a planet.

    Avasthas describe the state/condition of a planet. There are multiple
    avastha systems: Baladi (age), Jagradadi (alertness), Deeptadi (luminosity).

    Args:
        planet: Planet name (e.g., "sun", "jupiter")
        longitude: Planet's longitude for calculating specific avastha (optional)

    Returns:
        Avastha system definitions and the planet's current avastha if longitude given

    Example:
        lookup_avastha("jupiter", 136.24)
    """
    try:
        data = get_avastha_definitions()
        avasthas = data.get("avasthas", data)

        planet_lower = planet.lower()
        result: dict[str, Any] = {"found": True, "planet": planet_lower, "avasthas": avasthas}

        # Calculate Baladi Avastha from longitude if provided
        if longitude > 0:
            degree_in_sign = longitude % 30
            # Baladi avastha: Bala (0-6), Kumara (6-12), Yuva (12-18), Vridha (18-24), Mrita (24-30)
            if degree_in_sign < 6:
                result["baladi_avastha"] = "bala"
                result["baladi_meaning"] = "Infant state - weak expression"
            elif degree_in_sign < 12:
                result["baladi_avastha"] = "kumara"
                result["baladi_meaning"] = "Adolescent state - developing"
            elif degree_in_sign < 18:
                result["baladi_avastha"] = "yuva"
                result["baladi_meaning"] = "Youthful state - strongest expression"
            elif degree_in_sign < 24:
                result["baladi_avastha"] = "vridha"
                result["baladi_meaning"] = "Old state - declining strength"
            else:
                result["baladi_avastha"] = "mrita"
                result["baladi_meaning"] = "Dead state - weakest expression"

        return result

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def lookup_nitya_yoga(yoga_number: int) -> dict[str, Any]:
    """
    Get Nitya Yoga definition.

    Nitya Yogas are 27 yogas formed by the combined longitudes of Sun and Moon.
    Each yoga has specific qualities for muhurta and daily activity planning.

    Args:
        yoga_number: Yoga number (1-27)

    Returns:
        Nitya Yoga details including name, nature, ruling planet, and effects

    Example:
        lookup_nitya_yoga(1)  # Vishkambha
    """
    try:
        data = get_nitya_yoga_definitions()
        yogas = data.get("nitya_yogas", data)

        yoga_key = str(yoga_number)
        if isinstance(yogas, dict):
            if yoga_key in yogas:
                return {"found": True, "nitya_yoga": yogas[yoga_key]}
            for _key, val in yogas.items():
                if isinstance(val, dict) and val.get("number") == yoga_number:
                    return {"found": True, "nitya_yoga": val}
        elif isinstance(yogas, list):
            for y in yogas:
                if isinstance(y, dict) and y.get("number") == yoga_number:
                    return {"found": True, "nitya_yoga": y}

        return {"found": False, "error": f"Nitya Yoga {yoga_number} not found"}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def _get_bphs_collection():
    """Get ChromaDB collection for BPHS semantic search (lazy init)."""
    global _bphs_collection
    if _bphs_collection is None:
        import chromadb

        client = chromadb.PersistentClient(path=str(BPHS_VECTOR_DB_DIR))
        _bphs_collection = client.get_collection(name="bphs_knowledge")
    return _bphs_collection


def _get_bphs_master_index() -> dict:
    """Load BPHS master index."""
    return _load_json(BPHS_JSON_DIR / "bphs_master_index.json")


def _get_bphs_knowledge() -> dict:
    """Load BPHS knowledge entries."""
    return _load_json(BPHS_JSON_DIR / "bphs_knowledge.json")


@mcp.tool()
def search_bphs(
    query: str,
    max_results: int = 10,
    chapter: int | None = None,
    volume: int | None = None,
    topic: str | None = None,
) -> dict[str, Any]:
    """
    Semantic search across BPHS (Brihat Parashara Hora Shastra) text.

    Uses vector embeddings to find conceptually related content even without
    exact keyword matches. For example, searching "marriage timing" will find
    content about 7th house lord, Venus placement, and dasha periods.

    Args:
        query: Natural language search query (e.g., "marriage timing from dasha",
               "raja yoga conditions", "remedies for weak saturn")
        max_results: Maximum results to return (default: 10)
        chapter: Filter by chapter number (1-100)
        volume: Filter by volume (1 or 2)
        topic: Filter by topic keyword (e.g., "raja_yogas", "saturn_remedies")

    Returns:
        Ranked results with text, chapter context, and similarity scores
    """
    try:
        # Try ChromaDB first, fall back to JSON keyword search
        try:
            collection = _get_bphs_collection()
            return _search_bphs_chromadb(collection, query, max_results, chapter, volume, topic)
        except Exception:
            # ChromaDB not available — fall back to JSON keyword search
            return _search_bphs_json_fallback(query, max_results, chapter, volume, topic)

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def _search_bphs_chromadb(collection, query, max_results, chapter, volume, topic):
    """Semantic search using ChromaDB vector embeddings."""
    where_clauses = []
    if chapter is not None:
        where_clauses.append({"chapter": {"$eq": chapter}})
    if volume is not None:
        where_clauses.append({"volume": {"$eq": volume}})
    if topic is not None:
        where_clauses.append({"topics": {"$contains": topic}})

    where = None
    if len(where_clauses) == 1:
        where = where_clauses[0]
    elif len(where_clauses) > 1:
        where = {"$and": where_clauses}

    fetch_n = min(max_results * 3, collection.count())

    results = collection.query(
        query_texts=[query],
        n_results=fetch_n,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"][0]:
        return {"query": query, "total_results": 0, "results": [], "search_mode": "semantic"}

    seen_entries = set()
    output = []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        strict=False,
    ):
        entry_idx = meta["entry_index"]
        if entry_idx in seen_entries:
            continue
        seen_entries.add(entry_idx)

        output.append(
            {
                "text": doc,
                "chapter": meta["chapter"],
                "chapter_title": meta["chapter_title"],
                "volume": meta["volume"],
                "verse_ref": meta["verse_ref"],
                "type": meta["type"],
                "topics": meta["topics"],
                "score": round(1 - dist, 4),
            }
        )

        if len(output) >= max_results:
            break

    return {
        "query": query,
        "total_results": len(output),
        "results": output,
        "search_mode": "semantic",
    }


def _search_bphs_json_fallback(query, max_results, chapter, volume, topic):
    """Keyword-based fallback search on bphs_knowledge.json when ChromaDB unavailable."""
    knowledge = _get_bphs_knowledge()
    entries = knowledge.get("entries", [])
    query_lower = query.lower()
    query_words = query_lower.split()

    scored = []
    for entry in entries:
        # Apply filters
        if chapter is not None and entry.get("chapter") != chapter:
            continue
        if volume is not None and entry.get("volume") != volume:
            continue
        if topic is not None:
            entry_topics = entry.get("topics", [])
            if isinstance(entry_topics, str):
                entry_topics = [t.strip() for t in entry_topics.split(",")]
            if not any(topic.lower() in t.lower() for t in entry_topics):
                continue

        # Score by keyword matching
        text = entry.get("text", "").lower()
        keywords = entry.get("keywords", [])
        if isinstance(keywords, list):
            keywords_str = " ".join(k.lower() for k in keywords)
        else:
            keywords_str = str(keywords).lower()
        topics_str = (
            " ".join(t.lower() for t in entry.get("topics", []))
            if isinstance(entry.get("topics"), list)
            else str(entry.get("topics", "")).lower()
        )

        combined = f"{text} {keywords_str} {topics_str}"

        # Count matching words
        matches = sum(1 for w in query_words if w in combined)
        if matches == 0:
            continue

        # Score: proportion of query words matched + bonus for keyword hits
        score = matches / len(query_words)
        keyword_bonus = sum(0.1 for w in query_words if w in keywords_str)
        score += keyword_bonus

        scored.append((score, entry))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    output = []
    for score, entry in scored[:max_results]:
        output.append(
            {
                "text": entry.get("text", ""),
                "chapter": entry.get("chapter"),
                "chapter_title": entry.get("chapter_title", ""),
                "volume": entry.get("volume"),
                "verse_ref": entry.get("verse_ref", ""),
                "type": entry.get("type", ""),
                "topics": ", ".join(entry["topics"])
                if isinstance(entry.get("topics"), list)
                else str(entry.get("topics", "")),
                "score": round(score, 4),
            }
        )

    return {
        "query": query,
        "total_results": len(output),
        "results": output,
        "search_mode": "keyword_fallback",
    }


@mcp.tool()
def get_bphs_chapter(chapter_number: int) -> dict[str, Any]:
    """
    Get structured content for a specific BPHS chapter.

    Returns all sections (verse translations, notes, headers) for the chapter.

    Args:
        chapter_number: Chapter number (1-100)

    Returns:
        Chapter data with title, volume, topics, and all text sections
    """
    try:
        chapter_file = BPHS_JSON_DIR / "chapters" / f"ch{chapter_number:03d}.json"
        if not chapter_file.exists():
            return {
                "found": False,
                "error": f"Chapter {chapter_number} not found (valid: 1-100)",
            }

        data = _load_json(chapter_file)
        title = data.get("chapter_title") or data.get("title", "Unknown")

        # Add related MCP tools from cross-reference
        from packages.core.src.bphs_enricher import get_tools_for_chapter

        related_tools = get_tools_for_chapter(chapter_number)

        return {
            "found": True,
            "chapter": data,
            "related_tools": related_tools,
            "summary": (
                f"Ch.{chapter_number}: {title} "
                f"(Vol.{data.get('volume', '?')}, {len(data.get('sections', []))} sections, "
                f"{len(related_tools)} related MCP tools)"
            ),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def get_bphs_topics() -> dict[str, Any]:
    """
    List all available BPHS topics with chapter mappings.

    Returns the complete topic index from the BPHS master index,
    mapping each topic to the chapters that cover it.

    Returns:
        Topic index with chapter numbers, plus chapter listing
    """
    try:
        index = _get_bphs_master_index()
        topic_index = index.get("topic_index", {})
        chapters = index.get("chapters", [])

        # Add related tools from cross-reference to each chapter
        from packages.core.src.bphs_enricher import get_tools_for_chapter

        chapter_list = [
            {
                "number": ch["number"],
                "title": ch["title"],
                "volume": ch["volume"],
                "related_tools": get_tools_for_chapter(ch["number"]),
            }
            for ch in chapters
        ]

        # Count how many chapters have tool mappings
        mapped_chapters = sum(1 for ch in chapter_list if ch["related_tools"])

        return {
            "total_topics": len(topic_index),
            "total_chapters": len(chapter_list),
            "chapters_with_tool_mappings": mapped_chapters,
            "topic_index": topic_index,
            "chapters": chapter_list,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def _matches(query: str, fields: list[str]) -> bool:
    """Check if query matches any field."""
    return any(field and query in field.lower() for field in fields)


if __name__ == "__main__":
    mcp.run()
