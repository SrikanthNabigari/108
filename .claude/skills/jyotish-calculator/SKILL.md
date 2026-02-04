---
name: jyotish-calculator
description: Calculate Vedic astrology positions including planets, houses, nakshatras, and divisional charts using Swiss Ephemeris
triggers:
  - calculate
  - planetary positions
  - birth chart
  - houses
  - nakshatra
  - dasha
  - transit
globs:
  - "packages/cosmos/**/*.py"
  - "knowledge/definitions/*.json"
---

# Jyotish Calculator Skill

You are an expert in Vedic astrology calculations using Swiss Ephemeris (pyswisseph).

## Core Concepts

### Ayanamsa
Always use **Lahiri ayanamsa** (default) for sidereal calculations:
```python
import swisseph as swe
swe.set_sid_mode(swe.SIDM_LAHIRI)
```

### The 9 Grahas (Planets)
```python
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,  # True node: swe.TRUE_NODE
    "Ketu": None  # Calculate as Rahu + 180°
}
```

### The 12 Rashis (Signs)
```python
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
```

### The 27 Nakshatras
Each nakshatra spans 13°20' (800 minutes). Each has 4 padas of 3°20'.

```python
def get_nakshatra(longitude: float) -> tuple[str, int]:
    """Get nakshatra name and pada from longitude."""
    nakshatra_span = 360 / 27  # 13.333...
    pada_span = nakshatra_span / 4  # 3.333...

    nakshatra_index = int(longitude / nakshatra_span)
    position_in_nakshatra = longitude % nakshatra_span
    pada = int(position_in_nakshatra / pada_span) + 1

    return NAKSHATRAS[nakshatra_index], pada
```

## Calculation Patterns

### Julian Day Conversion
```python
from datetime import datetime

def to_julian_day(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    return swe.julday(
        dt.year, dt.month, dt.day,
        dt.hour + dt.minute/60 + dt.second/3600
    )
```

### Planet Position
```python
def get_planet_position(planet_id: int, jd: float) -> dict:
    """Get sidereal position of a planet."""
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    result = swe.calc_ut(jd, planet_id, flags)

    longitude = result[0][0]
    speed = result[0][3]

    rashi_index = int(longitude / 30)
    degree_in_sign = longitude % 30

    return {
        "longitude": longitude,
        "rashi": RASHIS[rashi_index],
        "degree": degree_in_sign,
        "is_retrograde": speed < 0,
        "nakshatra": get_nakshatra(longitude)
    }
```

### House Calculation
```python
def get_houses(jd: float, lat: float, lon: float) -> dict:
    """Calculate house cusps using Placidus."""
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')  # P = Placidus

    return {
        "ascendant": ascmc[0],
        "mc": ascmc[1],
        "cusps": list(cusps)
    }
```

### Vimshottari Dasha
```python
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
    "Mars": 7, "Rahu": 18, "Jupiter": 16,
    "Saturn": 19, "Mercury": 17
}

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars",
               "Rahu", "Jupiter", "Saturn", "Mercury"]

def get_dasha_lord(moon_nakshatra: str) -> str:
    """Get starting dasha lord from birth nakshatra."""
    nakshatra_to_lord = {
        "Ashwini": "Ketu", "Magha": "Ketu", "Mula": "Ketu",
        "Bharani": "Venus", "Purva Phalguni": "Venus", "Purva Ashadha": "Venus",
        # ... complete mapping
    }
    return nakshatra_to_lord[moon_nakshatra]
```

## File Locations

- **Calculation code**: `packages/cosmos/src/`
- **Planet definitions**: `knowledge/definitions/planets.json`
- **Nakshatra definitions**: `knowledge/definitions/nakshatras.json`
- **Rashi definitions**: `knowledge/definitions/rashis.json`

## Testing Calculations

Always verify calculations against known ephemeris data:
```python
def test_sun_position():
    """Test Sun position for known date."""
    jd = swe.julday(2000, 1, 1, 12.0)
    pos = get_planet_position(swe.SUN, jd)
    assert 255 < pos["longitude"] < 260  # Should be in Sagittarius
```

## Common Pitfalls

1. **Always set ayanamsa** before calculations
2. **Ketu is Rahu + 180°** (not a separate calculation)
3. **Use UTC** for all Julian day conversions
4. **Close ephemeris** after calculations: `swe.close()`
