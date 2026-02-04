# Gochara (Transit) Analysis Module Guide

## Overview

The Transits module provides comprehensive planetary transit analysis based on Vedic astrology principles. It calculates how current transiting planets affect the native's natal Moon position and life circumstances.

## Module Location

```
packages/context/src/transits.py
```

## Key Concepts

### 1. Gochara (Transit Analysis)

Gochara means "movement" and refers to the current position of planets as they transit through the zodiac. The Gochara system evaluates planetary transits relative to the **natal Moon's position**, which is the primary reference point.

**Key Points:**
- All transit analysis is calculated from the natal Moon
- Planets are assessed in houses 1-12 relative to the Moon
- Favorable and unfavorable houses vary by planet
- Vedha (obstruction) can reduce beneficial effects

### 2. Sade Sati (7.5-Year Saturn Cycle)

Sade Sati is the most significant Saturn transit, occurring when Saturn passes through three houses relative to the natal Moon:

| Phase | Duration | Saturn Position | Characteristics |
|-------|----------|-----------------|-----------------|
| Rising | ~2.5 years | 12th from Moon | Mental stress, financial pressure, hidden enemies |
| Peak | ~2.5 years | 1st from Moon (conjunct) | Maximum challenges, health concerns, emotional turbulence |
| Setting | ~2.5 years | 2nd from Moon | Financial issues, gradual relief, family problems |

**Example:**
```python
from packages.context.src.transits import check_sade_sati

# User with Aquarius Moon (index 10)
# Saturn in Pisces (index 11) = 2nd from Moon
result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=11)

# Result:
# {
#   "active": True,
#   "phase": "setting",
#   "house_from_moon": 2,
#   "description": "Sade Sati - Setting Phase...",
#   "effects": ["Financial concerns...", ...],
#   "duration_years": 2.5,
#   "remedies": ["Continue Saturn worship...", ...]
# }
```

### 3. Dhaiya (Kantaka Shani / Ashtama Shani)

Dhaiya occurs when Saturn is in the 4th or 8th house from the natal Moon. Each phase lasts approximately 2.5 years.

| Type | Saturn Position | Effects |
|------|-----------------|---------|
| Kantaka Shani | 4th from Moon | Domestic troubles, vehicle problems, mother's health |
| Ashtama Shani | 8th from Moon | Sudden obstacles, health issues, accidents, hidden problems |

**Example:**
```python
from packages.context.src.transits import check_dhaiya

# Saturn in 4th from Moon
result = check_dhaiya(natal_moon_rashi=10, saturn_rashi=1)

# Result:
# {
#   "active": True,
#   "type": "kantaka_shani",
#   "house_from_moon": 4,
#   "description": "Kantaka Shani (Saturn in 4th from Moon)...",
#   "effects": ["Domestic troubles...", "Vehicle problems...", ...]
# }
```

### 4. Vedha (Obstruction)

Vedha occurs when a benefic planet is in a favorable position but another planet occupies the "vedha house," obstructing the good results.

**Example:**
```python
from packages.context.src.transits import get_gochara

# Jupiter in 5th from Moon (favorable position)
# But Saturn in 4th from Moon (vedha point for Jupiter in 5th)
transit_positions = {
    "jupiter": 2,   # 5th from Moon (10)
    "saturn": 1,    # 4th from Moon (vedha point)
}

result = get_gochara(
    natal_moon_rashi=10,
    transit_planet="jupiter",
    transit_rashi=2,
    all_transit_rashis=transit_positions
)

# Result:
# {
#   "planet": "jupiter",
#   "house_from_moon": 5,
#   "is_favorable": True,
#   "has_vedha": True,
#   "vedha_by": "saturn",
#   "net_effect": "unfavorable",  # Good position blocked by vedha
#   "effects": [...]
# }
```

## API Functions

### Primary Analysis Functions

#### 1. `check_sade_sati(natal_moon_rashi, saturn_rashi)`

Detects if Sade Sati is active and identifies the phase.

**Parameters:**
- `natal_moon_rashi` (int): Natal Moon's rashi (0-11, where 0=Aries, 11=Pisces)
- `saturn_rashi` (int): Current Saturn's rashi (0-11)

**Returns:**
```python
{
    "active": bool,
    "phase": str|None,  # "rising", "peak", "setting", or None
    "house_from_moon": int,  # 1-12
    "description": str,
    "effects": list[str],
    "duration_years": float|None,
    "remedies": list[str]
}
```

#### 2. `check_dhaiya(natal_moon_rashi, saturn_rashi)`

Detects if Dhaiya is active.

**Parameters:**
- `natal_moon_rashi` (int): Natal Moon's rashi (0-11)
- `saturn_rashi` (int): Current Saturn's rashi (0-11)

**Returns:**
```python
{
    "active": bool,
    "type": str|None,  # "kantaka_shani" or "ashtama_shani"
    "house_from_moon": int,  # 1-12
    "description": str,
    "effects": list[str],
    "duration_years": float|None,
    "remedies": list[str]
}
```

#### 3. `get_gochara(natal_moon_rashi, transit_planet, transit_rashi, all_transit_rashis=None)`

Analyzes a single planet's transit effect.

**Parameters:**
- `natal_moon_rashi` (int): Natal Moon's rashi (0-11)
- `transit_planet` (str): Planet name (lowercase: "sun", "moon", "mars", etc.)
- `transit_rashi` (int): Transit planet's current rashi (0-11)
- `all_transit_rashis` (dict, optional): All planet positions for vedha analysis

**Returns:**
```python
{
    "planet": str,
    "transit_sign": int,
    "house_from_moon": int,  # 1-12
    "is_favorable": bool,
    "has_vedha": bool,
    "vedha_by": str|None,
    "net_effect": str,  # "favorable" or "unfavorable"
    "effects": list[str]
}
```

#### 4. `get_full_transit_analysis(natal_moon_rashi, transit_positions)`

Complete analysis of all transiting planets.

**Parameters:**
- `natal_moon_rashi` (int): Natal Moon's rashi (0-11)
- `transit_positions` (dict): All planet positions {planet_name: rashi}

**Returns:**
```python
{
    "natal_moon_sign": int,
    "sade_sati": dict,  # Sade Sati analysis
    "dhaiya": dict,      # Dhaiya analysis
    "planet_transits": dict,  # Individual planet analyses
    "summary": {
        "favorable_count": int,
        "unfavorable_count": int,
        "total_planets_analyzed": int,
        "overall_trend": str,  # "highly_favorable", "favorable", "mixed", etc.
        "saturn_active": bool
    }
}
```

### Helper Functions

#### 1. `get_transiting_planet_house(natal_moon_rashi, transit_planet, transit_rashi)`

Get house position of a transiting planet from natal Moon.

#### 2. `is_planet_favorable_in_house(planet, house_from_moon)`

Check if a planet is in a naturally favorable house.

#### 3. `validate_transit_data(natal_moon_rashi, transit_positions)`

Validate transit data for correctness.

**Returns:** `(bool, str)` - (is_valid, error_message)

## Constants

### GOCHARA_FAVORABLE

Maps each planet to its favorable houses from the Moon:

```python
GOCHARA_FAVORABLE = {
    "sun": [3, 6, 10, 11],
    "moon": [1, 3, 6, 7, 10, 11],
    "mars": [3, 6, 11],
    "mercury": [2, 4, 6, 8, 10, 11],
    "jupiter": [2, 5, 7, 9, 11],
    "venus": [1, 2, 3, 4, 5, 8, 9, 11, 12],
    "saturn": [3, 6, 11],
    "rahu": [3, 6, 10, 11],
    "ketu": [3, 6, 10, 11],
}
```

### VEDHA_POINTS

Maps favorable positions to their vedha (obstruction) houses:

```python
VEDHA_POINTS = {
    "sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    # ... (see source for complete mapping)
}
```

### TRANSIT_EFFECTS

Maps each planet to effects in each house from the Moon.

## Rashi Reference (0-indexed)

```
0  = Aries (Mesha)
1  = Taurus (Vrishabha)
2  = Gemini (Mithuna)
3  = Cancer (Karka)
4  = Leo (Simha)
5  = Virgo (Kanya)
6  = Libra (Tula)
7  = Scorpio (Vrischika)
8  = Sagittarius (Dhanu)
9  = Capricorn (Makara)
10 = Aquarius (Kumbha)
11 = Pisces (Meena)
```

## Usage Examples

### Complete Example: Aquarius Moon Native

```python
from packages.context.src.transits import get_full_transit_analysis, check_sade_sati

# Native with Aquarius Moon (10)
natal_moon = 10

# Current transit positions
transit_positions = {
    "sun": 0,       # Aries
    "moon": 2,      # Gemini
    "mars": 3,      # Cancer
    "mercury": 4,   # Leo
    "jupiter": 5,   # Virgo
    "venus": 6,     # Libra
    "saturn": 11,   # Pisces (2nd from Moon - Sade Sati setting)
    "rahu": 7,      # Scorpio
    "ketu": 8,      # Sagittarius
}

# Get full analysis
analysis = get_full_transit_analysis(natal_moon, transit_positions)

print(f"Sade Sati Active: {analysis['sade_sati']['active']}")
print(f"Phase: {analysis['sade_sati']['phase']}")
print(f"Overall Trend: {analysis['summary']['overall_trend']}")
print(f"Favorable Planets: {analysis['summary']['favorable_count']}")
print(f"Unfavorable Planets: {analysis['summary']['unfavorable_count']}")

# Detailed planet analysis
for planet, gochara in analysis['planet_transits'].items():
    effect = gochara['net_effect']
    house = gochara['house_from_moon']
    print(f"\n{planet.upper()} (House {house}): {effect}")
    if gochara['has_vedha']:
        print(f"  Obstructed by: {gochara['vedha_by']}")
    for eff in gochara['effects'][:2]:
        print(f"  - {eff}")
```

## Important Notes

### 1. Moon as Reference Point
All transit analysis is relative to the **natal Moon**, not the Ascendant. This is the standard Gochara system.

### 2. Rashi Calculation
House from Moon = ((transit_rashi - natal_moon_rashi) % 12) + 1

This ensures houses are numbered 1-12, where 1 = same sign as Moon.

### 3. Vedha Exception
Sun and Saturn do NOT cause vedha to each other. This is a special rule in the Vedha system.

### 4. Saturn Effects
Saturn is best placed in houses 3, 6, and 11 from the Moon. When in unfavorable positions, Saturn brings delays, obstacles, and challenges.

### 5. Venus Favorable Houses
Venus has the most favorable houses (9 out of 12), making it generally beneficial in most transit positions except 6, 7, and 10.

## Integration with Other Modules

The Transits module works with:

1. **Dasha Module** - Understand current dasha period alongside transits
2. **Ephemeris Data** - Requires accurate planetary positions
3. **Yoga Detection** - Combine with yogas for comprehensive analysis

## Error Handling

The module includes validation:

```python
from packages.context.src.transits import validate_transit_data

is_valid, message = validate_transit_data(
    natal_moon_rashi=10,
    transit_positions={"sun": 0, "moon": 1}
)

if not is_valid:
    print(f"Error: {message}")
```

## Performance Considerations

- All calculations are O(n) where n = number of planets
- Vedha check is O(n²) in worst case (checking all planets against vedha houses)
- For typical 9-planet analysis, computational cost is negligible

## References

- Classical texts: Phaladeepika, Jataka Parijata
- Transit house significance is crucial for predictive astrology
- Sade Sati is one of the most feared periods in natal astrology
- Vedha obstruction principles are from classical Hora Shastras

## Future Enhancements

1. Retrograde planet special handling
2. Conjunction and aspect calculations
3. Transit speed analysis (fast/slow movers)
4. Vimshottari dasha correlation with transits
5. Progressed chart analysis
