# Planetary Strength Calculations Module

## Overview

The `strength.py` module implements comprehensive planetary strength calculations for the 108 Vedic Astrology system, including:

1. **Shadbala** (Six-fold Strength)
2. **Ashtakavarga** (Eight-fold Classification)
3. **Sarvashtakavarga** (Total Strength)
4. **Planet Dignity** Classification

## Shadbala (Six-fold Strength)

Shadbala measures the overall strength of a planet across six dimensions. Each component is measured in virupas (60 virupas = 1 full strength unit).

### 1. Sthana Bala (Positional Strength)

Measures a planet's strength based on its position in the chart.

**Components:**
- **Uchcha Bala** (0-60): Strength from exaltation
  - Maximum at exact exaltation degree
  - Zero at debilitation (180° opposite)
  - 30 points in neutral positions
  
- **Saptavargaja Bala**: Strength in 7 divisional charts
  - D1 (Rashi), D2 (Hora), D3 (Drekkana)
  - D7 (Saptamsha), D9 (Navamsha)
  - D12 (Dwadasamsha), D24 (Chaturvimshamsha)
  
- **Ojhayugmarasyamsa Bala**: Odd/even sign placement
  - Generally beneficial in odd signs (7.5) vs even signs (5.0)
  
- **Kendradi Bala** (House Placement)
  - Kendra (1, 4, 7, 10): 60 points (angular houses)
  - Panapara (2, 5, 8, 11): 30 points (succeedent)
  - Apoklima (3, 6, 9, 12): 15 points (cadent)
  
- **Drekkana Bala**: Decanate placement
  - Each sign divided into 3 decanates (10° each)
  - 10 points for favorable placement

### 2. Dig Bala (Directional Strength)

Measures planetary strength based on directional placement.

**Strong Directions (60 points max):**
- Jupiter & Mercury: East (1st house/Lagna)
- Sun & Mars: South (10th house/MC)
- Saturn: West (7th house)
- Moon & Venus: North (4th house)

**Formula:**
```
Dig Bala = 60 × (1 - distance_from_strong_house / 180°)
```

### 3. Kala Bala (Temporal Strength)

Measures planetary strength based on time factors.

**Components:**
- **Nathonnatha Bala**: Day/night strength
  - Sun & Mars: strong during day (15 points)
  - Moon & Venus: strong during night (15 points)
  - Others: 10 points
  
- **Paksha Bala**: Lunar phase strength
  - Moon strongest during waxing (Shukla) phase
  - Other planets modulated by lunar phase
  
- **Ayana Bala**: Declination strength
  - Based on planet's latitude/declination
  - 5 points (simplified)
  
- **Varsha/Masa/Dina/Hora Bala**: Year/month/day/hour lords
- **Tribhaga Bala**: Three parts of day/night

### 4. Chesta Bala (Motional Strength)

Measures strength based on planet's motion.

**Motion States (0-60):**
- Retrograde: 60 points (high strength)
- Stationary (speed < 0.5°/day): 45 points
- Slow (0.5° - 1.0°/day): 30 points
- Moderate (1.0° - 1.5°/day): 15 points
- Very fast (> 1.5°/day): 0 points

### 5. Naisargika Bala (Natural Strength)

Inherent strength of each planet (fixed values):

| Planet | Virupas |
|--------|---------|
| Sun | 60.0 |
| Moon | 51.43 |
| Jupiter | 34.29 |
| Venus | 42.86 |
| Mercury | 25.71 |
| Mars | 17.14 |
| Saturn | 8.57 |
| Rahu/Ketu | 0.0 |

### 6. Drik Bala (Aspectual Strength)

Measures strength from aspects received from other planets.

**Calculation:**
- Benefic aspects (Jupiter, Venus, Mercury): +5 points each
- Malefic aspects (Sun, Mars, Saturn): -5 points each
- Baseline: 30 points

## Strength Ratings

| Total Shadbala | Rating | Chart Impact |
|---|---|---|
| 360+ | Very Strong | Major influence, strong results |
| 300-359 | Strong | Significant positive influence |
| 200-299 | Moderate | Average strength |
| 100-199 | Weak | Limited influence |
| <100 | Very Weak | Minimal strength |

## Ashtakavarga (Eight-fold Classification)

Ashtakavarga measures a planet's strength in each of the 12 zodiac signs.

### Concept

Each of the 7 planets contributes "bindus" (points) to each sign based on:
1. The planet's position relative to Lagna (Ascendant)
2. The planet's position relative to 7 other planets
3. Total: 8 references

### Benefic Points Table

For each planet, specific signs receive bindus from each reference point:

**Example - Sun Ashtakavarga:**
```python
"sun": {
    "sun": [1, 2, 4, 7, 8, 9, 10, 11],    # Signs where Sun aspect is beneficial
    "moon": [3, 6, 10, 11],
    "mars": [1, 2, 4, 7, 8, 9, 10, 11],
    "mercury": [3, 5, 6, 9, 10, 11, 12],
    "jupiter": [5, 6, 9, 11],
    "venus": [6, 7, 12],
    "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
    "lagna": [3, 4, 6, 10, 11, 12]
}
```

### Calculation Method

1. For each sign (0-11):
   - Count how many references contribute a bindu
   - Sum contributions from all 8 references
   
2. Result: 0-8 bindus per sign per planet

3. Example output:
```
Moon Ashtakavarga: [4, 1, 3, 1, 4, 2, 1, 2, 5, 0, 3, 0]
Sign:              [Aries, Taurus, Gemini, Cancer, Leo, Virgo, 
                    Libra, Scorpio, Sagittarius, Capricorn, 
                    Aquarius, Pisces]
```

## Sarvashtakavarga (SAV)

Total Ashtakavarga summed across all 7 planets.

- **Range**: 0-56 bindus per sign (7 planets × 8 max points)
- **Interpretation**:
  - High SAV (40+): Sign is very strong, beneficial for activities
  - Medium SAV (20-40): Average strength
  - Low SAV (<20): Sign is weak, unfavorable for activities

### Usage Examples

**Finding Strong Transits:**
```python
sav = calculator.calculate_sarvashtakavarga(chart)
# Signs with SAV >= 40 are best for starting new ventures
strong_signs = [i for i, v in enumerate(sav) if v >= 40]
```

**Determining Sign Strength:**
```python
sign_strength = sav[sign_index]
if sign_strength >= 40:
    rating = "Excellent"
elif sign_strength >= 30:
    rating = "Good"
elif sign_strength >= 20:
    rating = "Fair"
else:
    rating = "Poor"
```

## Planet Dignity

Classification of a planet's status in a sign.

### Dignity Types

1. **Exalted** (Uchcha)
   - Planet at peak strength
   - Example: Sun in Aries (exaltation 10°)
   
2. **Own Sign** (Swarucha)
   - Planet in its own ruled sign
   - Example: Sun in Leo
   
3. **Friendly Sign**
   - Planet in sign of a friendly planet
   - Moderate strength
   
4. **Neutral Sign**
   - Neither beneficial nor harmful
   - Average strength
   
5. **Enemy Sign**
   - Planet in sign of enemy planet
   - Reduced strength
   
6. **Debilitated** (Neecha)
   - Planet at lowest strength (opposite of exaltation)
   - Example: Sun in Libra

### Example Classifications

```python
# Exaltation Examples
Sun in Aries (10°) → exalted
Moon in Taurus (3°) → exalted
Mars in Capricorn (28°) → exalted

# Own Sign Examples
Moon in Cancer → own
Mercury in Gemini → own
Venus in Taurus → own

# Debilitation Examples
Sun in Libra (10°) → debilitated
Moon in Scorpio (3°) → debilitated
Mars in Cancer (28°) → debilitated
```

## API Reference

### Main Methods

#### `calculate_shadbala(planet: Planet, chart: BirthChart) -> Dict`

Calculate complete Shadbala for a planet.

**Returns:**
```python
{
    "planet": "sun",
    "total": 315.0,
    "components": {
        "sthana_bala": 115.0,
        "dig_bala": 60.0,
        "kala_bala": 30.0,
        "chesta_bala": 15.0,
        "naisargika_bala": 60.0,
        "drik_bala": 35.0
    },
    "is_strong": True,
    "strength_rating": "strong"
}
```

#### `calculate_ashtakavarga(planet: Planet, chart: BirthChart) -> List[int]`

Calculate Ashtakavarga for a planet.

**Returns:** List of 12 integers (bindus per sign)

#### `calculate_sarvashtakavarga(chart: BirthChart) -> List[int]`

Calculate total Ashtakavarga for all signs.

**Returns:** List of 12 integers (total bindus per sign)

#### `get_planet_dignity(planet: Planet, sign: Rashi) -> str`

Get dignity classification of planet in sign.

**Returns:** One of: "exalted", "own", "friendly", "neutral", "enemy", "debilitated"

#### `analyze_strength_profile(chart: BirthChart) -> Dict`

Comprehensive strength analysis of the chart.

**Returns:**
```python
{
    "all_strengths": {...},
    "strongest_planet": "sun",
    "strongest_value": 315.0,
    "weakest_planet": "rahu",
    "weakest_value": 182.5,
    "very_strong_count": 2,
    "strong_count": 3,
    "weak_count": 4,
    "sarvashtakavarga": [...],
    "average_sav": 23.17,
    "chart_strength_level": "moderate"
}
```

## Example Usage

```python
from packages.self.src.strength import StrengthCalculator
from packages.core.src.constants import Planet, Rashi

# Initialize calculator
calculator = StrengthCalculator()

# Calculate Shadbala for Sun
sun_strength = calculator.calculate_shadbala(Planet.SUN, chart)
print(f"Sun Strength: {sun_strength['total']} virupas")
print(f"Rating: {sun_strength['strength_rating']}")

# Get planet dignity
dignity = calculator.get_planet_dignity(Planet.SATURN, Rashi.LIBRA)
print(f"Saturn in Libra: {dignity}")  # Output: "exalted"

# Analyze entire chart
profile = calculator.analyze_strength_profile(chart)
print(f"Strongest planet: {profile['strongest_planet']}")
print(f"Chart strength: {profile['chart_strength_level']}")

# Find strong signs for transits
sav = calculator.calculate_sarvashtakavarga(chart)
for i, bindus in enumerate(sav):
    if bindus >= 40:
        print(f"Sign {i}: Strong ({bindus} bindus)")
```

## References

- **BPHS** (Brihat Parasara Hora Sastra) - Chapters 22-23
- **Phaladeepa** - Commentaries on planetary strengths
- **Jyotish Classics** - Traditional strength measurement systems

## Implementation Notes

1. **Simplified Calculations**: Current implementation uses simplified formulas for some components (Tribhaga Bala, Varsha/Masa/Dina/Hora Bala) that can be expanded with full ephemeris data

2. **Rahu/Ketu**: These nodes have no Shadbala but can be included in Ashtakavarga calculations

3. **Divisional Charts**: Full Saptavargaja Bala requires divisional chart calculations (can be integrated with divisional module)

4. **Aspect Calculation**: Drik Bala simplified; full implementation requires precise aspect calculations

5. **Day/Night Determination**: Currently uses birth hour as proxy; full implementation uses sunrise/sunset times

## Future Enhancements

- Integration with divisional chart module for Saptavargaja Bala
- Precise aspect calculations for Drik Bala
- Exact Varsha/Masa/Dina/Hora Bala calculations
- Planetary war strength (Yuddha Bala)
- Custom strength thresholds per use case
- Strength trend analysis over time
