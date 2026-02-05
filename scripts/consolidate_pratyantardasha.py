#!/usr/bin/env python3
"""
Consolidate all 9 Pratyantardasha MD files into a single master file.
729 combinations total (9 MD x 9 AD x 9 PD)

Handles multiple file formats from different generation agents.
"""

import json
from pathlib import Path

# Paths
RULES_DIR = Path(__file__).parent.parent / "knowledge" / "rules"

PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

# Mahadasha years
MD_YEARS = {
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "mercury": 17,
    "jupiter": 16,
    "venus": 20,
    "saturn": 19,
    "rahu": 18,
    "ketu": 7,
}

# Mahadasha files
MD_FILES = [
    ("sun", "pratyantardasha_sun_md.json"),
    ("moon", "pratyantardasha_moon_md.json"),
    ("mars", "pratyantardasha_mars_md.json"),
    ("mercury", "pratyantardasha_mercury_md.json"),
    ("jupiter", "pratyantardasha_jupiter_md.json"),
    ("venus", "pratyantardasha_venus_md.json"),
    ("saturn", "pratyantardasha_saturn_md.json"),
    ("rahu", "pratyantardasha_rahu_md.json"),
    ("ketu", "pratyantardasha_ketu_md.json"),
]


def extract_planet_name(key):
    """Extract planet name from various key formats."""
    key_lower = key.lower()
    for planet in PLANETS:
        if key_lower.startswith(planet):
            return planet
        if f"_{planet}" in key_lower:
            continue  # Check next planet
    # Try splitting
    parts = key_lower.replace("_antardasha", "").replace("_pratyantardasha", "").split("_")
    for part in parts:
        if part in PLANETS:
            return part
    return key_lower


def process_sun_moon_mars_format(data, md_key):
    """
    Format: {md}_mahadasha → {ad}_antardasha → {pd}_pratyantardasha
    """
    normalized = {}
    md_data = data.get(f"{md_key}_mahadasha", {})

    for ad_key, ad_data in md_data.items():
        if not isinstance(ad_data, dict):
            continue
        ad_name = extract_planet_name(ad_key)
        if ad_name not in PLANETS:
            continue

        normalized[ad_name] = {}
        for pd_key, pd_effects in ad_data.items():
            if isinstance(pd_effects, dict):
                pd_name = extract_planet_name(pd_key)
                if pd_name in PLANETS:
                    normalized[ad_name][pd_name] = pd_effects

    return normalized


def process_mercury_format(data):
    """
    Format: pratyantardasha → {ad}_{pd} keys with effects
    Example: "mercury_mercury" → effects dict
    """
    normalized = {}
    pd_data = data.get("pratyantardasha", {})

    for key, effects in pd_data.items():
        if not isinstance(effects, dict):
            continue
        parts = key.lower().split("_")
        if len(parts) >= 2:
            ad_name = parts[0]
            pd_name = parts[1] if len(parts) == 2 else parts[-1]
            if ad_name in PLANETS and pd_name in PLANETS:
                if ad_name not in normalized:
                    normalized[ad_name] = {}
                normalized[ad_name][pd_name] = effects

    return normalized


def process_jupiter_format(data):
    """
    Format: pratyantardasha_combinations → mix of {md}_{ad} and {md}_{ad}_{pd} keys
    Example: "jupiter_sun" (AD metadata) vs "jupiter_sun_moon" (PD effects)
    Only process 3-part keys as PD combinations
    """
    normalized = {}
    pc = data.get("pratyantardasha_combinations", {})

    for key, effects in pc.items():
        if not isinstance(effects, dict):
            continue
        parts = key.lower().split("_")
        # Only process 3-part keys (md_ad_pd), skip 2-part AD metadata keys
        if len(parts) == 3:
            ad_name = parts[1]
            pd_name = parts[2]
            if ad_name in PLANETS and pd_name in PLANETS:
                if ad_name not in normalized:
                    normalized[ad_name] = {}
                normalized[ad_name][pd_name] = effects

    return normalized


def process_venus_format(data):
    """
    Format: venus_antardasha list → each item has pratyantardasha list
    Each AD has antardasha like "Venus-Venus" and pratyantardasha list with pd_name
    """
    normalized = {}
    vad = data.get("venus_antardasha", [])

    for ad_item in vad:
        if not isinstance(ad_item, dict):
            continue
        # Handle "Venus-Venus" format - extract second part
        ad_raw = ad_item.get("antardasha", "")
        ad_name = ad_raw.split("-")[1].lower() if "-" in ad_raw else ad_raw.lower()

        if ad_name not in PLANETS:
            continue

        normalized[ad_name] = {}
        pd_data = ad_item.get("pratyantardasha", [])

        if isinstance(pd_data, list):
            for pd_item in pd_data:
                if isinstance(pd_item, dict):
                    # Venus uses pd_name like "Venus-Venus-Sun"
                    pd_raw = pd_item.get("pd_name", pd_item.get("lord", ""))
                    pd_name = pd_raw.split("-")[-1].lower() if "-" in pd_raw else pd_raw.lower()
                    if pd_name in PLANETS:
                        normalized[ad_name][pd_name] = pd_item
        elif isinstance(pd_data, dict):
            for pd_key, pd_effects in pd_data.items():
                pd_name = extract_planet_name(pd_key)
                if pd_name in PLANETS and isinstance(pd_effects, dict):
                    normalized[ad_name][pd_name] = pd_effects

    return normalized


def process_saturn_format(data):
    """
    Format: pratyantardashas → {md}_{ad}_{pd} flat keys
    Example: "saturn_saturn_saturn" → effects dict
    """
    normalized = {}
    pd_data = data.get("pratyantardashas", {})

    for key, effects in pd_data.items():
        if not isinstance(effects, dict):
            continue
        parts = key.lower().split("_")
        if len(parts) >= 3:
            ad_name = parts[1]
            pd_name = parts[2]
            if ad_name in PLANETS and pd_name in PLANETS:
                if ad_name not in normalized:
                    normalized[ad_name] = {}
                normalized[ad_name][pd_name] = effects

    return normalized


def process_rahu_format(data):
    """
    Format: pratyantardasha_combinations → {md}_{ad} keys, each with nested pratyantardasha dict
    The pratyantardasha dict has keys like "rahu_rahu_rahu" (md_ad_pd format)
    Example: "rahu_rahu" → {"pratyantardasha": {"rahu_rahu_rahu": effects, ...}}
    """
    normalized = {}
    pc = data.get("pratyantardasha_combinations", {})

    for ad_key, ad_data in pc.items():
        if not isinstance(ad_data, dict):
            continue
        parts = ad_key.lower().split("_")
        ad_name = parts[1] if len(parts) >= 2 else parts[0]
        if ad_name not in PLANETS:
            continue

        normalized[ad_name] = {}
        pd_container = ad_data.get("pratyantardasha", {})

        if isinstance(pd_container, dict):
            for pd_key, pd_effects in pd_container.items():
                # Keys are like "rahu_rahu_rahu" - extract 3rd part
                key_parts = pd_key.lower().split("_")
                pd_name = key_parts[2] if len(key_parts) >= 3 else extract_planet_name(pd_key)
                if pd_name in PLANETS and isinstance(pd_effects, dict):
                    normalized[ad_name][pd_name] = pd_effects
        elif isinstance(pd_container, list):
            for pd_item in pd_container:
                if isinstance(pd_item, dict):
                    pd_name = pd_item.get("lord", pd_item.get("pratyantardasha_lord", "")).lower()
                    if pd_name in PLANETS:
                        normalized[ad_name][pd_name] = pd_item

    return normalized


def process_ketu_format(data):
    """
    Format: antardasha_periods list → each has pratyantardashas list
    """
    normalized = {}
    periods = data.get("antardasha_periods", [])

    for ad_item in periods:
        if not isinstance(ad_item, dict):
            continue
        ad_name = ad_item.get("antardasha", "").lower()
        if ad_name not in PLANETS:
            continue

        normalized[ad_name] = {}
        pd_list = ad_item.get("pratyantardashas", [])

        if isinstance(pd_list, list):
            for pd_item in pd_list:
                if isinstance(pd_item, dict):
                    pd_name = pd_item.get("lord", pd_item.get("pratyantardasha", "")).lower()
                    if pd_name in PLANETS:
                        normalized[ad_name][pd_name] = pd_item
        elif isinstance(pd_list, dict):
            for pd_key, pd_effects in pd_list.items():
                pd_name = extract_planet_name(pd_key)
                if pd_name in PLANETS and isinstance(pd_effects, dict):
                    normalized[ad_name][pd_name] = pd_effects

    return normalized


def process_file(filepath, md_key):
    """Process a single MD file and return normalized data."""
    with Path(filepath).open() as f:
        data = json.load(f)

    # Try each format processor based on file structure
    if f"{md_key}_mahadasha" in data:
        return process_sun_moon_mars_format(data, md_key), "nested_md"
    elif "venus_antardasha" in data:
        return process_venus_format(data), "venus_list"
    elif "antardasha_periods" in data:
        return process_ketu_format(data), "ketu_list"
    elif "pratyantardashas" in data:
        return process_saturn_format(data), "flat_keys"
    elif "pratyantardasha_combinations" in data:
        # Could be Jupiter or Rahu format
        pc = data["pratyantardasha_combinations"]
        first_key = next(iter(pc.keys())) if pc else ""
        first_val = pc.get(first_key, {})
        if isinstance(first_val, dict) and "pratyantardasha" in first_val:
            return process_rahu_format(data), "rahu_nested"
        else:
            return process_jupiter_format(data), "jupiter_flat"
    elif "pratyantardasha" in data:
        return process_mercury_format(data), "mercury_dict"

    return {}, "unknown"


def count_combinations(normalized):
    """Count total PD combinations."""
    count = 0
    for ad_data in normalized.values():
        if isinstance(ad_data, dict):
            count += len(ad_data)
    return count


def main():
    master = {
        "metadata": {
            "description": "Complete Pratyantardasha effects for Vimshottari Dasha system",
            "total_combinations": 729,
            "structure": "9 Mahadashas x 9 Antardashas x 9 Pratyantardashas",
            "source": "BPHS, Phaladeepika, Traditional",
            "mahadasha_years": MD_YEARS,
        },
        "pratyantardasha_effects": {},
    }

    total_count = 0
    md_counts = {}

    for md_key, filename in MD_FILES:
        filepath = RULES_DIR / filename
        if not filepath.exists():
            print(f"✗ {md_key.upper():8} MD: {filename} not found!")
            continue

        normalized, format_type = process_file(filepath, md_key)
        count = count_combinations(normalized)

        if count > 0:
            master["pratyantardasha_effects"][md_key] = normalized
            md_counts[md_key] = count
            total_count += count
            status = "✓" if count == 81 else "?"
            print(f"{status} {md_key.upper():8} MD: {count:3} combinations ({format_type})")
        else:
            print(f"✗ {md_key.upper():8} MD: Could not extract PD data ({format_type})")

    # Update actual count
    master["metadata"]["actual_combinations"] = total_count
    master["metadata"]["combinations_by_md"] = md_counts
    master["metadata"]["completeness"] = f"{total_count}/729 ({100 * total_count / 729:.1f}%)"

    # Write master file
    output_path = RULES_DIR / "pratyantardasha_master.json"
    with output_path.open("w") as f:
        json.dump(master, f, indent=2)

    print(f"\n{'=' * 50}")
    print("PRATYANTARDASHA MASTER FILE CREATED")
    print(f"{'=' * 50}")
    print(f"Total combinations: {total_count}/729")
    print(f"Output: {output_path}")
    print(f"Size: {output_path.stat().st_size:,} bytes")

    # Show which MDs are incomplete
    incomplete = [md for md, cnt in md_counts.items() if cnt < 81]
    if incomplete:
        print(f"\nIncomplete MDs: {', '.join(incomplete)}")


if __name__ == "__main__":
    main()
