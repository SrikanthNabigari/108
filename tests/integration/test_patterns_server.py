#!/usr/bin/env python
"""
Quick test of the patterns_server functionality.
This validates that all tools are properly defined and importable.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.mcp.patterns_server import (  # noqa: E402
    ashtakavarga,
    calculate_strength,
    detect_doshas,
    detect_yogas,
)


def test_detect_yogas():
    """Test yoga detection with sample data."""
    planets = {
        "sun": {
            "longitude": 52.5,
            "sign": "taurus",
            "house": 10,
            "rashi": 1,
            "is_retrograde": False,
        },
        "mars": {"longitude": 139.5, "sign": "leo", "house": 1, "rashi": 4, "is_retrograde": False},
        "jupiter": {
            "longitude": 286.5,
            "sign": "capricorn",
            "house": 7,
            "rashi": 9,
            "is_retrograde": False,
        },
        "moon": {
            "longitude": 102.5,
            "sign": "gemini",
            "house": 12,
            "rashi": 2,
            "is_retrograde": False,
        },
        "mercury": {
            "longitude": 35.5,
            "sign": "aries",
            "house": 9,
            "rashi": 0,
            "is_retrograde": False,
        },
        "venus": {
            "longitude": 325.5,
            "sign": "pisces",
            "house": 8,
            "rashi": 11,
            "is_retrograde": False,
        },
        "saturn": {
            "longitude": 245.5,
            "sign": "sagittarius",
            "house": 6,
            "rashi": 8,
            "is_retrograde": False,
        },
    }

    result = detect_yogas(planets, "libra", "gemini")
    print("✓ detect_yogas executed successfully")
    print(f"  - Found {result.get('total_yogas_found', 0)} yogas")
    print(f"  - Success: {result.get('success', False)}")
    if result.get("error"):
        print(f"  - Error: {result['error']}")
    return result


def test_detect_doshas():
    """Test dosha detection with sample data."""
    planets = {
        "sun": {"sign": "taurus", "longitude": 52.5, "house": 10},
        "mars": {"sign": "leo", "longitude": 139.5, "house": 1},
        "jupiter": {"sign": "capricorn", "longitude": 286.5, "house": 7},
        "moon": {"sign": "gemini", "longitude": 102.5, "house": 12},
        "mercury": {"sign": "aries", "longitude": 35.5, "house": 9},
        "venus": {"sign": "pisces", "longitude": 325.5, "house": 8},
        "saturn": {"sign": "sagittarius", "longitude": 245.5, "house": 6},
    }

    result = detect_doshas(planets, lagna_rashi="libra", moon_rashi="gemini", venus_rashi="pisces")
    print("✓ detect_doshas executed successfully")
    print(f"  - Found {result.get('total_doshas_found', 0)} doshas")
    print(f"  - Has Mangal Dosha: {result.get('has_mangal_dosha', False)}")
    print(f"  - Has Kaal Sarp: {result.get('has_kaal_sarp', False)}")
    print(f"  - Success: {result.get('success', False)}")
    if result.get("error"):
        print(f"  - Error: {result['error']}")
    return result


def test_calculate_strength():
    """Test Shadbala calculation."""
    result = calculate_strength(
        planet="jupiter", longitude=286.5, house=7, sign="capricorn", is_retrograde=False
    )
    print("✓ calculate_strength executed successfully")
    print(f"  - Planet: {result.get('planet', 'unknown')}")
    print(f"  - Strength Rating: {result.get('strength_rating', 'unknown')}")
    print(f"  - Total Strength: {result.get('total_strength', 'unknown')}")
    print(f"  - Is Strong: {result.get('is_strong', False)}")
    print(f"  - Success: {result.get('success', False)}")
    if result.get("error"):
        print(f"  - Error: {result['error']}")
    return result


def test_ashtakavarga():
    """Test Ashtakavarga calculation."""
    planets = {
        "sun": {"sign": "taurus", "longitude": 52.5},
        "mars": {"sign": "leo", "longitude": 139.5},
        "jupiter": {"sign": "capricorn", "longitude": 286.5},
        "moon": {"sign": "gemini", "longitude": 102.5},
        "mercury": {"sign": "aries", "longitude": 35.5},
        "venus": {"sign": "pisces", "longitude": 325.5},
        "saturn": {"sign": "sagittarius", "longitude": 245.5},
    }

    result = ashtakavarga(planets, "libra")
    print("✓ ashtakavarga executed successfully")
    print(f"  - Planets analyzed: {list(result.get('planets', {}).keys())}")
    print(f"  - Sarvashtakavarga signs: {len(result.get('sarvashtakavarga', []))}")
    print(f"  - Success: {result.get('success', False)}")
    if result.get("error"):
        print(f"  - Error: {result['error']}")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Testing 108 Patterns MCP Server")
    print("=" * 60)

    try:
        print("\n1. Testing detect_yogas...")
        test_detect_yogas()

        print("\n2. Testing detect_doshas...")
        test_detect_doshas()

        print("\n3. Testing calculate_strength...")
        test_calculate_strength()

        print("\n4. Testing ashtakavarga...")
        test_ashtakavarga()

        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
