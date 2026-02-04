# 108 Patterns MCP Server

The Patterns MCP Server provides yoga detection, dosha detection, and planetary strength calculation tools for the 108 Vedic Astrology application via the Model Context Protocol (MCP).

## Overview

The server exposes four main tools:

1. **detect_yogas** - Identify auspicious planetary combinations (yogas)
2. **detect_doshas** - Identify afflictions and karmic challenges (doshas)
3. **calculate_strength** - Compute Shadbala (six-fold planetary strength)
4. **ashtakavarga** - Calculate Ashtakavarga (benefic influence analysis)

## Installation and Running

### Start the Server

```bash
# From project root
uv run python -m services.mcp.patterns
```

The server will start on stdin/stdout and wait for MCP protocol messages.

### Configuration

The server is configured in `.mcp.json`:

```json
{
  "patterns": {
    "command": "uv",
    "args": ["run", "python", "-m", "services.mcp.patterns"],
    "env": {
      "PYTHONPATH": "packages"
    }
  }
}
```

## Tools

### 1. detect_yogas

Detects all yogas (auspicious planetary combinations) present in a birth chart.

**Parameters:**
- `planets` (Dict): Planet positions with format:
  ```python
  {
    "sun": {
      "longitude": 52.5,
      "sign": "taurus",
      "house": 10,
      "rashi": 1,
      "is_retrograde": false
    },
    ...
  }
  ```
- `lagna_rashi` (str): Ascendant sign (e.g., "libra", "aries")
- `moon_rashi` (str, optional): Moon sign for additional calculations
- `houses` (Dict, optional): House cusps data

**Returns:**
```python
{
  "lagna": "libra",
  "total_yogas_found": 5,
  "yogas": [
    {
      "id": "pancha_mahapurusha_ruchaka",
      "name": "Ruchaka Yoga",
      "category": "pancha_mahapurusha",
      "is_present": True,
      "strength": 0.85,
      "involved_planets": ["mars"],
      "description": "Mars in a Kendra from the Lagna...",
      "effects": ["Courage", "Leadership", "Strength"],
      "cancellation": None
    }
  ],
  "categories": {
    "pancha_mahapurusha": 2,
    "raja_yoga": 3
  },
  "success": True
}
```

**Detected Yoga Categories:**
- Pancha Mahapurusha Yogas (5 great-person yogas)
- Raja Yogas (royal combinations)
- Dhana Yogas (wealth combinations)
- Parivartan Yogas (exchange yogas)
- Chandra Mangala Yoga
- Gajakesari Yoga
- Neech Bhanga Yoga (debilitation cancellation)
- And more...

### 2. detect_doshas

Detects doshas (afflictions and karmic challenges) in a birth chart.

**Parameters:**
- `planets` (Dict): Planet positions
- `lagna_rashi` (str): Ascendant sign
- `moon_rashi` (str, optional): Moon sign for Mangal Dosha from Moon
- `venus_rashi` (str, optional): Venus sign for Mangal Dosha from Venus
- `houses` (Dict, optional): House cusps data

**Returns:**
```python
{
  "lagna": "libra",
  "total_doshas_found": 1,
  "doshas": [
    {
      "id": "mangal_dosha",
      "name": "Mangal Dosha",
      "is_present": True,
      "severity": "moderate",
      "involved_planets": ["mars"],
      "description": "Mars affliction in marriage houses...",
      "effects": ["Marital challenges", "Delayed marriage"],
      "remedies": ["Worshipping Mars", "Reciting Hanuman Chalisa"],
      "cancellation": None
    }
  ],
  "has_mangal_dosha": True,
  "has_kaal_sarp": False,
  "success": True
}
```

**Detected Doshas:**
- Mangal Dosha (Mars affliction) - from Lagna, Moon, and Venus
- Kaal Sarp Dosha (Rahu-Ketu axis) - 12 types based on Rahu position
- Pitra Dosha (ancestral karma)
- Grahan Dosha (eclipse shadow)
- Guru Chandal Dosha (Jupiter-Rahu affliction)
- Daridra Yoga (poverty combinations)

### 3. calculate_strength

Computes Shadbala (six-fold strength) for a planet.

**Parameters:**
- `planet` (str): Planet name (sun, moon, mars, mercury, jupiter, venus, saturn)
- `longitude` (float): Sidereal longitude (0-360)
- `house` (int): House number (1-12)
- `sign` (str): Sign name (aries, taurus, gemini, etc.)
- `is_retrograde` (bool, optional): Whether planet is retrograde

**Returns:**
```python
{
  "planet": "jupiter",
  "longitude": 136.24,
  "house": 12,
  "sign": "virgo",
  "is_retrograde": False,
  "dignity": "debilitated",
  "shadbala": {
    "sthana_bala": 45.0,
    "dig_bala": 30.0,
    "kala_bala": 35.0,
    "chesta_bala": 40.0,
    "naisargika_bala": 34.29,
    "drik_bala": 25.0,
    "total": 209.29
  },
  "total_strength": 209.29,
  "is_strong": False,
  "strength_rating": "moderate",
  "success": True
}
```

**Shadbala Components:**
- **Sthana Bala** (60 max): Positional strength in own sign, exaltation, friendly signs
- **Dig Bala** (60 max): Directional strength in its strong houses
- **Kala Bala** (60 max): Temporal strength (day/night, annual, monthly, weekly)
- **Chesta Bala** (60 max): Motional strength (retrograde vs direct motion)
- **Naisargika Bala** (varies): Natural strength inherent to each planet
- **Drik Bala** (60 max): Aspectual strength from conjunctions and aspects

**Strength Ratings:**
- `very_strong`: >= 400
- `strong`: >= 300
- `moderate`: >= 200
- `weak`: >= 100
- `very_weak`: < 100

### 4. ashtakavarga

Calculates Ashtakavarga (benefic influence bindus) for all planets.

**Parameters:**
- `planets` (Dict): Planet positions with signs
- `lagna_rashi` (str): Ascendant sign

**Returns:**
```python
{
  "planets": {
    "sun": {
      "bindus_by_sign": [8, 7, 6, 5, 7, 8, 6, 5, 7, 8, 6, 5],
      "total_bindus": 83
    },
    "mars": {
      "bindus_by_sign": [7, 6, 5, 6, 7, 8, 5, 6, 7, 8, 6, 7],
      "total_bindus": 84
    }
  },
  "sarvashtakavarga": [52, 48, 45, 47, 51, 50, 46, 48, 51, 52, 48, 50],
  "sarvashtakavarga_with_signs": {
    "Aries": 52,
    "Taurus": 48,
    ...
  },
  "success": True
}
```

**Ashtakavarga Rules:**
- Each planet contributes 0-8 bindus per sign
- Rules based on planetary aspects and positions
- Sarvashtakavarga (SAV) = sum of all planet bindus for each sign
- Max bindus per sign = 56 (7 planets × 8 bindus)
- Higher bindus indicate favorable planetary influence

**Interpretation:**
- Signs with 30+ bindus: Very strong
- Signs with 25-29 bindus: Strong
- Signs with 20-24 bindus: Moderate
- Signs with <20 bindus: Weak

## Data Format Reference

### Planet Position Format
```python
{
  "planet_name": {
    "longitude": float,      # 0-360 degrees
    "sign": str,            # "aries" to "pisces"
    "house": int,           # 1-12
    "rashi": int,           # 0-11 (optional)
    "rashi_degree": float,  # 0-30 (optional)
    "nakshatra": str,       # (optional)
    "nakshatra_pada": int,  # 1-4 (optional)
    "nakshatra_lord": str,  # (optional)
    "latitude": float,      # (optional)
    "speed": float,         # (optional)
    "is_retrograde": bool   # (optional)
  }
}
```

### Sign Names (Case-insensitive)
- "aries", "taurus", "gemini", "cancer", "leo", "virgo"
- "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"

### Planet Names
- "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"
- "rahu", "ketu" (shadow planets)

## Error Handling

All tools return a `success` field indicating success/failure:

```python
{
  "error": "Invalid planet: xyz",
  "type": "ValueError",
  "success": False
}
```

Common error types:
- `ValueError`: Invalid planet or sign name
- `KeyError`: Missing required data
- `Exception`: General calculation errors

## Examples

### Example 1: Detect Yogas in a Chart

```python
planets = {
    "sun": {
        "longitude": 52.5,
        "sign": "taurus",
        "house": 10,
        "is_retrograde": False
    },
    "mars": {
        "longitude": 139.5,
        "sign": "leo",
        "house": 1,
        "is_retrograde": False
    },
    "jupiter": {
        "longitude": 286.5,
        "sign": "capricorn",
        "house": 7,
        "is_retrograde": False
    }
}

result = detect_yogas(planets, "libra", "gemini")
# Returns yoga detections including Pancha Mahapurusha yogas
```

### Example 2: Check Mangal Dosha

```python
result = detect_doshas(
    planets,
    lagna_rashi="libra",
    moon_rashi="gemini",
    venus_rashi="taurus"
)

if result["has_mangal_dosha"]:
    for dosha in result["doshas"]:
        if dosha["id"] == "mangal_dosha":
            print(f"Severity: {dosha['severity']}")
            print(f"Remedies: {dosha['remedies']}")
```

### Example 3: Calculate Jupiter's Strength

```python
result = calculate_strength(
    planet="jupiter",
    longitude=136.24,
    house=12,
    sign="virgo",
    is_retrograde=False
)

print(f"Jupiter Strength: {result['strength_rating']}")
print(f"Total Shadbala: {result['total_strength']}")
```

### Example 4: Analyze Ashtakavarga

```python
result = ashtakavarga(planets, "libra")

for sign_name, bindus in result["sarvashtakavarga_with_signs"].items():
    if bindus >= 30:
        print(f"{sign_name}: Very Strong ({bindus} bindus)")
```

## Technical Details

### Dependencies
- `mcp.server.fastmcp`: FastMCP framework for protocol handling
- `packages.core.src`: Core models and enums (Planet, Rashi, BirthChart, etc.)
- `packages.self.src`: Pattern detection modules (YogaDetector, DoshaDetector, StrengthCalculator)
- `packages.cosmos.src`: Ephemeris calculations (if needed for validation)

### Key Classes
- **YogaDetector**: Detects yogas from birth chart data
- **DoshaDetector**: Identifies doshas and afflictions
- **StrengthCalculator**: Computes Shadbala and Ashtakavarga

### Design Notes
- The server creates minimal BirthChart objects internally for detection
- All calculations use sidereal zodiac (Lahiri ayanamsa by default)
- House systems are assumed to be Placidus if not specified
- Results include both technical (Shadbala components) and interpretive data (effects, remedies)

## Integration with 108 System

This server integrates with:
- **Ephemeris Server**: Uses planetary positions calculated by ephemeris tools
- **Knowledge Server**: Provides detailed interpretations of detected patterns
- **Memory Server**: Stores and retrieves user chart analyses
- **Biorhythm Server**: Timing information for dosha remedies

## Maintenance and Updates

### Adding New Yogas
Yogas are defined in the `packages.self.src.yoga_detector` module. Add new yoga rules to the YAML configuration.

### Customizing Strength Calculations
Modify `packages.self.src.strength.py` to adjust Shadbala or Ashtakavarga calculations.

### Extending Dosha Detection
Update `packages.self.src.dosha_detector.py` to add new dosha types or modify detection rules.

## References

- BPHS (Brihat Parasara Hora Sastra) - Classical Vedic astrology text
- Phaladeepa - Traditional commentary on planetary effects
- Jataka Bharata - Comprehensive yogas reference
- Saravali - Advanced yoga combinations
