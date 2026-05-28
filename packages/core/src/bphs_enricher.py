"""BPHS Enrichment Module for 108-core MCP Tools.

Adds authoritative Brihat Parashara Hora Shastra (BPHS) chapter and verse
references to any MCP tool response. Uses deterministic cross-reference
lookups (no AI/embedding), making it fast and reliable.

Usage:
    from packages.core.src.bphs_enricher import enrich_response

    result = detect_yogas(planets, lagna_rashi)
    result = enrich_response("detect_yogas", result, {"yogas": ["hamsa_yoga"]})
"""

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# --- Path resolution ---
# 108-core knowledge directory (cross-reference lives here)
_CORE_KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"

# BPHS chapter JSONs (in the separate 108/knowledge directory)
_BPHS_ROOT = Path(
    os.environ.get(
        "BPHS_KNOWLEDGE_PATH",
        str(Path(__file__).parent.parent.parent.parent.parent / "108" / "knowledge"),
    )
)
_BPHS_JSON_DIR = _BPHS_ROOT / "04_JSON"
_BPHS_CHAPTERS_DIR = _BPHS_JSON_DIR / "chapters"

# Maximum references to include per response (keep responses concise)
MAX_REFERENCES = 5
# Maximum text length per reference excerpt
MAX_EXCERPT_LENGTH = 500


@lru_cache(maxsize=1)
def _load_cross_reference() -> dict[str, Any]:
    """Load and cache the BPHS cross-reference index."""
    filepath = _CORE_KNOWLEDGE_DIR / "bphs_cross_reference.json"
    if not filepath.exists():
        logger.warning(f"BPHS cross-reference not found: {filepath}")
        return {}
    try:
        with filepath.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Error loading BPHS cross-reference: {e}")
        return {}


@lru_cache(maxsize=100)
def _load_bphs_chapter(chapter_number: int) -> dict[str, Any]:
    """Load and cache a BPHS chapter JSON file."""
    filepath = _BPHS_CHAPTERS_DIR / f"ch{chapter_number:03d}.json"
    if not filepath.exists():
        logger.warning(f"BPHS chapter file not found: {filepath}")
        return {}
    try:
        with filepath.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Error loading BPHS chapter {chapter_number}: {e}")
        return {}


def _extract_relevant_sections(
    chapter_data: dict[str, Any],
    keywords: list[str] | None = None,
    max_sections: int = 3,
) -> list[dict[str, Any]]:
    """Extract the most relevant sections from a BPHS chapter.

    Prioritizes translations over notes/prose. If keywords given,
    scores sections by keyword match count.
    """
    sections = chapter_data.get("sections", [])
    if not sections:
        return []

    # Type priority: translations are most authoritative
    type_priority = {"translation": 3, "notes": 2, "prose": 1}

    if keywords:
        # Score each section by keyword matches + type priority
        scored = []
        keywords_lower = [k.lower() for k in keywords]
        for section in sections:
            text_lower = section.get("text", "").lower()
            section_keywords = [k.lower() for k in section.get("keywords", [])]

            # Count keyword matches in text and section keywords
            match_score = sum(
                1 for kw in keywords_lower if kw in text_lower or kw in section_keywords
            )
            type_score = type_priority.get(section.get("type", ""), 0)
            total_score = match_score * 10 + type_score

            if match_score > 0:
                scored.append((total_score, section))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored[:max_sections]]
    else:
        # No keywords: return first few translations, then notes
        sorted_sections = sorted(
            sections,
            key=lambda s: type_priority.get(s.get("type", ""), 0),
            reverse=True,
        )
        return sorted_sections[:max_sections]


def _build_reference(
    chapter_number: int,
    chapter_title: str,
    section: dict[str, Any],
    relevance: str = "",
) -> dict[str, Any]:
    """Build a single BPHS reference entry."""
    text = section.get("text", "")
    if len(text) > MAX_EXCERPT_LENGTH:
        text = text[:MAX_EXCERPT_LENGTH] + "..."

    verse_ref = section.get("verse_ref")
    ref_str = f"Ch.{chapter_number}"
    if verse_ref:
        ref_str += f", verses {verse_ref}"

    return {
        "chapter": chapter_number,
        "chapter_title": chapter_title,
        "verse_ref": ref_str,
        "type": section.get("type", ""),
        "text": text,
        "relevance": relevance,
    }


def _get_chapters_for_tool(
    tool_name: str,
    context: dict[str, Any] | None = None,
) -> list[int]:
    """Get relevant BPHS chapter numbers for a tool + context."""
    xref = _load_cross_reference()
    tool_mappings = xref.get("tool_mappings", {})
    mapping = tool_mappings.get(tool_name, {})

    if not mapping:
        return []

    chapters = list(mapping.get("chapters", []))

    # Try to narrow down using context
    if context:
        # For dasha tools: narrow by planet
        if "mahadasha_lord" in context or "planet" in context:
            planet = context.get("mahadasha_lord") or context.get("planet", "")
            planet_lower = planet.lower() if planet else ""

            # Check planet_specific or planet_dasha_chapters
            planet_specific = mapping.get("planet_specific", {})
            if planet_lower in planet_specific:
                chapters = planet_specific[planet_lower].get("chapters", chapters)
            else:
                # Check top-level planet_dasha_chapters
                planet_dasha = xref.get("planet_dasha_chapters", {})
                if planet_lower in planet_dasha:
                    pd = planet_dasha[planet_lower]
                    if "antardasha" in tool_name:
                        chapters = [pd["antardasha"]]
                    elif "dasha" in tool_name:
                        chapters = [pd["mahadasha"]]

        # For yoga tools: narrow by yoga type
        if "yogas" in context:
            yoga_names = context["yogas"]
            if isinstance(yoga_names, str):
                yoga_names = [yoga_names]

            yoga_specific = mapping.get("yoga_specific", {})
            narrowed = []
            for yoga_name in yoga_names:
                yoga_lower = yoga_name.lower().replace(" ", "_")
                for _category, spec in yoga_specific.items():
                    cat_keywords = spec.get("keywords", [])
                    if any(kw in yoga_lower for kw in cat_keywords):
                        narrowed.extend(spec.get("chapters", []))
            if narrowed:
                chapters = list(set(narrowed))

        # For dosha tools: narrow by dosha type
        if "doshas" in context:
            dosha_names = context["doshas"]
            if isinstance(dosha_names, str):
                dosha_names = [dosha_names]

            dosha_specific = mapping.get("dosha_specific", {})
            narrowed = []
            for dosha_name in dosha_names:
                dosha_lower = dosha_name.lower().replace(" ", "_")
                for _category, spec in dosha_specific.items():
                    cat_keywords = spec.get("keywords", [])
                    if any(kw in dosha_lower for kw in cat_keywords):
                        narrowed.extend(spec.get("chapters", []))
            if narrowed:
                chapters = list(set(narrowed))

        # For house tools: narrow by house number
        if "house" in context:
            house_num = str(context["house"])
            house_chapters = xref.get("house_chapters", {})
            if house_num in house_chapters:
                house_info = house_chapters[house_num]
                ch = house_info.get("chapter") if isinstance(house_info, dict) else house_info
                if ch:
                    chapters = [ch]

    return chapters


def _get_context_keywords(
    tool_name: str,
    context: dict[str, Any] | None = None,
) -> list[str]:
    """Build keyword list from tool name + context for section matching."""
    keywords = []

    if context:
        # Add planet names
        for key in ["mahadasha_lord", "antardasha_lord", "planet", "pratyantardasha_lord"]:
            if context.get(key):
                keywords.append(context[key].lower())

        # Add yoga/dosha names
        for key in ["yogas", "doshas"]:
            if key in context:
                names = context[key]
                if isinstance(names, str):
                    names = [names]
                for name in names:
                    keywords.extend(name.lower().replace("_", " ").split())

        # Add lagna
        if "lagna_rashi" in context:
            keywords.append(context["lagna_rashi"].lower())

    # Add tool-derived keywords
    tool_keywords = {
        "detect_yogas": ["yoga"],
        "detect_doshas": ["dosha"],
        "calculate_strength": ["strength", "bala"],
        "ashtakavarga": ["ashtakavarga", "rekha", "bindu"],
        "current_dasha": ["dasa", "dasha", "period"],
        "antardasha_effects": ["antardasa", "antardasha"],
        "pratyantardasha_effects": ["pratyantardasa", "pratyantardasha"],
        "transit_analysis": ["transit", "gochara"],
        "sade_sati_status": ["saturn", "sade sati"],
        "muhurta_check": ["muhurta", "auspicious"],
        "gem_recommendation": ["gem", "stone", "propitiation"],
        "recommend_chart_remedies": ["remedy", "propitiation", "shanti"],
        "kundali_matching": ["matching", "compatibility", "marriage"],
        "upapada_analysis": ["upapada", "marriage"],
        "chara_karakas": ["karaka", "atmakaraka"],
        "atmakaraka_analysis": ["atmakaraka", "karakamsa"],
        "prashna_analysis": ["prashna", "horary"],
    }
    keywords.extend(tool_keywords.get(tool_name, []))

    return keywords


def enrich_response(
    tool_name: str,
    response: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add BPHS references to any MCP tool response.

    This is the main entry point. Call this after computing a tool result
    to add authoritative BPHS chapter/verse references.

    Args:
        tool_name: MCP tool function name (e.g., "detect_yogas", "current_dasha")
        response: Original tool response dictionary
        context: Optional narrowing context. Supported keys:
            - "mahadasha_lord": planet name for dasha tools
            - "antardasha_lord": planet name for antardasha tools
            - "planet": planet name for general tools
            - "yogas": list of yoga names detected
            - "doshas": list of dosha names detected
            - "house": house number (1-12)
            - "lagna_rashi": ascendant sign name

    Returns:
        Response dict with added "bphs_references" list
    """
    try:
        chapters = _get_chapters_for_tool(tool_name, context)
        if not chapters:
            return response

        keywords = _get_context_keywords(tool_name, context)
        references = []

        for ch_num in chapters:
            if len(references) >= MAX_REFERENCES:
                break

            chapter_data = _load_bphs_chapter(ch_num)
            if not chapter_data:
                continue

            chapter_title = chapter_data.get("chapter_title", f"Chapter {ch_num}")

            # Extract relevant sections from this chapter
            sections = _extract_relevant_sections(
                chapter_data,
                keywords=keywords,
                max_sections=2 if len(chapters) > 3 else 3,
            )

            for section in sections:
                if len(references) >= MAX_REFERENCES:
                    break
                ref = _build_reference(
                    ch_num,
                    chapter_title,
                    section,
                    relevance=tool_name,
                )
                references.append(ref)

        if references:
            response["bphs_references"] = references
            response["bphs_chapters_cited"] = sorted({ref["chapter"] for ref in references})

        return response

    except Exception as e:
        logger.error(f"BPHS enrichment failed for {tool_name}: {e}")
        # Never break the tool response — return original on error
        return response


def get_bphs_chapters_for_tool(tool_name: str) -> list[dict[str, Any]]:
    """Get list of BPHS chapters relevant to a tool (for documentation/discovery).

    Returns:
        List of {"chapter": int, "title": str} for the given tool
    """
    xref = _load_cross_reference()
    tool_mappings = xref.get("tool_mappings", {})
    mapping = tool_mappings.get(tool_name, {})
    chapters = mapping.get("chapters", [])

    result = []
    for ch_num in chapters:
        chapter_data = _load_bphs_chapter(ch_num)
        title = (
            chapter_data.get("chapter_title", f"Chapter {ch_num}")
            if chapter_data
            else f"Chapter {ch_num}"
        )
        result.append({"chapter": ch_num, "title": title})

    return result


def get_tools_for_chapter(chapter_number: int) -> list[str]:
    """Get list of MCP tools that reference a given BPHS chapter.

    Returns:
        List of tool names
    """
    xref = _load_cross_reference()
    chapter_to_tools = xref.get("chapter_to_tools", {})
    return chapter_to_tools.get(str(chapter_number), [])


def clear_cache() -> None:
    """Clear all caches (useful for testing/reloading)."""
    _load_cross_reference.cache_clear()
    _load_bphs_chapter.cache_clear()
